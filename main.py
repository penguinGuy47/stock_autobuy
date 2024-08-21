from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import time

driver = webdriver.Chrome(service=Service("chromedriver.exe"))

driver.get("https://www.tradier.com/")

wait = WebDriverWait(driver, 10)

login_button = driver.find_element(By.XPATH, "//a[contains(@class, 'ml-8') and contains(text(), 'Login')]")

# Click the "Login" button
login_button.click()

username="minc8088"

login_field = driver.find_element(By.NAME, "username")
for char in username:
    login_field.send_keys(char)
    time.sleep(0.1) 

pw="Jcpledd123?"
pw_field = driver.find_element(By.NAME, "password")
for char in pw:
    pw_field.send_keys(char)
    time.sleep(0.1) 

time.sleep(5)

sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(),'Sign In')]")
sign_in_button.click()

time.sleep(10)

driver.quit()