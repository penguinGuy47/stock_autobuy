from utils.sleep import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

two_fa_sessions = {}

# TODO:
# fix errors
# address cookie saving/loading
# add multi buy function
def buy(ticker, dir, prof, qty):
    driver, temp_dir = start_regular_driver(dir, prof)
    # driver = start_headless_driver(dir, prof)
    driver.get("https://robinhood.com/login")
    short_sleep()

    # try:
    #     load_cookies(driver, "rh_cookies.pkl")
    #     driver.refresh()
    # except Exception as e:
    #     logger.info(e)
    #     logger.info("No cookies available")
    #     short_sleep()
    #     driver.get("https://robinhood.com/login")

    # short_sleep()
    login(driver)
    setup_trade(driver, ticker)
    accounts = get_num_accounts(driver)
    for accNum in range(1, accounts+1):
        if accNum != 1:
            switch_accounts(driver, accNum)
        enter_share_qty(driver, qty)
        submit_order(driver)
    driver.quit()


def sell(ticker, dir, prof, qty):
    driver = start_headless_driver(dir, prof)
    driver.get("https://robinhood.com/login/")
    short_sleep()
    login(driver)
    setup_trade(driver, ticker)

    # navigate to sell
    enter_sell = driver.find_element(By.XPATH, '//*[@id="sdp-ticker-symbol-highlight"]/div[1]/form/div[1]/div/div[1]/div/div/div[2]/div/div/div/div')
    enter_sell.click()

    very_short_sleep()
    accounts = get_num_accounts(driver)
    for accNum in range(1, accounts+1):
        if accNum != 1:
            switch_accounts(driver, accNum)
        enter_share_qty(driver, qty)
        submit_order(driver)
    driver.quit()


def login(driver, tempdir ,username, password):
    wait = WebDriverWait(driver, 7)

    if driver.current_url != "https://robinhood.com/":
        username_field = driver.find_element(By.XPATH, '//*[@id="react_root"]/div[1]/div[2]/div/div/div/div[2]/div/form/div/div[1]/label/div[2]/input')
        username_field.click()
        human_type(username, username_field)
        very_short_sleep()

        pw_field = driver.find_element(By.XPATH, '//*[@id="current-password"]')
        pw_field.click()
        human_type(password, pw_field)
        very_short_sleep()

        # keep_login = driver.find_element(By.XPATH, '//*[@id="react_root"]/div[1]/div[2]/div/div/div/div[2]/div/form/div/div[3]/label/div/div/div')
        # keep_login.click()
        # very_short_sleep()

        login_button = driver.find_element(By.XPATH, '//*[@id="react_root"]/div[1]/div[2]/div/div/div[2]/div[2]/div/form/footer/div[1]/div/button')
        login_button.click()

        try: 
            # waits up to 60 seconds for user to accept notification
            WebDriverWait(driver, 60).until(
                EC.url_to_be("https://robinhood.com/")
            )
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
        except TimeoutException:
            logger.info("\n\nError: you did not accept the 2FA request \n\n")

            # SMS 2FA
            try:
                code_input = wait.until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="react_root"]/div[3]/div/div[3]/div/div/section/div/div/div/div/div[2]/div[2]/div/form/div/div/input'))
                )

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

                # To input 2FA code and continue

                code_input = wait.until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="react_root"]/div[3]/div/div[3]/div/div/section/div/div/div/div/div[2]/div[2]/div/form/div/div/input'))
                )

                human_type(TEMPVAR ,code_input)
                continue_button = driver.find_element(By.XPATH, '//*[@id="react_root"]/div[3]/div/div[3]/div/div/section/div/div/div/div/div[2]/div[3]/div[1]/div/button')
                continue_button.click()
                short_sleep()
                driver.get("https://robinhood.com/us/en/")
                short_sleep()
                save_cookies(driver, "rh_cookies.pkl")
            except TimeoutException:
                logger.info("2FA input timed out.")
                # restart_driver()
            
