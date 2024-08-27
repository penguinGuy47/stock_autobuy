from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

import sleep
import time

driver = webdriver.Chrome(service=Service("chromedriver.exe"))
driver.get("https://www.chase.com/")
wait = WebDriverWait(driver, 10)

ticker = 'XCUR'

sleep.short_sleep()
# sign in field
try:
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    
    # Switch to the iframe using its id or name
    driver.switch_to.frame("logonbox")
    print("Switched to the iframe.")

    username_field = driver.execute_script('return document.querySelector("#userId").shadowRoot.querySelector("#userId-input")')
    driver.execute_script('arguments[0].click();', username_field)
    username='user'
    for char in username:
        username_field.send_keys(char)
        sleep.human_like()

    sleep.short_sleep()

    pw_field = driver.execute_script('return document.querySelector("#password").shadowRoot.querySelector("#password-input")')
    driver.execute_script('arguments[0].click();', pw_field)
    pw = 'pw'
    for char in pw:
        pw_field.send_keys(char)
        sleep.human_like()

    # click remember me box
    checkbox = driver.execute_script(
        "var checkbox = document.querySelector('mds-checkbox#rememberMe'); checkbox.setAttribute('state', 'true'); return checkbox;"
    )

    sleep.short_sleep()

    signin = driver.execute_script('return document.querySelector("#signin-button").shadowRoot.querySelector("button")')
    driver.execute_script('arguments[0].click();', signin)

except Exception as e:
    print(f"An error occurred: {e}")

input("\n\nPlease complete 2FA if requested and then press Enter when you reach the dashboard...\n\n")
print("Logged into Chase!")

sleep.short_sleep()

# select account and find ticker
account_select = driver.execute_script('return document.querySelector("#account-table-INVESTMENT").shadowRoot.querySelector("#row-header-row0-column0 > div > a > span")')
driver.execute_script('arguments[0].click();', account_select)

sleep.short_sleep()

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

sleep.long_sleep()
iframes = driver.find_elements(By.TAG_NAME, "iframe")
    
# Switch to the iframe
driver.switch_to.frame("quote-markit-thirdPartyIFrameFlyout")
print("Switched to the iframe.")
try:
    close_button = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='close-add-market-alert-notification']"))
    )
    # If found, click the button
    close_button.click()
    sleep.rand_sleep()
except TimeoutException:
    print("Continuing with buy...")

# purchase ticker
trade_button = driver.find_element(By.XPATH, '//*[@id="quote-header-trade-button"]')
trade_button.click()

sleep.rand_sleep()
driver.switch_to.default_content()

# action (buy/sell)
buy_button = driver.find_element(By.XPATH, '//*[@id="orderAction-segmentedButtonInput-0"]')
buy_button.click()

sleep.short_sleep()

# dropdown order type
order_type_dropdown = driver.execute_script('return document.querySelector("#orderTypeDropdown").shadowRoot.querySelector("#select-orderTypeDropdown")')
driver.execute_script('arguments[0].click();', order_type_dropdown)

sleep.short_sleep()

market_order = driver.find_element(By.XPATH, '//*[@id="orderTypeDropdown"]/mds-select-option[1]')
market_order.click()

sleep.short_sleep()

share_qty = driver.execute_script('return document.querySelector("#orderQuantity").shadowRoot.querySelector("#orderQuantity-input")')
driver.execute_script('arguments[0].click();', share_qty)
sleep.short_sleep()
share_qty.send_keys("1")

sleep.short_sleep()

preview_button = driver.execute_script('return document.querySelector("#previewButton").shadowRoot.querySelector("button")')
driver.execute_script('arguments[0].click();', preview_button)

sleep.short_sleep()

place_order_button = driver.execute_script('return document.querySelector("#orderPreviewContent > div.order-preview-section.mds-pt-4 > div > mds-button").shadowRoot.querySelector("button")')
driver.execute_script('arguments[0].click();', place_order_button)

print("Order placed successfully on Chase!")

time.sleep(100000)

driver.quit()