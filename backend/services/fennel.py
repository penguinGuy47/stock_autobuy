from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track 2FA sessions
two_fa_sessions = {}

def setup_driver():
    """
    Sets up and returns the Appium driver with appropriate options
    """
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "emulator-5554"  # Update to match your emulator's device name
    options.app_package = "com.fennel.app"
    options.app_activity = "com.fennel.app.MainActivity"
    options.automation_name = "UiAutomator2"

    print("Connecting to Appium server...")
    driver = webdriver.Remote("http://localhost:4723", options=options)
    return driver

def login(driver, tempdir=None, username=None, password=None):
    """
    Handles login functionality for Fennel app
    Returns status dict similar to fidelity implementation
    """
    try:
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds

        # Allow/deny notifications
        try:
            # Wait for and click the permission dialog
            allow_button = wait.until(
                    EC.presence_of_element_located(
                        (By.ID, "com.android.permissioncontroller:id/permission_deny_button")
                    )
            )
            allow_button.click()
            logger.info("Handled notification permission")

        except Exception as e:
            logger.info("No notification permission dialog found")

        # Click "Log in" button
        try:
            login_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//android.widget.Button[@content-desc='Log in']")
                )
            )
            login_button.click()
            logger.info("Clicked 'Log in' button")
        except Exception as e:
            logger.error(f"Error clicking login button: {e}")
            return {'status': 'error', 'message': 'Failed to click login button'}

        # Enter email
        try:
            email_input = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//android.widget.EditText")
                )
            )
            email_input.send_keys(username)
            logger.info("Entered email")
        except Exception as e:
            logger.error(f"Error entering email: {e}")
            return {'status': 'error', 'message': 'Failed to enter email'}
        
        # Check for and handle popup
        try:
            # Wait a short time to see if popup appears
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//android.widget.RelativeLayout[@resource-id=\"com.fennel.app:id/ib_core_onboarding_container\"]/android.widget.RelativeLayout"
                ))
            )
            logger.info("Popup detected - attempting to dismiss it")
            
            # Get screen size
            screen_size = driver.get_window_size()
            screen_width = screen_size['width']
            screen_height = screen_size['height']
            
            # Tap near the bottom of the screen to dismiss popup
            driver.tap([(int(screen_width * 0.5), int(screen_height * 0.8))], 100)
            logger.info("Tapped elsewhere to dismiss popup")
            
            time.sleep(1)
            
        except Exception as e:
            logger.info("No popup detected or couldn't dismiss it")

        # Click "Log in" button to continue
        try:
            continue_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//android.widget.Button[@content-desc='Continue']")
                )
            )
            continue_button.click()
            logger.info("Clicked 'Log in' button to continue")
        except Exception as e:
            logger.error(f"Error clicking 'Log in' button: {e}")
            return {'status': 'error', 'message': 'Failed to click continue button'}

        # Check for 2FA input
        try:
            two_factor_input = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//android.widget.EditText")
                )
            )
            logger.info("2FA input detected")
            
            # Generate a unique session ID
            session_id = str(uuid.uuid4())
            two_fa_sessions[session_id] = {
                'driver': driver,
                'temp_dir': tempdir,
                'username': username,
                'password': password,
                'method': 'email',
                'action': None  # To be set by buy/sell functions
            }
            
            # Indicate that Text-Based 2FA is required
            return {'status': '2FA_required', 'method': 'email', 'session_id': session_id}
            
        except Exception as e:
            logger.info("No 2FA input detected, login successful")
            return {'status': 'success'}

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return {'status': 'error', 'message': f'Login failed: {str(e)}'}

def complete_2fa_and_trade(session_id, two_fa_code=None):
    """
    Completes the 2FA process and performs the requested trade
    """
    logger.info(f"Completing 2FA for session {session_id}")
    
    if session_id not in two_fa_sessions:
        logger.error("Invalid session ID")
        return {'status': 'error', 'message': 'Invalid session ID'}
    
    session_info = two_fa_sessions[session_id]
    driver = session_info['driver']
    action = session_info['action']
    tickers = session_info.get('tickers')
    trade_share_count = session_info.get('trade_share_count')
    
    try:
        wait = WebDriverWait(driver, 10)
        
        # Enter 2FA code
        if two_fa_code:
            try:
                two_factor_input = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//android.widget.EditText")
                    )
                )
                two_factor_input.send_keys(two_fa_code)
                logger.info("Entered 2FA code")
                
                # Automatically submits after inputting the code
                time.sleep(2)  # Wait for processing
                
            except Exception as e:
                logger.error(f"Error submitting 2FA code: {e}")
                return {'status': 'error', 'message': 'Failed to submit 2FA code'}
        
        # After 2FA, proceed with the trade
        # TODO: Implement specific buy/sell logic for Fennel app
        if action == 'buy':
            return buy_after_login(driver, tickers, trade_share_count)
        elif action == 'sell':
            return sell_after_login(driver, tickers, trade_share_count)
        else:
            logger.error("Invalid trade action specified")
            return {'status': 'error', 'message': 'Invalid trade action specified'}
            
    except Exception as e:
        logger.error(f"Error during 2FA completion: {str(e)}")
        return {'status': 'error', 'message': f'2FA completion failed: {str(e)}'}
    finally:
        # Clean up the session
        if session_id in two_fa_sessions:
            del two_fa_sessions[session_id]

