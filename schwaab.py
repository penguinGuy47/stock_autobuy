from sleep import *

# TODO:
# add multi buy function
def buy(ticker, dir, prof):
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={dir}")
    options.add_argument(f"--profile-directory={prof}") # add 
    options.add_argument("--disable-blink-features=AutomationControlled")   # bypass automation protection
    driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
    driver.get("https://client.schwab.com/Areas/Access/Login")
    wait = WebDriverWait(driver, 10)
    short_sleep()


    # sign in field
    try:
        driver.find_elements(By.TAG_NAME, "iframe")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "lmsIframe")))
        
        # ENTER YOUR CREDENTIALS
        username = "kash0440"   # ENTER YOUR USERNAME
        pw = "Jcpledd123?"         # ENTER YOUR PASSWORD
        
        # login
        username_field = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="loginIdInput"]'))
        )
        human_type(username, username_field)
        very_short_sleep()

        pw_field = driver.find_element(By.XPATH, '//*[@id="passwordInput"]')
        human_type(pw, pw_field)
        very_short_sleep()

        # login button
        login_button = driver.find_element(By.XPATH, '//*[@id="btnLogin"]')
        login_button.click()

    except Exception as e:
        print(f"An error occurred: {e}")

    os.system('echo \a')
    input("\n\nPlease complete 2FA if requested and then press Enter when you reach the dashboard...\n\n\n")
    print("Logged into Schwab!")
    short_sleep()

    # search ticker
    driver.get("https://client.schwab.com/app/trade/tom/trade")
    short_sleep()
    ticker_search = driver.find_element(By.XPATH, '//*[@id="_txtSymbol"]')
    human_type(ticker, ticker_search)
    very_short_sleep()
    ticker_search.send_keys(Keys.ENTER)

    long_sleep()

    

