from utils.sleep import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

two_fa_sessions = {}

# TODO:
# headless
# method abstraction
def login(driver, tempdir ,username, password):
    wait = WebDriverWait(driver, 5)
    try:
        driver.find_elements(By.TAG_NAME, "iframe")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "lmsIframe")))

        username_field = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="loginIdInput"]'))
        )
        human_type(username, username_field)
        very_short_sleep()

        pw_field = driver.find_element(By.XPATH, '//*[@id="passwordInput"]')
        human_type(password, pw_field)
        very_short_sleep()

        login_button = driver.find_element(By.XPATH, '//*[@id="btnLogin"]')
        login_button.click()
        
        # Switch back to default content after login
        driver.switch_to.default_content()
        short_sleep()

    except Exception as e:
        print(f"An error occurred logging in:\n\n{e}")
        # Make sure we're back to default content even if there's an error
        try:
            driver.switch_to.default_content()
        except:
            pass

    # 2FA Handling
    try:
        # Send as mobile notification
        mobile_auth = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'mobile_approve'))
        )

        mobile_auth.click()

        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        two_fa_sessions[session_id] = {
            'driver': driver,
            'temp_dir': tempdir,  # Store temp_dir for cleanup, delete later
            'username': username,
            'password': password,
            'method': 'app',
            'action': None  # Set by buy/sell functions
        }
        return {'status': '2FA_required', 'method': 'app', 'session_id': session_id}
    except:
        try: 
            # Send as text
            text_auth = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="otp_sms"]'))
            )

            text_auth.click()

            # Generate a unique session ID
            session_id = str(uuid.uuid4())

            two_fa_sessions[session_id] = {
                'driver': driver,
                'temp_dir': tempdir,
                'username': username,
                'password': password,
                'method': 'text',
                'action': None
            }

            return {'status': '2FA_required', 'method': 'text', 'session_id': session_id}
        except Exception as e:
            try:
                # Wait for document loading to be complete
                wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

                wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="securityCode"]'))
                )

                # Generate a unique session ID
                session_id = str(uuid.uuid4())
                two_fa_sessions[session_id] = {
                    'driver': driver,
                    'temp_dir': tempdir,  
                    'username': username,
                    'password': password,
                    'method': 'text',
                    'action': None 
                }
                return {'status': '2FA_required', 'method': 'text', 'session_id': session_id}
            except:
                print("2FA not required. Login successful.")
                return {'status': 'success'}

def buy(tickers, dir, prof, trade_share_count, username, password, two_fa_code=None):
    driver, temp_dir = start_regular_driver(dir, prof)

    try:
        driver.get("https://client.schwab.com/app/trade/tom/trade")
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
    long_sleep()
    # Redirect to trade page
    driver.get("https://client.schwab.com/app/trade/tom/trade")
    short_sleep()

    # Get accounts
    try:
        account_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="basic-example-small"]'))
        )
        account_dropdown.click()

        ul_element = driver.find_element(By.XPATH, '//*[@id="basic-example-small-list"]/ul')
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
        li_count = len(li_elements)
    except:
        logger.error("Error getting account dropdown")

    for num in range(li_count):
        if num != 0:
            account_dropdown = driver.find_element(By.XPATH, '//*[@id="basic-example-small"]')
            account_dropdown.click()
        very_short_sleep()

        logger.info(f"Clicking on account {num}")

        # Click on account
        try:
            account_select = driver.find_element(By.ID, f'basic-example-small-header-0-account-{num}')
            account_select.click()
            
            # Wait for page to fully load after account switch
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            short_sleep() 
            
        except:
            logger.error(f"Could not select account {num}")

        very_short_sleep()
        for ticker in tickers:
            # Search for ticker
            try:
                ticker_search = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, '_txtSymbol'))
                )
                human_type(ticker, ticker_search)
                short_sleep()

                ticker_search.send_keys(Keys.ENTER)
                short_sleep()
            except Exception as e:
                logger.error(f"Error searching for ticker: {str(e)}")
                raise

            # Set action to Buy
            try:
                action_button = driver.find_element(By.ID, '_action')
                action_button.click()
                very_short_sleep()

                select = Select(action_button)
                select.select_by_visible_text("Buy")
                very_short_sleep()
            except Exception as e:
                logger.error(f"Error setting Buy action: {str(e)}")
                raise

            # Set quantity if needed
            try:
                if (trade_share_count != 1):
                    qty_field = driver.find_element(By.ID, 'ordernumber01inputqty-stepper-input')
                    qty_field.clear()
                    human_type(str(trade_share_count), qty_field)
            except Exception as e:
                logger.error(f"Error setting quantity: {str(e)}")
                raise

            # Check if limit is higher than current price
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'mctorderdetail-checkbox')]"))
                )
                higher_than_ask_checkbox = driver.find_element(By.ID, 'mctorderdetailfbb8f5e5CHECKBOX_0')
                higher_than_ask_checkbox.click()
                print("Limit price is higher than actual, continuing with purchase...\n\n")
            except Exception as e:
                pass

            # Review order
            try:
                review_order_button = driver.find_element(By.XPATH, "//button[normalize-space()='Review Order']")
                review_order_button.click()
                short_sleep()
            except Exception as e:
                logger.error(f"Error clicking review order: {str(e)}")
                raise

            very_short_sleep()

            # Check for and handle additional order message checkbox
            try:
                order_message_checkbox = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'mctorderdetail') and contains(@id, 'CHECKBOX')]"))
                )
                order_message_checkbox.click()
                very_short_sleep()
            except Exception as e:
                # Checkbox may not always be present, so just log and continue
                logger.info("Order message checkbox not found or not clickable")
                pass

            very_short_sleep()

            # Place buy order
            try:
                submit_buy = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="mtt-place-button"]'))
                )
                submit_buy.click()
            except Exception as e:
                logger.error(f"Error clicking submit buy: {str(e)}")

            short_sleep()

            print(f"Buy order for '{ticker}' submitted!")

            # redirect
            driver.get("https://client.schwab.com/app/trade/tom/trade")
            short_sleep()

