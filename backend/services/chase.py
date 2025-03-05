from utils.sleep import *
import time

# TODO:
# Add additonal 2FA handling
# Fix selling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

two_fa_sessions = {}

def login(driver, tempdir, username, password):
    short_sleep()
    
    wait = WebDriverWait(driver, 25)
    
    # Enter login information
    try:
        driver.find_elements(By.TAG_NAME, "iframe")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "logonbox")))
        very_short_sleep()

        # Get and enter username
        username_field = wait.until(lambda d: d.execute_script(
            'return document.querySelector("#userId").shadowRoot.querySelector("#userId-input")'))
        driver.execute_script('arguments[0].click();', username_field)
        very_short_sleep()
        human_type(username, username_field)
        short_sleep()

        # Get and enter password
        pw_field = wait.until(lambda d: d.execute_script(
            'return document.querySelector("#password").shadowRoot.querySelector("#password-input")'))
        driver.execute_script('arguments[0].click();', pw_field)
        human_type(password, pw_field)

        # Click remember me checkbox
        driver.execute_script(
            "var checkbox = document.querySelector('mds-checkbox#rememberMe'); checkbox.setAttribute('state', 'true'); return checkbox;"
        )
        short_sleep()

        # Click sign in button
        signin = driver.execute_script(
            'return document.querySelector("#signin-button").shadowRoot.querySelector("button")')
        short_sleep()
        driver.execute_script('arguments[0].click();', signin)

    except Exception as e:
        logger.info(f"An error occurred during login: {e}")
        driver.quit()

    # Handle 2FA as text
    try:
        send_text_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="header-simplerAuth-dropdownoptions-styledselect"]'))
        )
        send_text_btn.click()

        phone_num = driver.find_element(By.XPATH, '//*[@id="container-1-simplerAuth-dropdownoptions-styledselect"]')
        phone_num.click()

        submit_btn = driver.find_element(By.XPATH, '//*[@id="requestIdentificationCode"]')
        submit_btn.click()

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
        logger.info("Error sending 2FA as text, attempting alternative method")
        try:
            # Alternative 2FA handling in app
            send_to_app_btn = driver.execute_script(
                'return document.querySelector("#optionsList").shadowRoot.querySelector("#mds-list__list-items > li > div > a")'
            )
            driver.execute_script('arguments[0].click()', send_to_app_btn)

            very_short_sleep()

            nxt_btn = driver.execute_script(
                'return document.querySelector("#next-content").shadowRoot.querySelector("button")'
            )
            driver.execute_script('arguments[0].click()', nxt_btn)

            session_id = str(uuid.uuid4())
            two_fa_sessions[session_id] = {
                'driver': driver,
                'temp_dir': tempdir,
                'username': username,
                'password': password,
                'method': 'app',
                'action': None  # To be set by buy/sell functions
            }

            # Indicate that App Notification-Based 2FA is required
            return {'status': '2FA_required', 'method': 'app', 'session_id': session_id}
        except Exception as e:
            logger.info(f"An error occurred during alternative 2FA handling: {e}")
            driver.quit()

def wait_for_shadow_element(driver, shadow_host_css, shadow_element_selector):
    very_short_sleep()
    try:
        WebDriverWait(driver, 10).until(lambda d: d.execute_script(
            f'''
            let shadowHost = document.querySelector("{shadow_host_css}");
            if (!shadowHost) return false;
            let shadowRoot = shadowHost.shadowRoot;
            if (!shadowRoot) return false;
            let element = shadowRoot.querySelector("{shadow_element_selector}");
            return element !== null;
            '''
        ))
        return driver.execute_script(
            f'''
            return document.querySelector("{shadow_host_css}").shadowRoot.querySelector("{shadow_element_selector}");
            '''
        )
    except TimeoutException:
        return None

def select_account(driver, wait, index):
    try:
        script_info = f'''
            return document.querySelector("#investment-account-table").shadowRoot.querySelector("#row-header-row{index}-column0 > div > a")
        '''

        account_select = wait.until(lambda d: d.execute_script(script_info))
        driver.execute_script('arguments[0].click();', account_select)
        logger.info(f"Selected account {index + 1}")
        short_sleep()
        return driver.current_url
    
    except Exception as e:
        logger.info(f"Failed to select account {index + 1}: {e}")
        return None

def search_ticker(driver, wait, ticker):
    try:
        ticker_search = wait.until(lambda d: d.execute_script(
            'return document.querySelector("#quoteSearchLink").shadowRoot.querySelector("a")'))
        driver.execute_script('arguments[0].click();', ticker_search)
        short_sleep()

        ticker_input = wait.until(lambda d: d.execute_script(
            'return document.querySelector("#typeaheadSearchTextInput").shadowRoot.querySelector("#typeaheadSearchTextInput-input")'))
        driver.execute_script('arguments[0].click()', ticker_input)
        short_sleep()

        human_type(ticker, ticker_input)
        short_sleep()
        ticker_input.send_keys(Keys.ENTER)
        long_sleep()

        # Switch to the iframe
        driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame("quote-markit-thirdPartyIFrameFlyout")
        return True
    except Exception as e:
        logger.info(f"An error occurred while searching for ticker '{ticker}': {e}")
        return False

