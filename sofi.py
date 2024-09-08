from sleep import *

# TODO:
# add login
# add buy
# add account switching
# add multi buy function
def buy(ticker, dir, prof):
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={dir}")
    options.add_argument(f"--profile-directory={prof}") 
    options.add_argument("--disable-blink-features=AutomationControlled")   # bypass automation protection
    # user agent is required to bypass cloudflare bot protection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    # driver.get('https://www.sofi.com/')
    driver.get("https://login.sofi.com/u/login?state=hKFo2SBMaFhNak5SOHJMRUM3RlZGeHFGTjNFcmRXeElOVkY1bqFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIHV5bXFzQTZBZjdSaXM1X0VtLWdpSFY5OW1hUExJSFpko2NpZNkgNkxuc0xDc2ZGRUVMbDlTQzBDaWNPdkdlb2JvZXFab2I")
    wait = WebDriverWait(driver, 10)
    long_sleep()

    # ENTER YOUR CREDENTIALS
    email = ""   # ENTER YOUR EMAIL
    pw = ""         # ENTER YOUR PASSWORD

    # click on log in tab
    # login_tab = driver.find_element(By.XPATH, '//*[@id="main-nav-login-link"]')
    # login_tab.click()
    # short_sleep()

    email_field = driver.find_element(By.XPATH, '//*[@id="username"]')
    human_type(email, email_field)
    very_short_sleep()

    pw_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    human_type(pw, pw_field)
    very_short_sleep()

    login_button = driver.find_element(By.XPATH, '//*[@id="widget_block"]/div/div[2]/div/div/main/section/div/div/div/form/div[2]/button')
    login_button.click()
    short_sleep()

    os.system('echo \a')
    input("\n\nPlease complete 2FA if requested and then press Enter when you reach the dashboard...\n\n\n")
    print("Logged into Schwab!")
    short_sleep()

    invest_tab = driver.find_element(By.XPATH, '//*[@id="root"]/div/header/nav/div[3]/a[4]')
    invest_tab.click()
    short_sleep()