def sell(tickers, dir, prof, trade_share_count, username, password, two_fa_code=None):
    driver, temp_dir = start_regular_driver(dir, prof)

    try:
        driver.get("https://client.schwab.com/Areas/Access/Login")
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
    # Redirect to trade page
    driver.get("https://client.schwab.com/app/trade/tom/trade")
    short_sleep()
    # Get accounts
    try:
        account_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="basic-example-small"]'))
        )
        account_dropdown.click()

        ul_element = driver.find_element(By.XPATH, '//*[@id="basic-example-small-list"]/ul')
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
        li_count = len(li_elements)

    except:
        print("Error getting account dropdown")

    for num in range(li_count):
        if num != 0:
            account_dropdown = driver.find_element(By.XPATH, '//*[@id="basic-example-small"]')
            account_dropdown.click()
        very_short_sleep()

        # Click on account
        account_select = driver.find_element(By.ID, f'basic-example-small-header-0-account-{num}')
        account_select.click()
        very_short_sleep()
        for ticker in tickers:
            # Ticker search
            ticker_search = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="_txtSymbol"]'))
            )
            human_type(ticker, ticker_search)
            very_short_sleep()
            ticker_search.send_keys(Keys.ENTER)
            short_sleep()

            action_button = driver.find_element(By.XPATH, '//*[@id="_action"]')
            action_button.click()
            very_short_sleep()

            select = Select(action_button)
            select.select_by_visible_text("Sell")
            very_short_sleep()

            if (trade_share_count != 1):
                qty_field = driver.find_element(By.XPATH, '//*[@id="ordernumber01inputqty-stepper-input"]')
                qty_field.clear()
                human_type(str(trade_share_count), qty_field)

            # Review order
            try:
                review_order_button = driver.find_element(By.XPATH, "//button[normalize-space()='Review Order']")
                review_order_button.click()
                short_sleep()
            except Exception as e:
                logger.error(f"Error clicking review order: {str(e)}")
                raise

            very_short_sleep()

            # Check for and handle additional order message checkbox
            try:
                order_message_checkbox = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'mctorderdetail') and contains(@id, 'CHECKBOX')]"))
                )
                order_message_checkbox.click()
                very_short_sleep()
            except Exception as e:
                # Checkbox may not always be present, so just log and continue
                logger.info("Order message checkbox not found or not clickable")
                pass

            # Place sell order
            try:
                submit_sell = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="mtt-place-button"]'))
                )
                submit_sell.click()
            except Exception as e:
                logger.error(f"Error clicking submit sell: {str(e)}")

            short_sleep()

            print(f"Sell order for '{ticker}' submitted!")

            # redirect
            driver.get("https://client.schwab.com/app/trade/tom/trade")
            short_sleep()

    
def complete_2fa_and_trade(session_id, two_fa_code=None):
    """
    Completes the 2FA process based on the session ID and performs the trade.
    """
    logger.info(f"Completing 2FA for session {session_id}.")

    if session_id not in two_fa_sessions:
        logger.error("Invalid session ID.")
        return {'status': 'error', 'message': 'Invalid session ID.'}

    session_info = two_fa_sessions[session_id]
    driver = session_info['driver']
    temp_dir = session_info['temp_dir']
    method = session_info['method']
    action = session_info['action']
    tickers = session_info.get('tickers')
    trade_share_count = session_info.get('trade_share_count')
    username = session_info.get('username')
    password = session_info.get('password')

    try:
        wait = WebDriverWait(driver, 24)

        if method == 'text':
            if not two_fa_code:
                logger.error("2FA code is missing for text-based 2FA.")
                return {'status': 'error', 'message': '2FA code is required for text-based 2FA.'}

            # Enter the 2FA code received via text
            code_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="securityCode"]'))
            )
            human_type(two_fa_code, code_input)

            submit_code = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="continueButton"]'))
            )
            submit_code.click()

            logger.info("Submitted 2FA code via text.")

        elif method == 'app':
            # Wait for user to approve app notification
            logger.info("Awaiting site redirect")
            short_sleep()
            
            btnContinue = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'btnContinue'))
            )
            btnContinue.click()

            success_urls = {
                'https://client.schwab.com/app/trade/tom/trade',
                'https://client.schwab.com/clientapps/accounts/summary/'
            }

            # Wait for a certain time and check if login is successful
            try:
                WebDriverWait(driver, 30).until(
                lambda d: d.current_url in success_urls
            )
            except TimeoutException:
                logger.error("App Notification 2FA not approved within the expected time.")
                return {'status': 'error', 'message': 'App Notification 2FA not approved.'}

        else:
            logger.error("Invalid 2FA method specified.")
            return {'status': 'error', 'message': 'Invalid 2FA method specified.'}

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

    except Exception as e:
        logger.error(f"Error during 2FA completion and trade: {str(e)}")
        driver.quit()
        shutil.rmtree(temp_dir, ignore_errors=True)
        del two_fa_sessions[session_id]
        return {'status': 'error', 'message': 'An error occurred during 2FA completion and trade.', 'error': str(e)}
