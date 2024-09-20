from utils.sleep import *

import time

# User credentials
USERNAME = ""  # ENTER YOUR USERNAME
PASSWORD = ""  # ENTER YOUR PASSWORD

USERNAME = "kash0440"  # ENTER YOUR USERNAME
PASSWORD = "Jcpledd123?"  # ENTER YOUR PASSWORD

def buy(ticker, driver_path, profile_path):
    """
    Args:
        ticker (str): The stock ticker symbol to buy.
        driver_path (str): Path to the ChromeDriver executable.
        profile_path (str): Path to the Chrome user profile.
    """
    driver = None
    try:
        # Initialize WebDriver
        driver = start_regular_driver(driver_path, profile_path)
        driver.get("https://www.tradier.com/")
        wait = WebDriverWait(driver, 10)

        # Login process
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'ml-8') and contains(text(), 'Login')]"))
        )
        login_button.click()

        # Enter username
        login_field = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        login_field.clear()
        human_type(USERNAME, login_field)

        # Enter password
        pw_field = driver.find_element(By.NAME, "password")
        pw_field.clear()
        human_type(PASSWORD, pw_field)

        very_short_sleep()

        # Click sign in
        sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(),'Sign In')]")
        sign_in_button.click()

        short_sleep()

        # Audible alert and manual 2FA completion
        os.system('echo \a')
        input("\n\nPlease complete 2FA if requested and then press Enter when you reach the dashboard...\n\n\n")
        print("Logged into Tradier!")

        # Open account dropdown
        short_sleep()
        account_dropdown = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="headlessui-menu-button-3"]'))
        )
        account_dropdown.click()

        # Track processed accounts
        bought_accounts = set()

        while True:
            try:
                # Fetch all account buttons
                accounts = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, '//*[@id="headlessui-menu-items-4"]/div[1]//button'))
                )

                for account in accounts:
                    account_text = account.text.strip()

                    if account_text in bought_accounts:
                        print(f"Skipping account: {account_text}")
                        continue

                    if not account.get_attribute('disabled'):
                        print(f"Switching account to purchase on: {account_text}")
                        account.click()
                        short_sleep()

                        bought_accounts.add(account_text)
                        print(f'\n\n\nBought Account: {bought_accounts}\n\n\n')

                        # Execute buy operation
                        perform_buy(driver, ticker, wait)

                        # Check if all accounts have been processed
                        if len(bought_accounts) >= len(accounts):
                            print("No more accounts to process.")
                            return

                        # Reload dashboard for next account
                        driver.get('https://dash.tradier.com/dashboard')
                        rand_sleep()

                        # Reopen account dropdown
                        try:
                            account_dropdown = wait.until(
                                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/header/div/div[2]/div/div[3]/div/button'))
                            )
                            account_dropdown.click()
                        except Exception as e:
                            print("Failed to reopen account dropdown:", e)
                            return

            except Exception as e:
                print("Error while processing accounts:", e)
                continue

    except Exception as e:
        print("An unexpected error occurred:", e)
    finally:
        if driver:
            driver.quit()
            print("WebDriver has been closed.")

def perform_buy(driver, ticker, wait):
    """
    Perform the buy operation for a specified ticker.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.
        ticker (str): The stock ticker symbol to buy.
        wait (WebDriverWait): WebDriverWait instance for handling dynamic elements.
    """
    try:
        # Search for the ticker
        ticker_search = wait.until(
            EC.visibility_of_element_located((By.NAME, "quote_module_symbol_search"))
        )
        ticker_search.clear()
        human_type(ticker, ticker_search)
        short_sleep()
        ticker_search.send_keys(Keys.ENTER)
        short_sleep()

        # Click trade button
        trade_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'button') and contains(@class, 'success') and contains(@class, 'lg')]"))
        )
        trade_button.click()
        short_sleep()

        # Select 'Buy' from dropdown
        buy_dropdown = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/main/div/div/div[1]/div[2]/div[1]/div[1]/form/div[1]/div[1]/div[1]/label/div/select'))
        )
        select = Select(buy_dropdown)
        select.select_by_visible_text("Buy")
        short_sleep()

        # Enter quantity
        quantity_field = wait.until(
            EC.visibility_of_element_located((By.NAME, "quantity"))
        )
        quantity_field.clear()
        quantity_field.send_keys("1")

        # Preview order
        very_short_sleep()
        preview_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div/div/div[1]/div[2]/div[1]/div[1]/form/div[2]/div/div/button[2]')
        preview_button.click()

        # Submit order
        very_short_sleep()
        submit_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div/div/div[1]/div[2]/div[1]/div[1]/form/div[2]/div/div/button[3]')
        submit_button.click()

        print(f'Order successfully placed for "{ticker}" on Tradier!')
        short_sleep()

    except Exception as e:
        print(f"Failed to buy stock {ticker}: {e}")
        # Optionally, you can add more error handling or logging here