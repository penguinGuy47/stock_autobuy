from sleep import *

# TODO:
# add login
# add buy
# add multi buy function
def buy(ticker):
    options = webdriver.ChromeOptions()
    # options.add_argument(r"user-data-dir=") # add path to your own Chrome
    # options.add_argument(r"--profile-directory=Profile 6") # change Profile 6 to your desired profile
    options.add_argument("--disable-blink-features=AutomationControlled")   # bypass automation protection
    driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
    # driver.get("https://digital.fidelity.com/prgw/digital/login/full-page")
    driver.get("https://digital.fidelity.com/ftgw/digital/portfolio/summary")
    wait = WebDriverWait(driver, 10)
    short_sleep()