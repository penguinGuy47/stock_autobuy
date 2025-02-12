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
import shutil
import tempfile
import logging
import uuid

chromedriver_path = os.path.join(os.path.dirname(__file__), "../../drivers/chromedriver.exe")

def restart_driver(driver):
    driver.quit()
    short_sleep()
    
    return start_headless_driver()

def human_type(word, destination):
    random_num = random.uniform(0.05,0.25)
    for char in word:
        destination.send_keys(char)
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

def start_headless_driver(dir=None, prof=None):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new") NEED THIS FOR FIDELITY
    options.add_argument("--headless=old")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")
    # options.add_argument("--window-position=-2400,-2400")      #Chromium 129 bug

    # Create a temporary directory for user-data-dir
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f"user-data-dir={temp_dir}")

    # Initialize ChromeDriver using webdriver-manager
    driver = webdriver.Chrome(options=options, service=Service(chromedriver_path))
    return driver, temp_dir

def start_regular_driver(dir=None, prof=None):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--enable-unsafe-swiftshader")
    # options.add_argument("--incognito")  # Open browser in incognito mode for testing
    options.add_argument("--disable-cookies")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument("--disable-web-security")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")
    
    # FOR TESTING
    # brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    # options.binary_location = brave_path

    # Create a temporary directory for user-data-dir
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f"user-data-dir={temp_dir}")

    # Initialize ChromeDriver using webdriver-manager
    driver = webdriver.Chrome(options=options, service=Service(chromedriver_path))
    
    return driver, temp_dir

def save_cookies(driver, path):
    with open(path, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

def load_cookies(driver, path):
    with open(path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        