import time
import random

def human_like():
    random_num = random.uniform(0.05,0.25)
    time.sleep(random_num)

def short_sleep():
    random_num = random.randint(3,4)
    time.sleep(random_num)

# MTF
def rand_sleep():
    random_num = random.randint(6, 9)
    time.sleep(random_num)

def long_sleep():
    random_num = random.randint(10,15)
    time.sleep(random_num)