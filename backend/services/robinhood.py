from utils.sleep import *
import logging
import uuid
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import random
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

two_fa_sessions = {}

def login(driver, tempdir, username, password):
    """
    Handles login typing and submitting functionality for Robinhood.
    """
    very_short_sleep()
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)
    
    # Apply enhanced protections
    enhance_fingerprint_protection(driver)
    normalize_network_patterns(driver)
    improve_session_management(driver)

    try:
        # Enter username
        username_field = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="react_root"]/div[1]/div[2]/div/div/div[2]/div[2]/div/form/div/div[1]/label/div[2]/input'))
        )
        
        # Natural mouse movement to username field
        natural_mouse_movement(driver, end_element=username_field, duration=random.uniform(0.8, 1.5))
        very_short_sleep()
        
        # More realistic typing
        realistic_typing(username, username_field, error_probability=0.02)
        very_short_sleep()

        # Enter password with similar enhancements
        pw_field = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="current-password"]'))
        )
        natural_mouse_movement(driver, start_element=username_field, end_element=pw_field, duration=random.uniform(0.5, 1.2))
        very_short_sleep()
        
        realistic_typing(password, pw_field, error_probability=0.01)  # Less errors on password typically
        
        # Sometimes users check "Remember me" box
        if random.random() < 0.7:  # 70% chance
            try:
                remember_me = driver.find_element(By.XPATH, '//label[contains(text(), "Remember")]')
                natural_mouse_movement(driver, start_element=pw_field, end_element=remember_me, duration=random.uniform(0.4, 0.8))
                very_short_sleep()
            except Exception:
                pass
        
        very_short_sleep()
        
        while True:
            # Click login button
            logger.info("Clicking Robinhood login button.")
            login_button = driver.find_element(By.XPATH, '//*[@id="react_root"]/div[1]/div[2]/div/div/div[2]/div[2]/div/form/footer/div[1]/div[1]/button')  # PLACEHOLDER: update with actual XPath
            actions.move_to_element(login_button).perform()
            driver.execute_script("arguments[0].click();", login_button)

            # Short sleep before checking if the button is still available
            very_short_sleep()

            # Check if the login button is still available
            try:
                # Click the login button
                driver.execute_script("arguments[0].click();", login_button)
                very_short_sleep()  # Optional: Add a short sleep after clicking

                # Attempt to detect 2FA approval (app-based) by waiting for the Continue button to be clickable
                try:
                    # Wait for the Continue button to be clickable
                    wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="react_root"]/div[3]/div/div[3]/div/div/section/div/div/div/div/div[2]/main/div[3]/div[1]/button'))
                    )
                    logger.info("2FA via app approved automatically, Continue button is clickable.")
                    
                    # Generate a unique session ID and store session details
                    session_id = str(uuid.uuid4())
                    two_fa_sessions[session_id] = {
                        'driver': driver,
                        'temp_dir': tempdir,
                        'username': username,
                        'password': password,
                        'method': 'app',
                        'action': None  # To be set by buy/sell functions
                    }
                    return {'status': '2FA_required', 'method': 'app', 'session_id': session_id}
                except TimeoutException:
                    logger.info("Continue button is not available, restarting login process.")
                    continue  # Now this continue is valid
            except Exception as e:
                logger.error(f"Error during login process: {str(e)}")
                driver.quit()
                shutil.rmtree(tempdir, ignore_errors=True)
                raise e
            break  # Exit the loop if everything succeeds

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        driver.quit()
        shutil.rmtree(tempdir, ignore_errors=True)
        raise e

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
    ticker = session_info.get('ticker')
    trade_share_count = session_info.get('trade_share_count')

    wait = WebDriverWait(driver, 60)
    try:
        if method == 'text':
            if not two_fa_code:
                logger.error("2FA code is missing for text-based 2FA.")
                driver.quit()
                shutil.rmtree(temp_dir, ignore_errors=True)
                del two_fa_sessions[session_id]
                return {'status': 'error', 'message': '2FA code is required for text-based 2FA.'}

            # Enter the 2FA code
            code_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, 'XPATH_FOR_2FA_INPUT'))  # PLACEHOLDER: update with actual XPath
            )
            human_type(two_fa_code, code_input)
            very_short_sleep()

            submit_code = driver.find_element(By.XPATH, 'XPATH_FOR_2FA_SUBMIT_BUTTON')  # PLACEHOLDER: update with actual XPath
            submit_code.click()
            logger.info("Submitted 2FA code via text.")
            short_sleep()

        elif method == 'app':
            logger.info("Awaiting app 2FA approval.")
            short_sleep()
        else:
            logger.error("Invalid 2FA method specified.")
            driver.quit()
            shutil.rmtree(temp_dir, ignore_errors=True)
            del two_fa_sessions[session_id]
            return {'status': 'error', 'message': 'Invalid 2FA method specified.'}

        short_sleep()
        # After 2FA, proceed with the trade
        if action == 'buy':
            trade_response = buy_after_login(driver, ticker, trade_share_count)
        elif action == 'sell':
            trade_response = sell_after_login(driver, ticker, trade_share_count)
        else:
            logger.error("Invalid trade action specified.")
            driver.quit()
            shutil.rmtree(temp_dir, ignore_errors=True)
            del two_fa_sessions[session_id]
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

