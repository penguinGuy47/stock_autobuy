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
import os

# for typing
def human_like():
    random_num = random.uniform(0.05,0.25)
    time.sleep(random_num)

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