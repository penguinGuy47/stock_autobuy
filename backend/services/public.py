from utils.sleep import *

# TODO:
# add login
# add buy
# add multi buy function

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

two_fa_sessions = {}

def login(driver, tempdir, username, password):
    wait = WebDriverWait(driver, 10)
    try:
        username_field = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="email"]'))
        )
        human_type(username, username_field)

        very_short_sleep()
        pw_field = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="password"]'))
        )
        human_type(password, pw_field)

        very_short_sleep()
        login_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div[2]/main/div/div/form/button[2]')
        login_button.click()

        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        two_fa_sessions[session_id] = {
            'driver': driver,
            'temp_dir': tempdir,  # Store temp_dir for cleanup
            'username': username,
            'password': password,
            'method': 'text',
            'action': None  # To be set by buy/sell functions
        }

        return {'status': '2FA_required', 'method': 'text', 'session_id': session_id}
    except:
        print("2FA not required. Login successful.")
        return {'status': 'success'}

    
def complete_2fa_and_trade(session_id, two_fa_code=None):
    logger.info(f"Completing 2FA for session {session_id}.")

    if not two_fa_code:
        logger.error("2FA code is missing for text-based 2FA.")
        return {'status': 'error', 'message': '2FA code is required for text-based 2FA.'}

    if session_id not in two_fa_sessions:
        logger.error("Invalid session ID.")
        return {'status': 'error', 'message': 'Invalid session ID.'}

    session_info = two_fa_sessions[session_id]
    driver = session_info['driver']
    temp_dir = session_info['temp_dir']
    # method = session_info['method'] # Only has 'text' method 
    action = session_info['action']
    tickers = session_info.get('tickers')
    # ticker = session_info.get('ticker')
    trade_share_count = session_info.get('trade_share_count')
    username = session_info.get('username')
    password = session_info.get('password')

    try:
        code_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="verificationCode"]'))
        )
        human_type(two_fa_code, code_input)
        very_short_sleep()

        next_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div[2]/main/div/div/form/div[2]/div/button')
        next_button.click()
    except:
        print("Error completing 2FA")
        return {'status': 'error', 'message': '2FA was incorrect.'}
    
    short_sleep()
    # After 2FA, proceed with the trade
    if action == 'buy':
        trade_response = buy_after_login(driver, tickers, trade_share_count)
    elif action == 'sell':
        trade_response = sell_after_login(driver, tickers, trade_share_count)
    else:
        logger.error("Invalid trade action specified.")
        return {'status': 'error', 'message': 'Invalid trade action specified.'}

    # Clean up
    driver.quit()
    shutil.rmtree(temp_dir, ignore_errors=True)
    del two_fa_sessions[session_id]

    return trade_response
    


# redirect site: https://public.com/portfolio


def buy(tickers, dir, prof, trade_share_count, username, password, two_fa_code=None):
    driver, temp_dir = start_regular_driver(dir, prof)

    try:
        driver.get("https://public.com/login")
        login_response = login(driver, temp_dir, username, password)
        
        if login_response['status'] == '2FA_required':
            logger.info(f"2FA required via {login_response['method']}.")
            # Store action details in the session
            session_id = login_response.get('session_id')
            two_fa_sessions[session_id]['action'] = 'buy'
            two_fa_sessions[session_id]['tickers'] = tickers
            two_fa_sessions[session_id]['trade_share_count'] = trade_share_count
            os.system('echo \a')
            return {
                'status': '2FA_required',
                'method': login_response['method'],
                'session_id': session_id,
                'message': '2FA is required'
            }
        elif login_response['status'] == 'success':
            # Proceed with buying
            trade_response = buy_after_login(driver, tickers, trade_share_count)
            driver.quit()
            shutil.rmtree(temp_dir, ignore_errors=True)
            return trade_response

        else:
            # Handle other statuses
            driver.quit()
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {
                'status': 'failure',
                'message': login_response.get('message', 'Login failed.')
            }
    except Exception as e:
        logger.error(f"Error during buy operation: {str(e)}")
        driver.quit()
        shutil.rmtree(temp_dir, ignore_errors=True)
        return {
            'status': 'failure',
            'message': f'Failed to buy {tickers}.',
            'error': str(e)
        }
    

