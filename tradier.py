from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import time
import sleep

# ticker = input("Please enter the ticker you are buying: ")
ticker = 'QMCO'

driver = webdriver.Chrome(service=Service("chromedriver.exe"))
driver.get("https://www.tradier.com/")
wait = WebDriverWait(driver, 10)

login_button = driver.find_element(By.XPATH, "//a[contains(@class, 'ml-8') and contains(text(), 'Login')]")
login_button.click()

username="kash0440"
login_field = driver.find_element(By.NAME, "username")
for char in username:
    login_field.send_keys(char)
    time.sleep(0.1) 

pw="Jcpledd123?"
pw_field = driver.find_element(By.NAME, "password")
for char in pw:
    pw_field.send_keys(char)
    time.sleep(0.1) 

sleep.short_sleep()

sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(),'Sign In')]")
sign_in_button.click()

sleep.rand_sleep()
current_url = driver.current_url
sleep.short_sleep()

if "https://dash.tradier.com/dashboard" in current_url:
    print("Logged into Tradier!")
else:
    input("Please complete 2FA if requested and then press Enter to continue...")

sleep.rand_sleep()

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
    EC.visibility_of_element_located((By.NAME, 'side'))
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

preview_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div/div/div[1]/div[2]/div[1]/div[1]/form/div[2]/div/div/button[2]')
preview_button.click()

sleep.short_sleep()

submit_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div/div/div[1]/div[2]/div[1]/div[1]/form/div[2]/div/div/button[3]')
submit_button.click()

print('Order successfully placed for "' +ticker+ '" on Tradier!')

time.sleep(20)

driver.quit()