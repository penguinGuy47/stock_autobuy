import time
import random

def human_like():
    random_number = random.uniform(0.1,0.3)
    time.sleep(random_number)

def short_sleep():
    random_number = random.randint(3,4)
    time.sleep(random_number)

def rand_sleep():
    random_number = random.randint(6, 10)
    time.sleep(random_number)