def buy_after_login(driver, tickers, trade_share_count):
    try:
        while (driver.current_url != "https://public.com/portfolio"):
            time.sleep(1)
        logger.info("Logged onto Public!")

        for ticker in tickers:
            ticker_search(driver, ticker)
            setup_trade(driver, trade_share_count)

            # Add to queue
            add_to_q = driver.find_element(By.XPATH, '//*[@id="maincontent"]/div/div[2]/div[1]/div/div[3]/button[2]')
            add_to_q.click()

        very_short_sleep()
        execute_trades(driver)
    except:
        logger.error("Error after log in")

    driver.quit()    

# DO HERE
def sell(tickers, dir, prof, trade_share_count, username, password, two_fa_code=None):
    driver, temp_dir = start_headless_driver(dir, prof)

    try:
        driver.get("https://public.com/login")
        login_response = login(driver, temp_dir, username, password)
        
        if login_response['status'] == '2FA_required':
            logger.info(f"2FA required via {login_response['method']}.")
            # Store action details in the session
            session_id = login_response.get('session_id')
            two_fa_sessions[session_id]['action'] = 'sell'
            two_fa_sessions[session_id]['tickers'] = tickers
            two_fa_sessions[session_id]['trade_share_count'] = trade_share_count
            os.system('echo \a')
            return {
                'status': '2FA_required',
                'method': login_response['method'],
                'session_id': session_id,
                'message': '2FA is required'
            }
        elif login_response['status'] == 'success':
            # Proceed with selling
            trade_response = sell_after_login(driver, tickers, trade_share_count)
            driver.quit()
            shutil.rmtree(temp_dir, ignore_errors=True)
            return trade_response

        else:
            # Handle other statuses
            driver.quit()
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {
                'status': 'failure',
                'message': login_response.get('message', 'Login failed.')
            }
    except Exception as e:
        logger.error(f"Error during sell operation: {str(e)}")
        driver.quit()
        shutil.rmtree(temp_dir, ignore_errors=True)
        return {
            'status': 'failure',
            'message': f'Failed to sell {tickers}.',
            'error': str(e)
        }

def sell_after_login(driver, tickers, trade_share_count):
    try:
        while (driver.current_url != "https://public.com/portfolio"):
            time.sleep(1)
        logger.info("Logged onto Public!")

        for ticker in tickers:
            ticker_search(driver, ticker)
            
            # Click on sell
            try:
                sell_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="maincontent"]/div/div[2]/div[1]/div/div[2]/div/label[2]'))
                )
                sell_tab.click()
            except:
                pass

            setup_trade(driver, trade_share_count)

            # Add to queue
            add_to_q = driver.find_element(By.XPATH, '//*[@id="maincontent"]/div/div[2]/div[1]/div/div[3]/button[2]')
            add_to_q.click()

        very_short_sleep()
        execute_trades(driver)
    except:
        logger.error("Error after log in")

    driver.quit()    

def ticker_search(driver, ticker):
    wait = WebDriverWait(driver, 10)
    try:
        search_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[1]/header/div/div/div[1]/div/div/input'))
        )
        human_type(ticker, search_input)
        short_sleep()
        search_input.send_keys(Keys.DOWN)
        very_short_sleep()
        search_input.send_keys(Keys.ENTER)

    except:
        logger.error("Error during ticker search")

def setup_trade(driver, qty):
    wait = WebDriverWait(driver, 10)
    try:
        # buy_type = wait.until(
        #     EC.element_to_be_clickable((By.XPATH, '//*[@id="radix-:r5u:"]'))
        # )
        # buy_type.click()
        # very_short_sleep()
        # logger.info("Switching to sharse...")

        # in_shares = driver.find_element(By.XPATH, '//*[@id="radix-:r5v:"]/div[2]')
        # in_shares.click()
        logger.info("Inputting amount...")
        very_short_sleep()
        share_amount = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="quantity"]'))
        )
        
        human_type(str(qty), share_amount)
        short_sleep()
    except:
        logger.error("Error setting up trade")

def execute_trades(driver):
    wait = WebDriverWait(driver, 10)
    try:
        go_to_q = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="side-nav"]/ul/li[12]/a'))
        )
        go_to_q.click()

        select_all_drafts = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="page-content"]/div/div/table/thead/tr/th[10]'))
        )
        select_all_drafts.click()
        very_short_sleep()

        submit_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="page-content"]/div/div/div[2]/div[2]/div[2]/button'))
        )
        submit_button.click()
        short_sleep()
        
        confirm_submission = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="page-content"]/div/div/div[2]/div[2]/div[2]/button'))
        )
        confirm_submission.click()
        rand_sleep()

        logger.info("ORDER SUBMITTED")
    except Exception as e:
        logger.error("Error during order submission: " + e)