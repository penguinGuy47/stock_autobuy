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

import time
import random
import pickle
import os
import re

def restart_driver(driver):
    driver.quit()
    short_sleep()
    
    return start_headless_driver()

def human_type(word, destination):
    random_num = random.uniform(0.05,0.25)
    for char in word:
        destination.send_keys(char)
        time.sleep(random_num)

# for typing
def human_like():
    random_num = random.uniform(0.05,0.25)
    time.sleep(random_num)

# shortest waits
def very_short_sleep():
    random_num = random.randint(1,2)
    time.sleep(random_num)

# for short human-like waits
def short_sleep():
    random_num = random.randint(3,4)
    time.sleep(random_num)

# for medium time waiting
def rand_sleep():
    random_num = random.randint(6, 9)
    time.sleep(random_num)

# for longer waits
def long_sleep():
    random_num = random.randint(10,15)
    time.sleep(random_num)

def start_headless_driver(dir, prof):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument(f"user-data-dir={dir}")  # COMMENTED FOR 2FA TESTING
    # options.add_argument(f"--profile-directory={prof}")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
    options.add_argument("--window-size=1920,1080")  # standard desktop size window
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
    return driver

def start_regular_driver(dir, prof):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument(f"user-data-dir={dir}")  # COMMENTED FOR 2FA TESTING
    # options.add_argument(f"--profile-directory={prof}")
    options.add_argument("--disable-blink-features=AutomationControlled")  # prevent detection
    options.add_argument("--window-size=1920,1080")  # standard desktop size window
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
    return driver

def save_cookies(driver, path):
    with open(path, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

def load_cookies(driver, path):
    with open(path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        