def setup_trade(driver, ticker):
    # Searches for the ticker
    try:
        # short_sleep()
        # ticker_search = driver.find_element(By.XPATH, '//*[@id="downshift-0-input"]')
        ticker_search = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="downshift-0-input"]'))
        )
        ticker_search.click()
        human_type(ticker, ticker_search)
        very_short_sleep()
        ticker_search.send_keys(Keys.ARROW_DOWN)
        ticker_search.send_keys(Keys.ENTER)
        short_sleep()
    except TimeoutException:
        logger.info("Timed out waiting ticker search to appear...")

def enter_share_qty(driver, qty):
    # select buy in shares
    short_sleep()
    try:
        shares_dropdown = driver.find_element(By.XPATH, '//button[starts-with(@id, "downshift-") and contains(@id, "-toggle") and .//span[text()="Dollars"]]')
        shares_dropdown.click()
        short_sleep()
        # disregard everything before: -options-menu-list-option-share"]
        shares_button = driver.find_element(By.XPATH, '//*[contains(@id, "options-menu-list-option-share")]')
        shares_button.click()
        short_sleep()
    except:
        pass

    random_click = driver.find_element(By.XPATH, '//*[@id="react_root"]/main/div[2]/div/div/div/div/main/div/div/div/header')
    random_click.click()

    logger.info("Entering share qty...")
    # enter number of shares shares
    short_sleep()

    # shares_qty = WebDriverWait(driver,100).until(
    #     # EC.element_to_be_clickable((By.XPATH, '//*[@id="sdp-ticker-symbol-highlight"]/div[1]/form/div[2]/div/div[3]/div/div/div/div/input'))
    #     EC.visibility_of_element_located((By.XPATH, '//*[@id="sdp-ticker-symbol-highlight"]/div[2]/form/div[2]/div/div[2]/div/div/div/div'))
    # )

    shares_qty = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div/div/div/main/div/aside/div[2]/form/div[2]/div/div[2]/div/div/div/div/input')
    shares_qty.click()
    human_type(qty, shares_qty)
    very_short_sleep()

        # logger.info("Error entering share quantity...")


def submit_order(driver):
    # review order button for penny stocks: //*[@id="sdp-ticker-symbol-highlight"]/div[2]/form/div[3]/div/div[2]/div/div/button
    # //*[@id="sdp-ticker-symbol-highlight"]/div[2]/form/div[3]/div/div[2]/div[1]/div/button
    # review order button for non-penny stocks: submit_button = driver.find_element(By.XPATH, '//*[@id="sdp-ticker-symbol-highlight"]/div[1]/form/div[3]/div/div[2]/div/div/button')
    # submit order button for non-penny stocks: //*[@id="sdp-ticker-symbol-highlight"]/div[1]/form/div[3]/div/div[2]/div[1]/div/button
    wait = WebDriverWait(driver, 10)
    try:
        submit_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sdp-ticker-symbol-highlight"]/div[1]/form/div[3]/div/div[2]/div/div/button'))
        )
        submit_button.click()
        very_short_sleep()
        verify_submit = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sdp-ticker-symbol-highlight"]/div[1]/form/div[3]/div/div[2]/div[1]/div/button'))
        )
        verify_submit.click()
        done_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sdp-ticker-symbol-highlight"]/div[1]/div/div[3]/div/button'))
        )
        done_button.click()
        short_sleep()
    except:
        logger.info("error submitting order...")

def get_num_accounts(driver):
    logger.info("Getting all your accounts...")
    try:
        initial_dropdown = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sdp-ticker-symbol-highlight"]/div[2]/form/button'))
        )
        initial_dropdown.click()
        very_short_sleep()
        div = driver.find_element(By.XPATH, '//*[@id="account-switcher-popover"]/div')
        accounts = div.find_elements(By.TAG_NAME, 'button')
        num_accounts = len(accounts)
        return num_accounts+""
    except:
        logger.info("Could not locate dropdown...")

def switch_accounts(driver, account_num):
    # //*[@id="account-switcher-popover"]/div/button[1]
    # //*[@id="account-switcher-popover"]/div/button[2]
    try:
        initial_dropdown = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sdp-ticker-symbol-highlight"]/div[1]/form/button'))
        )
        initial_dropdown.click()
        
        next_account = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, f'//*[@id="account-switcher-popover"]/div/button[{account_num}]'))
        )
        next_account.click()
        short_sleep()
        pass
    except:
        logger.info("Error switching accounts...")
    