def buy(tickers, dir, prof, trade_share_count, username, password, two_fa_code=None):
    """
    Initiates a buy operation for the specified tickers and quantity.
    """
    logger.info(f"Initiating buy operation for {trade_share_count} shares of {tickers} by user {username}")
    driver, temp_dir = start_regular_driver(dir, prof)
    
    try:
        driver.get("https://robinhood.com/login")
        login_response = login(driver, temp_dir, username, password)

        if login_response['status'] == '2FA_required':
            logger.info(f"2FA required via {login_response['method']}.")
            session_id = login_response.get('session_id')
            two_fa_sessions[session_id]['action'] = 'buy'
            two_fa_sessions[session_id]['tickers'] = tickers  # Allow multiple tickers
            two_fa_sessions[session_id]['trade_share_count'] = trade_share_count  # Changed from qty to trade_share_count
            os.system('echo \a')
            return {
                'status': '2FA_required',
                'method': login_response['method'],
                'session_id': session_id,
                'message': '2FA is required.'
            }
        elif login_response['status'] == 'success':
            trade_response = buy_after_login(driver, tickers, trade_share_count)  # Adjusted for trade_share_count
            driver.quit()
            shutil.rmtree(temp_dir, ignore_errors=True)
            return trade_response
        else:
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
    """
    Executes the buy operation after a successful login.
    """
    try:
        setup_trade(driver, tickers)
        accounts = get_num_accounts(driver)
        logger.info(f"Number of accounts found: {accounts}")

        for account_num in range(1, accounts + 1):
            if account_num != 1:
                switch_accounts(driver, account_num)
            enter_share_qty(driver, trade_share_count)  # Changed from qty to trade_share_count
            submit_order(driver)
        logger.info(f"Buy order for {trade_share_count} shares of {tickers} submitted successfully via Robinhood.")
        return {
            'status': 'success',
            'message': f'Buy order for {trade_share_count} shares of {tickers} submitted via Robinhood.'
        }
    except Exception as e:
        logger.error(f"Error during buy_after_login operation: {str(e)}")
        raise e

def sell(ticker, dir, prof, qty, username, password, two_fa_code=None):
    """
    Initiates a sell operation for the specified ticker and quantity.
    """
    logger.info(f"Initiating sell operation for {qty} shares of {ticker} by user {username}")
    driver, temp_dir = start_regular_driver(dir, prof)
    driver.get("https://robinhood.com/login")
    short_sleep()

    login_response = login(driver, temp_dir, username, password)

    if login_response['status'] == '2FA_required':
        session_id = login_response.get('session_id')
        two_fa_sessions[session_id]['action'] = 'sell'
        two_fa_sessions[session_id]['ticker'] = ticker
        two_fa_sessions[session_id]['qty'] = qty
        return {
            'status': '2FA_required',
            'method': login_response['method'],
            'session_id': session_id,
            'message': '2FA is required. Please provide the 2FA code.'
        }
    elif login_response['status'] == 'success':
        trade_response = sell_after_login(driver, ticker, qty)
        driver.quit()
        shutil.rmtree(temp_dir, ignore_errors=True)
        return trade_response
    else:
        driver.quit()
        shutil.rmtree(temp_dir, ignore_errors=True)
        return {
            'status': 'failure',
            'message': login_response.get('message', 'Login failed.')
        }

def sell_after_login(driver, ticker, qty):
    """
    Executes the sell operation after a successful login.
    """
    try:
        setup_trade(driver, ticker)
        # Navigate to the sell option (adjust XPath as needed)
        sell_option = driver.find_element(By.XPATH, 'XPATH_FOR_SELL_OPTION')  # PLACEHOLDER: update with actual XPath
        sell_option.click()
        very_short_sleep()

        accounts = get_num_accounts(driver)
        logger.info(f"Number of accounts found: {accounts}")

        for account_num in range(1, accounts + 1):
            if account_num != 1:
                switch_accounts(driver, account_num)
            enter_share_qty(driver, qty)
            submit_order(driver)
        logger.info(f"Sell order for {qty} shares of {ticker} submitted successfully via Robinhood.")
        return {
            'status': 'success',
            'message': f'Sell order for {qty} shares of {ticker} submitted via Robinhood.'
        }
    except Exception as e:
        logger.error(f"Error during sell_after_login operation: {str(e)}")
        raise e

