from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.options.android import UiAutomator2Options
import time, unittest

capabilities_options = UiAutomator2Options()
capabilities_options.platform_name = 'Android'
capabilities_options.platform_version = '15'
capabilities_options.device_name = 'Android Emulator'
capabilities_options.app_package = 'com.android.settings'
capabilities_options.app_activity = '.Settings'
capabilities_options.language = 'en'
capabilities_options.locale = 'US'

appium_server_url = "http://localhost:4723"

class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(
            command_executor=appium_server_url,
            options=capabilities_options
        )

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test_navigate_settings(self):
        print("Navigating through Settings...")
        network_and_internet = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Network & internet"]'))
        )
        network_and_internet.click()
        time.sleep(2)
        self.driver.back()
        time.sleep(1)

if __name__ == '__main__':
    unittest.main()



# try:
#     wait = WebDriverWait(driver, 30)
    
#     # Example: Logging into the app
#     username_field = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.fidelity.android:id/username")))
#     username_field.send_keys("your_username")
    
#     password_field = driver.find_element(AppiumBy.ID, "com.fidelity.android:id/password")
#     password_field.send_keys("your_password")
    
#     login_button = driver.find_element(AppiumBy.ID, "com.fidelity.android:id/login_button")
#     login_button.click()
    
#     # Wait for login to complete
#     time.sleep(5)
    
#     # Example: Navigating to the trade section
#     trade_button = wait.until(EC.element_to_be_clickable((AppiumBy.ID, "com.fidelity.android:id/trade_button")))
#     trade_button.click()
    
#     # Example: Buying a stock
#     buy_button = wait.until(EC.element_to_be_clickable((AppiumBy.ID, "com.fidelity.android:id/buy_button")))
#     buy_button.click()
    
#     ticker_field = driver.find_element(AppiumBy.ID, "com.fidelity.android:id/ticker_input")
#     ticker_field.send_keys("AAPL")
    
#     quantity_field = driver.find_element(AppiumBy.ID, "com.fidelity.android:id/quantity_input")
#     quantity_field.send_keys("10")
    
#     submit_buy = driver.find_element(AppiumBy.ID, "com.fidelity.android:id/submit_buy")
#     submit_buy.click()
    
#     # Confirm the trade
#     confirm_button = wait.until(EC.element_to_be_clickable((AppiumBy.ID, "com.fidelity.android:id/confirm_button")))
#     confirm_button.click()
    
#     print("Trade executed successfully!")

# except Exception as e:
#     print(f"An error occurred: {e}")

# finally:
#     # Close the Appium session
#     driver.quit()
