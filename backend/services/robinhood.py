from utils.sleep import *
import logging
import uuid
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

two_fa_sessions = {}

def login(driver, tempdir, username, password):
    """
    Handles login typing and submitting functionality for Robinhood.
    """
    short_sleep()
    driver.get("https://robinhood.com/login")
    short_sleep()
    wait = WebDriverWait(driver, 10)

    try:
        # Enter username
        username_field = wait.until(
            EC.element_to_be_clickable((By.XPATH, 'XPATH_FOR_USERNAME_FIELD'))  # PLACEHOLDER: update with actual XPath
        )
        username_field.click()
        human_type(username, username_field)
        very_short_sleep()

        # Enter password
        pw_field = wait.until(
            EC.element_to_be_clickable((By.XPATH, 'XPATH_FOR_PASSWORD_FIELD'))  # PLACEHOLDER: update with actual XPath
        )
        pw_field.click()
        human_type(password, pw_field)
        very_short_sleep()

        # Click login button
        logger.info("Clicking Robinhood login button.")
        login_button = driver.find_element(By.XPATH, 'XPATH_FOR_LOGIN_BUTTON')  # PLACEHOLDER: update with actual XPath
        login_button.click()

        # Attempt to detect 2FA approval (app-based) by waiting for a URL change
        try:
            WebDriverWait(driver, 60).until(EC.url_to_be("https://robinhood.com/"))
            logger.info("2FA via app approved automatically.")
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
            # If not auto-approved, try to locate text-based 2FA input field
            try:
                code_input = wait.until(
                    EC.visibility_of_element_located((By.XPATH, 'XPATH_FOR_2FA_INPUT'))  # PLACEHOLDER: update with actual XPath
                )
                logger.info("Text-based 2FA detected.")
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
            except TimeoutException:
                logger.error("2FA was not detected; login may have failed.")
                driver.quit()
                shutil.rmtree(tempdir, ignore_errors=True)
                return {'status': 'error', 'message': 'Login failed; 2FA not detected.'}

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
    qty = session_info.get('qty')

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
            # Wait for app approval (or page redirect)
            logger.info("Awaiting app 2FA approval.")
            short_sleep(15)  # Adjust wait time as needed

        else:
            logger.error("Invalid 2FA method specified.")
            driver.quit()
            shutil.rmtree(temp_dir, ignore_errors=True)
            del two_fa_sessions[session_id]
            return {'status': 'error', 'message': 'Invalid 2FA method specified.'}

        short_sleep()
        # After 2FA, proceed with the trade
        if action == 'buy':
            trade_response = buy_after_login(driver, ticker, qty)
        elif action == 'sell':
            trade_response = sell_after_login(driver, ticker, qty)
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

def buy(ticker, dir, prof, qty, username, password, two_fa_code=None):
    """
    Initiates a buy operation for the specified ticker and quantity.
    """
    logger.info(f"Initiating buy operation for {qty} shares of {ticker} by user {username}")
    driver, temp_dir = start_regular_driver(dir, prof)
    driver.get("https://robinhood.com/login")
    short_sleep()

    login_response = login(driver, temp_dir, username, password)

    if login_response['status'] == '2FA_required':
        session_id = login_response.get('session_id')
        two_fa_sessions[session_id]['action'] = 'buy'
        two_fa_sessions[session_id]['ticker'] = ticker
        two_fa_sessions[session_id]['qty'] = qty
        return {
            'status': '2FA_required',
            'method': login_response['method'],
            'session_id': session_id,
            'message': '2FA is required. Please provide the 2FA code.'
        }
    elif login_response['status'] == 'success':
        trade_response = buy_after_login(driver, ticker, qty)
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

def buy_after_login(driver, ticker, qty):
    """
    Executes the buy operation after a successful login.
    """
    try:
        setup_trade(driver, ticker)
        accounts = get_num_accounts(driver)
        logger.info(f"Number of accounts found: {accounts}")

        for account_num in range(1, accounts + 1):
            if account_num != 1:
                switch_accounts(driver, account_num)
            enter_share_qty(driver, qty)
            submit_order(driver)
        logger.info(f"Buy order for {qty} shares of {ticker} submitted successfully via Robinhood.")
        return {
            'status': 'success',
            'message': f'Buy order for {qty} shares of {ticker} submitted via Robinhood.'
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
    try:
        ticker_search = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, 'XPATH_FOR_TICKER_SEARCH'))  # PLACEHOLDER: update with actual XPath
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
