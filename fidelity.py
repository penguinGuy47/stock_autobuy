from sleep import *

import sleep

# TODO:
# add multi buy function
def buy(ticker):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")   # bypass automation protection
    driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
    driver.get("https://digital.fidelity.com/prgw/digital/login/full-page")
    wait = WebDriverWait(driver, 10)
    sleep.short_sleep()

    # ENTER YOUR CREDENTIALS
    username = ""   # ENTER YOUR USERNAME
    pw = ""         # ENTER YOUR PASSWORD

    username_field = driver.find_element(By.XPATH, '//*[@id="dom-username-input"]')
    username_field.click()
    for char in username:
        username_field.send_keys(char)
        sleep.human_like()

    sleep.short_sleep()

    pw_field = driver.find_element(By.XPATH, '//*[@id="dom-pswd-input"]')
    for char in pw:
        pw_field.send_keys(char)
        sleep.human_like()

    sleep.rand_sleep()

    log_in_button = driver.find_element(By.XPATH, '//*[@id="dom-login-button"]')
    log_in_button.click()

    input("\n\nPlease complete 2FA if requested and then press Enter when you reach the dashboard...\n\n\n")
    print("\nLogin Successful\n")

    # search for ticker
    ticker_search = driver.find_element(By.XPATH, '//*[@id="fa-search-input"]')
    for char in ticker:
        ticker_search.send_keys(char)
        sleep.human_like()
    ticker_search.send_keys(Keys.ENTER)

    sleep.short_sleep()

    # click on buy
    buy_button = driver.find_element(By.XPATH, '//*[@id="res-exp-container"]/research-main/div/div/section[1]/quote/div/nre-quick-quote/div/div[1]/div[5]/div[1]/pvd3-button/s-root/button')
    buy_button.click()

    sleep.short_sleep()

    # click dropdown
    # account_dropdown = driver.find_element(By.XPATH, '//*[@id="dest-acct-dropdown"]')
    # account_dropdown.click()

    sleep.very_short_sleep()
    print("clicked dropdown")

    # account_select = driver.find_element(By.XPATH, '//*[@id="ett-acct-sel-list"]')
    # account_select.click()
    sleep.very_short_sleep()
    driver.execute_script("document.getElementById('dest-acct-dropdown').click();")

    print("selecting account")
    sleep.short_sleep()

    ul_element = driver.find_element(By.XPATH, '//*[@id="ett-acct-sel-list"]/ul')
    li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

    # Count the number of <li> elements
    li_count = len(li_elements)

    account_select = driver.find_element(By.XPATH, '//*[@id="account0"]')
    account_select.click()

    print(f"Number of <li> elements: {li_count}")

    time.sleep(10000)

    