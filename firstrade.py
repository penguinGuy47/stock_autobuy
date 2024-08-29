from sleep import *

# TODO:
# add multi buy function
def buy(ticker, dir, prof):
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={dir}")
    options.add_argument(f"--profile-directory={prof}") # add 
    options.add_argument("--disable-blink-features=AutomationControlled")   # bypass automation protection
    driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
    driver.get("https://invest.firstrade.com/cgi-bin/login")
    wait = WebDriverWait(driver, 10)
    short_sleep()

    # ENTER YOUR CREDENTIALS
    username = ""   # ENTER YOUR USERNAME
    pw = ""         # ENTER YOUR PASSWORD

    username_field = driver.find_element(By.XPATH, '//*[@id="username"]')
    username_field.click()
    human_type(username, username_field)

    pw_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    human_type(pw, pw_field)
    short_sleep()

    submit_button = driver.find_element(By.XPATH, '//*[@id="loginButton"]')
    submit_button.click()

    os.system('echo \a')
    input("\n\nPlease complete 2FA if requested and then press Enter when you reach the dashboard...\n\n\n")
    print("Logged into First Trade!")
    short_sleep()

    account_dropdown = driver.find_element(By.XPATH, '//*[@id="head"]/ul/li[7]/div')
    account_dropdown.click()

    short_sleep()

    accounts_column = driver.find_elements(By.XPATH, '//*[@id="headcontent"]/div[3]/div[2]/table/tbody//a')

    bought_accounts = set()
    for account in range(1, len(accounts_column) + 1):
        if account != 1:
            account_dropdown = driver.find_element(By.XPATH, '//*[@id="head"]/ul/li[7]/div')
            account_dropdown.click()

            short_sleep()

        current_account = driver.find_element(By.XPATH, f'//*[@id="headcontent"]/div[3]/div[2]/table/tbody/tr[{account}]/th/a')
        bought_accounts.add(current_account.text)
        current_account.click()

        print("Bought accounts: ")
        print(bought_accounts)
        short_sleep()

        # input ticker
        ticker_search = driver.find_element(By.XPATH, '//*[@id="id-symlookup"]')
        ticker_search.clear()
        very_short_sleep()
        human_type(ticker, ticker_search)
        very_short_sleep()

        # click on search
        ticker_search = driver.find_element(By.XPATH, '//*[@id="id-searchbtngo"]')
        ticker_search.click()
        short_sleep()

        # buy button
        buy_button = driver.find_element(By.XPATH, '//*[@id="maincontent"]/div/div[2]/div[1]/div[3]/button[1]')
        buy_button.click()
        short_sleep()

        # qty
        share_qty = driver.find_element(By.XPATH, '//*[@id="quantity"]')
        human_type("1", share_qty)
        very_short_sleep()

        # send order (submit)
        send_button = driver.find_element(By.XPATH, '//*[@id="submitOrder"]')
        send_button.click()
        short_sleep()




    long_sleep()
    
    print("No more accounts to process.")
    driver.quit()
    exit()