def handle_market_alert(driver, wait):
    try:
        close_button = WebDriverWait(driver, 4).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='close-add-market-alert-notification']"))
        )
        close_button.click()
        rand_sleep()
    except TimeoutException:
        logger.info("\n\nNo market alert notification found, continuing...\n\n")

def perform_trade(driver, wait, action, qty):
    """
    Args:
        action (str): 'buy' or 'sell'
        qty (str): Quantity of shares to trade
    """
    try:
        trade_button = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="quote-header-trade-button"]'))
        )
        trade_button.click()
        rand_sleep()
        driver.switch_to.default_content()
        logger.info("in perform trade")
        if action == 'buy':
            order_button_xpath = '//*[@id="orderAction-segmentedButtonInput-0"]'
        elif action == 'sell':
            order_button_xpath = '//*[@id="orderAction-segmentedButtonInput-1"]'
        else:
            logger.info("Invalid trade action specified.")
            return False

        trade_button_element = driver.find_element(By.XPATH, order_button_xpath)
        trade_button_element.click()
        short_sleep()

        # Dropdown order type
        order_type_dropdown = wait.until(lambda d: d.execute_script(
            'return document.querySelector("#orderTypeDropdown").shadowRoot.querySelector("#select-orderTypeDropdown")'))
        driver.execute_script('arguments[0].click();', order_type_dropdown)
        short_sleep()

        # Choose market order
        market_order = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="orderTypeDropdown"]/mds-select-option[1]'))
        )
        market_order.click()
        short_sleep()

        # Share quantity
        share_qty = wait.until(lambda d: d.execute_script(
            'return document.querySelector("#orderQuantity").shadowRoot.querySelector("#orderQuantity-input")'))
        driver.execute_script('arguments[0].click();', share_qty)
        short_sleep()
        share_qty.send_keys(qty)
        short_sleep()

        # Click preview
        preview_button = wait.until(lambda d: d.execute_script(
            'return document.querySelector("#previewButton").shadowRoot.querySelector("button")'))
        driver.execute_script('arguments[0].click();', preview_button)
        very_short_sleep()

        # Click place order
        # place_order_button = driver.execute_script(
        #     'return document.querySelector("#orderPreviewContent > div.order-preview-section.mds-pt-4 > div > mds-button").shadowRoot.querySelector("button")')
        # driver.execute_script('arguments[0].click();', place_order_button)
        short_sleep()

        logger.info(f"Order placed successfully for {action} operation!")
        return True

    except Exception as e:
        logger.info(f"An error occurred during {action} operation: {e}")
        return False

def navigate_to_dashboard(driver):
    try:
        driver.get('https://secure.chase.com/web/auth/dashboard#/dashboard/overview')
        short_sleep()
    except Exception as e:
        logger.info(f"Failed to navigate to dashboard: {e}")

def buy(tickers, dir, prof, trade_share_count, username, password, two_fa_code=None):
    """
    Initiates a buy operation for the specified tickers and quantity.
    """
    logger.info(f"Initiating buy operation for {trade_share_count} shares of {tickers} by user {username}")
    driver, temp_dir = start_regular_driver(dir, prof)
    try:
        driver.get("https://secure.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/index")
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
    wait = WebDriverWait(driver, 10)
    try:
        # ERROR HERE
        # num_of_rows = driver.execute_script('''
        #     let shadow_root = document.querySelector("mds-select").shadowRoot;
        #     let options = shadow_root.querySelectorAll("mds-select-option:not([group-cwm-investment]):not([data-testid='ADD_GROUP'])");
        #     return options.length;
        # ''')
        num_of_rows = driver.execute_script('''
            let tbody = document.querySelector("tbody");
            let rows = tbody.querySelectorAll("tr");
            return Array.from(rows).filter(row => row.offsetParent !== null).length;
        ''')

        # returns ONE extra account
        logger.info(f"Number of Accounts: {num_of_rows}")

        # fix the order for buy and sell operations, chase recently changed their site and the ticker search
        # is no longer in the place it was accessible before. 
        # manually execute buy/sell order to understand the new process and go from there
        for i in range(num_of_rows-1):
            short_sleep()
            
            if driver.current_url != 'https://secure.chase.com/web/auth/dashboard#/dashboard/overview':
                navigate_to_dashboard(driver)

            short_sleep()
            account_url = select_account(driver, wait, i)

            if not account_url:
                continue

            for ticker in tickers:
                logger.info("SEARCHING FOR TICKERS")
                if not search_ticker(driver, wait, ticker):
                    continue

                handle_market_alert(driver, wait)

                if perform_trade(driver, wait, 'buy', trade_share_count):
                    logger.info(f"Buy order placed successfully for '{ticker}' on Chase!")
                else:
                    logger.info(f"Failed to place buy order for '{ticker}'.")

                # Navigate back to account
                driver.get(account_url)
                short_sleep()

        logger.info("No more accounts to process.")  

        return {'status': 'success', 'message': 'All sell orders processed successfully.'}
    
    except Exception as e:
        logger.error(f"Failed to determine number of account rows: {e}")
        return {'status': 'error', 'message': f'Failed to determine number of accounts: {e}'}
    
    finally:
        driver.quit()


