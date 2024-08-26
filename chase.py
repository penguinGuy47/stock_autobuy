from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import sleep
import time

driver = webdriver.Chrome(service=Service("chromedriver.exe"))
driver.get("https://www.chase.com/")
wait = WebDriverWait(driver, 10)

ticker = 'GME'

# sign in field
try:
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    
    # Switch to the iframe that contains the login form using its id or name attribute
    driver.switch_to.frame("logonbox")
    print("Switched to the iframe.")

    sleep.rand_sleep()

    username_field = driver.execute_script('return document.querySelector("#userId").shadowRoot.querySelector("#userId-input")')
    driver.execute_script('arguments[0].click();', username_field)
    username='kliang9228'
    for char in username:
        username_field.send_keys(char)
        sleep.human_like()
    print("Username entered successfully.")

    sleep.short_sleep()

    pw_field = driver.execute_script('return document.querySelector("#password").shadowRoot.querySelector("#password-input")')
    driver.execute_script('arguments[0].click();', pw_field)
    pw = 'Jcpledd1'
    for char in pw:
        pw_field.send_keys(char)
        sleep.human_like()
    print("Password entered successfully.")

    checkbox = driver.execute_script(
        "var checkbox = document.querySelector('mds-checkbox#rememberMe'); checkbox.setAttribute('state', 'true'); return checkbox;"
    )

    sleep.rand_sleep()

    signin = driver.execute_script('return document.querySelector("#signin-button").shadowRoot.querySelector("button")')
    driver.execute_script('arguments[0].click();', signin)

except Exception as e:
    print(f"An error occurred: {e}")

input("Please complete any necessary actions (e.g., 2FA) and press Enter to continue...")
print("Logged into Chase!")

sleep.rand_sleep()

# select account and find ticker
account_select = driver.execute_script('return document.querySelector("#account-table-INVESTMENT").shadowRoot.querySelector("#row-header-row0-column0 > div > a > span")')
driver.execute_script('arguments[0].click();', account_select)

sleep.rand_sleep()

try:
    ticker_search = driver.execute_script('return document.querySelector("#quoteSearchLink").shadowRoot.querySelector("a")')
    driver.execute_script('arguments[0].click();', ticker_search)
    sleep.short_sleep()

    ticker_search = driver.execute_script('return document.querySelector("#typeaheadSearchTextInput").shadowRoot.querySelector("#typeaheadSearchTextInput-input")')
    driver.execute_script('arguments[0].click()', ticker_search)
    sleep.short_sleep()

    for char in ticker:
        ticker_search.send_keys(char)
        time.sleep(0.1) 
    sleep.short_sleep()
    ticker_search.send_keys(Keys.ENTER)
except Exception as e:
    print(f"An error occurred: {e}")

time.sleep(100000)

driver.quit()