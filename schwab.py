from sleep import *

# TODO:
# add multi buy function
def buy(ticker, dir, prof):
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={dir}")
    options.add_argument(f"--profile-directory={prof}")
    options.add_argument("--disable-blink-features=AutomationControlled")   # bypass automation protection
    driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
    driver.get("https://client.schwab.com/Areas/Access/Login")
    wait = WebDriverWait(driver, 5)
    short_sleep()


    # sign in field
    try:
        driver.find_elements(By.TAG_NAME, "iframe")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "lmsIframe")))
        
        # ENTER YOUR CREDENTIALS
        # username = "minc8088"   # ENTER YOUR USERNAME
        # pw = "Jcpledd123?"         # ENTER YOUR PASSWORD
        username = "kash0440"
        pw = "Jcpledd123?" 

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

    # redirect to trade page
    driver.get("https://client.schwab.com/app/trade/tom/trade")
    short_sleep()

    # get accounts
    account_dropdown = driver.find_element(By.XPATH, '//*[@id="basic-example-small"]')
    account_dropdown.click()

    ul_element = driver.find_element(By.XPATH, '//*[@id="basic-example-small-list"]/ul')
    li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
    li_count = len(li_elements)

    print(li_count)

    for num in range(li_count):
        if num != 0:
            account_dropdown = driver.find_element(By.XPATH, '//*[@id="basic-example-small"]')
            account_dropdown.click()
        very_short_sleep()

        # click on account
        account_select = driver.find_element(By.ID, f'basic-example-small-header-0-account-{num}')
        account_select.click()
        very_short_sleep()

        # ticker search
        ticker_search = driver.find_element(By.XPATH, '//*[@id="_txtSymbol"]')
        human_type(ticker, ticker_search)
        very_short_sleep()
        ticker_search.send_keys(Keys.ENTER)
        short_sleep()

        action_button = driver.find_element(By.XPATH, '//*[@id="_action"]')
        action_button.click()
        very_short_sleep()

        select = Select(action_button)
        select.select_by_visible_text("Buy")
        very_short_sleep()

        # click review order
        review_order_button = driver.find_element(By.XPATH, '//*[@id="mcaio-footer"]/div/div[2]/button[2]')
        review_order_button.click()
        short_sleep()

        # check if limit is higher than current price
        try:
            xpath = "//*[contains(@id, 'mctorderdetail') and contains(@id, 'CHECKBOX_0')]"
            WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            higher_than_ask_checkbox = driver.find_element(By.XPATH, '//*[@id="mctorderdetailfbb8f5e5CHECKBOX_0"]')
            higher_than_ask_checkbox.click()
            print("Limit price is higher than actual, continuing with purchase...\n\n")
        except Exception as e:
            pass

        # place buy order
        submit_buy = driver.find_element(By.XPATH, '//*[@id="mtt-place-button"]')
        submit_buy.click()
        short_sleep()

        print(f"Order for '{ticker}' submitted!")

        # redirect
        driver.get("https://client.schwab.com/app/trade/tom/trade")
        short_sleep()

def sell(ticker, dir, prof):


    