def setup_trade(driver, ticker):
    """
    Searches for the given ticker and sets up the trade page.
    """
    logger.info("Setting up trade...")
    try:
        ticker_search = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="downshift-0-input"]'))  # PLACEHOLDER: update with actual XPath
        )
        ticker_search.click()
        human_type(ticker, ticker_search)
        very_short_sleep()
        ticker_search.send_keys(Keys.ARROW_DOWN)
        ticker_search.send_keys(Keys.ENTER)
        short_sleep()
    except TimeoutException:
        logger.error("Timed out waiting for ticker search element.")

def enter_share_qty(driver, qty):
    """
    Enters the share quantity into the order form.
    """
    short_sleep()
    try:
        # Optionally switch to "shares" mode if necessary
        shares_dropdown = driver.find_element(By.XPATH, 'XPATH_FOR_SHARES_DROPDOWN')  # PLACEHOLDER
        shares_dropdown.click()
        short_sleep()
        shares_option = driver.find_element(By.XPATH, 'XPATH_FOR_SHARES_OPTION_SHARE')  # PLACEHOLDER
        shares_option.click()
        short_sleep()
    except Exception:
        pass

    # Dismiss any overlays by clicking a random element
    random_click = driver.find_element(By.XPATH, 'XPATH_FOR_RANDOM_CLICK')  # PLACEHOLDER
    random_click.click()

    logger.info("Entering share quantity...")
    short_sleep()
    shares_qty = driver.find_element(By.XPATH, 'XPATH_FOR_SHARES_QTY_INPUT')  # PLACEHOLDER
    shares_qty.click()
    human_type(qty, shares_qty)
    very_short_sleep()

def submit_order(driver):
    """
    Submits the trade order.
    """
    wait = WebDriverWait(driver, 10)
    try:
        # Click the initial submit/review button
        submit_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, 'XPATH_FOR_SUBMIT_BUTTON'))  # PLACEHOLDER
        )
        submit_button.click()
        very_short_sleep()

        # Confirm the order if a confirmation step exists
        confirm_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, 'XPATH_FOR_CONFIRM_BUTTON'))  # PLACEHOLDER
        )
        confirm_button.click()
        very_short_sleep()

        # Click the done button to finalize the process
        done_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, 'XPATH_FOR_DONE_BUTTON'))  # PLACEHOLDER
        )
        done_button.click()
        short_sleep()
        logger.info("Order successfully submitted!")
    except Exception as e:
        logger.error("Error submitting order: %s", str(e))

def get_num_accounts(driver):
    """
    Retrieves the number of accounts available.
    """
    logger.info("Getting number of accounts...")
    try:
        initial_dropdown = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, 'XPATH_FOR_ACCOUNT_DROPDOWN'))  # PLACEHOLDER
        )
        initial_dropdown.click()
        very_short_sleep()
        account_container = driver.find_element(By.XPATH, 'XPATH_FOR_ACCOUNT_CONTAINER')  # PLACEHOLDER
        accounts = account_container.find_elements(By.TAG_NAME, 'button')
        return len(accounts)
    except Exception:
        logger.error("Could not locate accounts dropdown.")
        return 0

def switch_accounts(driver, account_num):
    """
    Switches to the specified account number.
    """
    try:
        initial_dropdown = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, 'XPATH_FOR_ACCOUNT_DROPDOWN'))  # PLACEHOLDER
        )
        initial_dropdown.click()
        next_account = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, f'XPATH_FOR_ACCOUNT_BUTTON[{account_num}]'))  # PLACEHOLDER
        )
        next_account.click()
        short_sleep()
    except Exception:
        logger.error("Error switching accounts.")

def improve_session_management(driver):
    """Implement session management techniques to appear more human-like"""
    
    # Set cookies that normal browsers would have
    common_cookies = [
        {'name': 'cookieConsent', 'value': 'true'},
        {'name': 'sessionDepth', 'value': str(random.randint(1, 5))},
        {'name': 'lastVisit', 'value': str(int(time.time() - random.randint(86400, 604800)))},
    ]
    
    for cookie in common_cookies:
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass  # Skip if domain doesn't match
    
    # Simulate browser history/navigation
    if random.random() < 0.2:  # 20% chance
        # Navigate to home page first, then to target
        driver.get("https://robinhood.com/")
        very_short_sleep()
        # Then navigate to login page through UI instead of direct URL
        try:
            login_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Log In')]")
            natural_mouse_movement(driver, end_element=login_link)
            short_sleep()
        except Exception:
            # Fall back to direct navigation if element not found
            driver.get("https://robinhood.com/login")
    
    # Set localStorage items that would be present in real user sessions
    local_storage_items = {
        'theme': random.choice(['light', 'dark', 'system']),
        'previousVisits': str(random.randint(1, 20)),
        'hasSeenWelcome': 'true',
    }
    
    for key, value in local_storage_items.items():
        driver.execute_script(f"localStorage.setItem('{key}', '{value}');")