def buy(tickers, dir=None, prof=None, trade_share_count=None, username=None, password=None, two_fa_code=None):
    """
    Initiates a buy operation for the specified ticker and quantity
    """
    logger.info(f"Initiating buy operation for {trade_share_count} shares of {tickers}")
    
    try:
        driver = setup_driver()
        login_response = login(driver, None, username, password)
        
        if login_response['status'] == '2FA_required':
            logger.info(f"2FA required via {login_response['method']}")
            # Store action details in the session
            session_id = login_response.get('session_id')
            two_fa_sessions[session_id]['action'] = 'buy'
            two_fa_sessions[session_id]['tickers'] = tickers
            two_fa_sessions[session_id]['trade_share_count'] = trade_share_count
            return login_response
            
        elif login_response['status'] == 'success':
            # Proceed with buying
            return buy_after_login(driver, tickers, trade_share_count)
            
        else:
            # Handle other statuses
            if driver is not None:
                driver.quit()
            return {
                'status': 'failure',
                'message': login_response.get('message', 'Login failed')
            }
            
    except Exception as e:
        logger.error(f"Error during buy operation: {str(e)}")
        if 'driver' in locals() and driver is not None:
            driver.quit()
        return {
            'status': 'failure',
            'message': f'Failed to buy {tickers}',
            'error': str(e)
        }

def buy_after_login(driver, tickers, trade_share_count):
    """
    Performs buy operation after successful login
    """
    try:
        # TODO: Implement specific buy logic for Fennel app
        # You'll need to implement the UI interactions specific to the buy process
        
        logger.info(f"Buying {trade_share_count} shares of {tickers}")
        # Example stub - replace with actual implementation
        return {
            'status': 'success',
            'message': f'Bought {trade_share_count} shares of {tickers} through Fennel',
            'data': {
                'tickers': tickers,
                'quantity': trade_share_count,
            }
        }
        
    except Exception as e:
        logger.error(f"Error during buy after login: {str(e)}")
        raise e

def sell(tickers, dir=None, prof=None, trade_share_count=None, username=None, password=None, two_fa_code=None):
    """
    Initiates a sell operation for the specified ticker and quantity
    """
    logger.info(f"Initiating sell operation for {trade_share_count} shares of {tickers}")
    
    try:
        driver = setup_driver()
        login_response = login(driver, None, username, password)
        
        if login_response['status'] == '2FA_required':
            logger.info(f"2FA required via {login_response['method']}")
            # Store action details in the session
            session_id = login_response.get('session_id')
            two_fa_sessions[session_id]['action'] = 'sell'
            two_fa_sessions[session_id]['tickers'] = tickers
            two_fa_sessions[session_id]['trade_share_count'] = trade_share_count
            return login_response
            
        elif login_response['status'] == 'success':
            # Proceed with selling
            return sell_after_login(driver, tickers, trade_share_count)
            
        else:
            # Handle other statuses
            if driver is not None:
                driver.quit()
            return {
                'status': 'failure',
                'message': login_response.get('message', 'Login failed')
            }
            
    except Exception as e:
        logger.error(f"Error during sell operation: {str(e)}")
        if 'driver' in locals() and driver is not None:
            driver.quit()
        return {
            'status': 'failure',
            'message': f'Failed to sell {tickers}',
            'error': str(e)
        }

def sell_after_login(driver, tickers, trade_share_count):
    """
    Performs sell operation after successful login
    """
    try:
        # TODO: Implement specific sell logic for Fennel app
        # You'll need to implement the UI interactions specific to the sell process
        
        logger.info(f"Selling {trade_share_count} shares of {tickers}")
        # Example stub - replace with actual implementation
        return {
            'status': 'success',
            'message': f'Sold {trade_share_count} shares of {tickers} through Fennel',
            'data': {
                'tickers': tickers,
                'quantity': trade_share_count,
            }
        }

    except Exception as e:
            logger.error(f"Error during sell after login: {str(e)}")
            raise e

    # Keep the script running for a bit to observe (optional)
    time.sleep(10)