from sleep import *

import time
import sleep

# TODO:
# add multi buy function
def buy(ticker):
    driver = webdriver.Chrome(service=Service("chromedriver.exe"))
    driver.get("https://www.tradier.com/")
    wait = WebDriverWait(driver, 10)

    # login
    login_button = driver.find_element(By.XPATH, "//a[contains(@class, 'ml-8') and contains(text(), 'Login')]")
    login_button.click()

    # ENTER YOUR CREDENTIALS
    username = ""   # ENTER YOUR USERNAME
    pw = ""         # ENTER YOUR PASSWORD

    login_field = driver.find_element(By.NAME, "username")
    for char in username:
        login_field.send_keys(char)
        time.sleep(0.1) 

    pw_field = driver.find_element(By.NAME, "password")
    for char in pw:
        pw_field.send_keys(char)
        time.sleep(0.1) 

    sleep.very_short_sleep()

    # sign in button
    sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(),'Sign In')]")
    sign_in_button.click()

    sleep.short_sleep()

    os.system('echo \a')
    input("Please complete 2FA if requested and then press Enter to continue...")
    print("Logged into Tradier!")

    # click dropdown to show accounts
    account_dropdown = driver.find_element(By.XPATH, '//*[@id="headlessui-menu-button-3"]/div')
    account_dropdown.click()

    # keep track of the accounts we have already bought on
    bought_accounts = set()

    while True:
        # obtain account buttons
        try:
            accounts = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="headlessui-menu-items-4"]/div[1]//button'))
            )

            for account in accounts:
                try:       
                    account_text = account.text.strip()

                    # skip if already processed
                    if account_text in bought_accounts:
                        print(f"Skipping account: {account_text}")
                        continue

                    # check for 'disabled' attr
                    account_id = account.get_attribute('id')
                    try:
                        current_account = None
                        if account.get_attribute('disabled') is None:
                            print("Switching account to purchase...")
                            account_id = account.get_attribute('id')
                            purchase_acc = wait.until(EC.element_to_be_clickable((By.ID, account_id)))
                            purchase_acc.click()
                            sleep.short_sleep()

                            # reopen dropdown to get account element
                            account_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="headlessui-menu-button-3"]/div')))
                            account_dropdown.click()

                    except:
                        pass

                    sleep.rand_sleep()

                    bought_accounts.add(account_text)
                    print('\n\n\nBought Account:')
                    print(bought_accounts)
                    print('\n\n\n')
        
                    sleep.short_sleep()

                    # buy operations
                    ticker_search = driver.find_element(By.NAME, "quote_module_symbol_search")
                    for char in ticker:
                        ticker_search.send_keys(char)
                        time.sleep(0.1) 

                    sleep.short_sleep()

                    ticker_search.send_keys(Keys.ENTER)

                    sleep.short_sleep()

                    trade_button = driver.find_element(By.XPATH, "//button[contains(@class, 'button') and contains(@class, 'success') and contains(@class, 'lg')]")
                    trade_button.click()

                    sleep.short_sleep()

                    buy_dropdown = wait.until(
                        EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/main/div/div/div[1]/div[2]/div[1]/div[1]/form/div[1]/div[1]/div[1]/label/div/select'))
                    )
                    buy_dropdown.click()
                    select = Select(buy_dropdown)
                    select.select_by_visible_text("Buy")

                    sleep.short_sleep()

                    # quantity of shares to purchase
                    quantity_field = wait.until(
                        EC.visibility_of_element_located((By.NAME, "quantity"))
                    )
                    quantity_field.send_keys("1")

                    # PREVIEW
                    sleep.very_short_sleep()
                    preview_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div/div/div[1]/div[2]/div[1]/div[1]/form/div[2]/div/div/button[2]')
                    preview_button.click()

                    # SUBMIT
                    # sleep.very_short_sleep()
                    # submit_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div/div/div[1]/div[2]/div[1]/div[1]/form/div[2]/div/div/button[3]')
                    # submit_button.click()

                    print(f'Order successfully placed for "{ticker}" on Tradier!')

                    sleep.short_sleep()

                    if len(bought_accounts) is len(accounts):
                        print("No more accounts to process.")
                        driver.quit()
                        exit()

                    # RELOAD
                    driver.get('https://dash.tradier.com/dashboard')
                    sleep.rand_sleep()

                    account_dropdown = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="headlessui-menu-button-3"]/div'))
                    )
                    account_dropdown.click()

                    break
                except Exception as e:
                    print(e)
                    continue

        except Exception as e:
            print(e)
            continue