def sell(tickers, dir, prof, trade_share_count, username, password, two_fa_code=None):
    """
    Initiates a sell operation for the specified tickers and quantity.
    """
    logger.info(f"Initiating sell operation for {trade_share_count} shares of {tickers} by user {username}")
    driver, temp_dir = start_regular_driver(dir, prof)
    try:
        driver.get("https://secure.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/index")
        login_response = login(driver, temp_dir, username, password)

        if login_response['status'] == '2FA_required':
            logger.info(f"2FA required via {login_response['method']}.")
            # Store action details in the session
            session_id = login_response.get('session_id')
            two_fa_sessions[session_id]['action'] = 'sell'
            two_fa_sessions[session_id]['tickers'] = tickers
            two_fa_sessions[session_id]['trade_share_count'] = trade_share_count
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
        shutil.rmtree(temp_dir, ignore_errors=True)
        return {
            'status': 'failure',
            'message': f'Failed to sell {tickers}.',
            'error': str(e)
        }

def sell_after_login(driver, tickers, trade_share_count):
    wait = WebDriverWait(driver,  10)
    try:
        # Determine the number of account rows
        num_of_rows = driver.execute_script('''
            let shadow_root = document.querySelector("#account-table-INVESTMENT").shadowRoot;
            let tbody = shadow_root.querySelector("tbody");
            return tbody.querySelectorAll("tr").length;
        ''')
        for i in range(num_of_rows):

            if driver.current_url != 'https://secure.chase.com/web/auth/dashboard#/dashboard/overview':
                navigate_to_dashboard(driver)

            short_sleep()
            account_url = select_account(driver, wait, i)
            if not account_url:
                continue

            for ticker in tickers:
                if not search_ticker(driver, wait, ticker):
                    continue

                handle_market_alert(driver, wait)

                if perform_trade(driver, wait, 'sell', trade_share_count):
                    logger.info(f"Sell order placed successfully for '{ticker}' on Chase!")
                else:
                    logger.info(f"Failed to place sell order for '{ticker}'.")

                # Navigate back to account
                driver.get(account_url)
                short_sleep()

        logger.info("No more accounts to process.")
        return {'status': 'success', 'message': 'All sell orders processed successfully.'}
    
    except Exception as e:
        logger.error(f"Failed to determine number of account rows: {e}")
        return {'status': 'error', 'message': f'Failed to determine number of accounts: {e}'}
    
    finally:
        driver.quit()

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
        wait = WebDriverWait(driver, 18)

        # UPDATE THIS TEXT SECTION 
        if method == 'text':
            if not two_fa_code:
                logger.error("2FA code is missing for text-based 2FA.")
                return {'status': 'error', 'message': '2FA code is required for text-based 2FA.'}

            # Enter the 2FA code received via text
            code_input = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="dom-otp-code-input"]'))
            )
            human_type(two_fa_code, code_input)

            asking_again = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="dom-widget"]/div/div[2]/pvd-field-group/s-root/div/div/s-slot/s-assigned-wrapper/pvd-form/s-root/div/form/s-slot/s-assigned-wrapper/div[1]/pvd-field-group/s-root/div/div/s-slot/s-assigned-wrapper/pvd-checkbox'))
            )
            asking_again.click()

            very_short_sleep()
            submit_code = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH, '//*[@id="dom-otp-code-submit-button"]'))
            )
            submit_code.click()

            logger.info("Submitted 2FA code via text.")
            short_sleep()

        elif method == 'app':
            # Wait for user to approve app notification
            logger.info("Awaiting site redirect")
            # Implement a polling mechanism or a waiting period
            # For simplicity, wait for a certain time and check if login is successful
            try:
                WebDriverWait(driver, 25).until(
                EC.url_to_be('https://secure.chase.com/web/auth/dashboard#/dashboard/overview')
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
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        del two_fa_sessions[session_id]

        return trade_response

    except Exception as e:
        logger.error(f"Error during 2FA completion and trade: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        del two_fa_sessions[session_id]
        return {'status': 'error', 'message': 'An error occurred during 2FA completion and trade.', 'error': str(e)}
    
    finally:
        driver.quit()