from utils.sleep import *
from selenium.webdriver.common.action_chains import ActionChains

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

two_fa_sessions = {}

# TODO:
def login(driver, tempdir, username, password):
    very_short_sleep()
    try:
        # Login logic
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="userid"]'))
        )
        human_type(username, username_field)
        short_sleep()

        pw_field = driver.find_element(By.XPATH, '//*[@id="password"]')
        human_type(password, pw_field)
        very_short_sleep()

        sign_on_button = driver.find_element(By.XPATH, '//*[@id="btnSignon"]')
        sign_on_button.click()

        send_mobile_2fa = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app-modal-root"]/div[4]/div/div/div/div/div/div/div/div[2]/div/div[2]/div[2]/div/ul/li[1]/button'))
        )
        send_mobile_2fa.click()

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

def buy(tickers, dir, prof, trade_share_count, username, password, two_fa_code=None):
    driver, temp_dir = start_regular_driver(dir, prof)

    try:
        driver.get("https://www.wellsfargo.com/")
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

    # enterTradeTicket(driver) 
    navigate_to_trade(driver)
    initiate_account_selection(driver)

    # In the trade ticket
    try:
        select_account_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="dropdown2"]'))
        )
        select_account_dropdown.click()
        very_short_sleep()

        # Obtain number of accounts
        li_elements = driver.find_elements(By.CSS_SELECTOR, '#dropdownlist2 li')

        for i in range(1, len(li_elements) + 1):
            select_account_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="dropdown2"]'))
            )

            if (i != 1):
                select_account_dropdown.click()

            account_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@id="dropdownlist2"]/li[{i}]'))
            )
            account_select.click()

            try:
                switch_ticket_conf = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-continue"]'))
                )
                switch_ticket_conf.click()
            except:
                pass


            try: 

                for ticker in tickers:
                    short_sleep()
                    order_url = driver.current_url
                    try:
                        select_action = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, 'BuySellBtn'))
                        )
                        select_action.click()

                        conduct_trade(driver, ticker, trade_share_count, "buy")
                        driver.get(order_url)
                    except:
                        logger.info("Error conducting buy action")
            except:
                logger.info("Error configuring trade")
    except:
        logger.info("Error occurred in trade ticket")

    logger.info("No more accounts to process.")
    driver.quit()
    # handle_popup(driver)
    
def conduct_trade(driver, ticker, trade_share_count, trade_type):
    wait = WebDriverWait(driver, 10)
    try:
        if trade_type == "buy":
            buy_action = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="eqentryfrm"]/div/div[1]/div[1]/div[1]/div[2]/ul/li[1]/a'))
            )
            buy_action.click()
        else:
            select_action = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="eqentryfrm"]/div/div[1]/div[1]/div[1]/div[2]/ul/li[2]/a'))
            )
            select_action.click()

        ticker_input = wait.until(
            EC.element_to_be_clickable((By.ID, 'Symbol'))
        )
        human_type(ticker, ticker_input)
        ticker_input.send_keys(Keys.ENTER)

        share_qty = wait.until(
            EC.element_to_be_clickable((By.ID, 'OrderQuantity'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", share_qty)
        short_sleep()
        human_type(str(trade_share_count), share_qty)

        very_short_sleep()

        order_type = wait.until(
            EC.element_to_be_clickable((By.ID, "OrderTypeBtnText"))
        )
        order_type.click()

        limit_order = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ordertyperow"]/div[2]/div[2]/ul/li[1]/a'))
        )
        limit_order.click()
        very_short_sleep()

        if trade_type == "buy":
            # ASK
            current_price = driver.find_element(By.XPATH, '//*[@id="prevdata"]/div[3]/div[1]/div[2]/div[1]').text
            price_as_float = float(current_price) + 0.1
        else:
            # BID
            current_price = driver.find_element(By.XPATH, '//*[@id="prevdata"]/div[3]/div[2]/div[2]/div[1]').text
            price_as_float = float(current_price) - 0.1

        current_price = f"{price_as_float:.2f}"  # Format back to string with 2 decimal places
        limit_input = wait.until(
            EC.element_to_be_clickable((By.ID, 'Price'))
        )
        human_type(current_price, limit_input)
        very_short_sleep()

        timing_select = wait.until(
            EC.element_to_be_clickable((By.ID, 'TIFBtnText'))
        )
        timing_select.click()
        very_short_sleep()

        day_select = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-val='Day']"))
        )

        day_select.click()
        very_short_sleep()

        preview_button = wait.until(
            EC.element_to_be_clickable((By.ID, 'actionbtnContinue'))
        )
        preview_button.click()
        very_short_sleep()

        try:
            submit_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="actionbtnbar"]/button[2]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            short_sleep()
            submit_button.click()
        except:
            logger.info("Error submitting order")
            driver.quit()
    except:
        logger.info("Error conducting trade...")


def navigate_to_trade(driver):

    try:
        brokerage_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="BROKERAGE_LINK7P"]'))
        )

        brokerage_button.click()
    except:
        logger.info("Error clicking on brokerage tab")

def initiate_account_selection(driver):
    try:
        # Select Account
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        portfolio_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/nav[2]/div/ul/li[4]'))
        )

        portfolio_button.click()

        very_short_sleep()
        trademenu_button =  WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'gotrading'))
        )
        trademenu_button.click()
    except:
        logger.info("Error clicking on trade menu button")

def handle_popup(driver):
    try:
        # Continue if there is a popup
        popup_click_yes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-continue"]'))
        )
        popup_click_yes.click()
    except:
        logger.error("No popup, continuing...")


def sell(tickers, dir, prof, trade_share_count, username, password, two_fa_code=None):
    driver, temp_dir = start_regular_driver(dir, prof)

    try:
        driver.get("https://www.wellsfargo.com/")
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
    except:
        print("Error logging in")

def sell_after_login(driver, tickers, trade_share_count):

    navigate_to_trade(driver)
    initiate_account_selection(driver)

    # In the trade ticket
    try:
        select_account_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="dropdown2"]'))
        )
        select_account_dropdown.click()
        very_short_sleep()

        # Obtain number of accounts
        li_elements = driver.find_elements(By.CSS_SELECTOR, '#dropdownlist2 li')

        for i in range(1, len(li_elements) + 1):
            select_account_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="dropdown2"]'))
            )

            if (i != 1):
                select_account_dropdown.click()

            account_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//*[@id="dropdownlist2"]/li[{i}]'))
            )
            account_select.click()

            try:
                switch_ticket_conf = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-continue"]'))
                )
                switch_ticket_conf.click()
            except:
                pass


            try: 
                for ticker in tickers:
                    short_sleep()
                    order_url = driver.current_url
                    try:
                        select_action = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="BuySellBtn"]'))
                        )
                        select_action.click()

                        conduct_trade(driver, ticker, trade_share_count, "sell")
                        driver.get(order_url)
                    except:
                        logger.info("Error conducting sell action")
            except:
                logger.info("Error configuring trade")
    except:
        logger.info("Error occurred in trade ticket")

    logger.info("No more accounts to process.")
    driver.quit()
    # handle_popup(driver)

def complete_2fa_and_trade(session_id, two_fa_code=None):
    logger.info(f"Completing 2FA for Wells Fargo session {session_id}.")

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
    # username = session_info.get('username')
    # password = session_info.get('password')

    try:
        verify_code = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="otp"]'))
        )
        human_type(two_fa_code, verify_code)
        very_short_sleep()

        continue_button = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/div/div/div/div/div/div/div[2]/div/form/div[3]/footer/div/button[1]')
        continue_button.click()
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