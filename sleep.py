import time
import random

def short_sleep():
    random_number = random.randint(1,3)
    time.sleep(random_number)

def rand_sleep():
    random_number = random.randint(5, 10)
    time.sleep(random_number)