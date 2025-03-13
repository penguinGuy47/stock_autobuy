from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException

import time
import random
import pickle
import os
import shutil
import tempfile
import logging
import uuid
import math
import numpy as np
import platform

logger = logging.getLogger(__name__)

chromedriver_path = os.path.join(os.path.dirname(__file__), "../../drivers/chromedriver.exe")

# Utility Functions
def restart_driver(driver):
    driver.quit()
    short_sleep()
    return start_headless_driver()

def human_type(word, destination):
    """Simulate human-like typing--no typos."""
    random_num = random.uniform(0.05, 0.25)
    for char in word:
        destination.send_keys(char)
        time.sleep(random_num)

# Sleep Functions
def very_short_sleep():
    time.sleep(random.uniform(0.1, 0.5))

def short_sleep():
    time.sleep(random.uniform(1, 3))

def medium_sleep():
    time.sleep(random.uniform(3, 7))

def long_sleep():
    time.sleep(random.uniform(7, 15))

# New Functionality: Random Mouse Movements
def random_mouse_movements(driver, num_movements=3):
    """Simulate random mouse movements to appear more human-like"""
    try:
        # Create a small JavaScript snippet to move the mouse randomly
        for _ in range(num_movements):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            script = f"var e = document.createEvent('MouseEvents'); e.initMouseEvent('mousemove', true, true, window, 0, 0, 0, {x}, {y}, false, false, false, false, 0, null); document.dispatchEvent(e);"
            driver.execute_script(script)
            very_short_sleep()
    except:
        # Ignore errors in mouse movement simulation
        pass

# New Functionality: Disguise Automation
def disguise_automation(driver):
    """Add various disguises to make the browser appear more human-like"""
    try:
        # Add random variables that automated detection checks for
        driver.execute_script("""
        // Add random screen dimensions
        Object.defineProperty(window.screen, 'width', { value: """ + str(random.choice([1366, 1440, 1536, 1920, 2560])) + """ });
        Object.defineProperty(window.screen, 'height', { value: """ + str(random.choice([768, 900, 864, 1080, 1440])) + """ });
        
        // Add random browser plugins
        Object.defineProperty(navigator, 'plugins', { 
            get: function() { 
                return { length: """ + str(random.randint(3, 10)) + """ };
            }
        });
        
        // Add random languages
        Object.defineProperty(navigator, 'languages', { 
            get: function() { 
                return ['en-US', 'en'];
            }
        });
        
        // Add consistent webdriver properties
        Object.defineProperty(navigator, 'webdriver', { value: false });
        """)
    except:
        # Ignore errors in disguise application
        pass

# Expanded User Agents List
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 14; Mobile; rv:123.0) Gecko/123.0 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.2365.80"
]

def start_headless_driver():
    """
    Start a headless Chrome browser with maximum compatibility settings
    Returns the webdriver instance and temporary directory path
    """
    # Create a temporary directory for Chrome user data
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Configure Chrome options for maximum stability
        chrome_options = Options()
        
        # Add headless mode options
        chrome_options.add_argument("--headless=new")  # New headless mode
        
        # User agent - use a recent mainstream one
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        chrome_options.add_argument(f"--user-agent={user_agent}")
        logger.info(f"Using User-Agent: {user_agent}")
        
        # Critical stability options
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, REQUIRED for some environments
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")  # Use temporary directory
        chrome_options.add_argument("--disable-extensions")  # Disable extensions for cleaner environment
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        chrome_options.add_argument("--disable-software-rasterizer")  
        chrome_options.add_argument("--window-size=1920,1080")  
        chrome_options.add_argument("--disable-notifications")  
        chrome_options.add_argument("--mute-audio") 
        # Fix SSL handshake issues
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--allow-insecure-localhost")
        chrome_options.add_argument("--disable-web-security")

        # Add crash handling
        chrome_options.add_argument("--disable-crash-reporter")
        chrome_options.add_argument("--disable-in-process-stack-traces")
        
        # Add memory options for stability
        chrome_options.add_argument("--disable-features=NetworkService")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Platform-specific settings
        system = platform.system().lower()
        if system == "windows":
            chrome_options.add_argument("--disable-features=WindowsD3DAdapter")
        
        # Create a new Chrome driver
        service = Service()  # Let it auto-detect the chromedriver path
        
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set page load timeout
            driver.set_page_load_timeout(30)
            
            # Set script timeout 
            driver.set_script_timeout(30)
            
            logger.info("Chrome webdriver started successfully")
            return driver, temp_dir
            
        except Exception as e:
            # Try alternative method with binary specification if we fail
            logger.warning(f"First attempt to start Chrome failed: {str(e)}")
            
            if system == "windows":
                # Try with explicit Chrome path for Windows
                chrome_binary_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
                
                for path in chrome_binary_paths:
                    if os.path.exists(path):
                        logger.info(f"Trying with explicit Chrome path: {path}")
                        chrome_options.binary_location = path
                        try:
                            driver = webdriver.Chrome(service=service, options=chrome_options)
                            logger.info("Chrome webdriver started with explicit binary path")
                            return driver, temp_dir
                        except Exception as inner_e:
                            logger.warning(f"Failed with explicit path {path}: {str(inner_e)}")
                
            logger.error(f"All attempts to start Chrome webdriver failed")
            raise
            
    except Exception as e:
        # Clean up the temporary directory and re-raise the exception
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        logger.error(f"Error starting Chrome webdriver: {str(e)}")
        raise

def start_regular_driver(dir=None, prof=None):
    options = webdriver.ChromeOptions()
    user_agent = random.choice(user_agents)
    logger.info(f"Using User-Agent: {user_agent}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument("--disable-cookies")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument("--disable-web-security")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f"user-data-dir={temp_dir}")

    driver = webdriver.Chrome(options=options, service=Service(chromedriver_path))
    disguise_automation(driver)
    return driver, temp_dir

def save_cookies(driver, path):
    with open(path, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

def load_cookies(driver, path):
    with open(path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)

def natural_mouse_movement(driver, start_element=None, end_element=None, duration=0.5):
    """Simulate human-like mouse movement with robust error handling."""
    actions = ActionChains(driver)
    
    try:
        # Reset action chains to clear any previous actions
        actions = ActionChains(driver)
        
        # Get browser window size with safety margin
        window_width = driver.execute_script("return window.innerWidth") - 10
        window_height = driver.execute_script("return window.innerHeight") - 10
        
        # If end_element is provided, ensure it's visible first
        if end_element:
            try:
                # Scroll element into view - center it to avoid edge issues
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'center', behavior: 'smooth'});", 
                    end_element
                )
                # Small wait for scrolling to complete
                time.sleep(0.3)
            except Exception as e:
                logger.warning(f"Couldn't scroll to element: {e}")
        
        # SIMPLIFIED APPROACH: Instead of complex paths, use direct movements with JS fallbacks
        if end_element:
            try:
                # Try direct Selenium move_to_element (most reliable)
                actions.move_to_element(end_element).perform()
                
                # If it's supposed to click, do that
                if random.random() < 0.8:  # 80% chance to click
                    try:
                        actions.click().perform()
                    except Exception as e:
                        logger.warning(f"Click failed: {e}")
                        # Fallback to JS click
                        driver.execute_script("arguments[0].click();", end_element)
                
                return  # Success! Exit the function
            except Exception as e:
                logger.warning(f"Direct element movement failed: {e}")
                
                # FALLBACK 1: Try getting element coordinates and move there
                try:
                    # Get element coordinates
                    rect = driver.execute_script("""
                        const rect = arguments[0].getBoundingClientRect();
                        return {
                            x: rect.left + rect.width/2,
                            y: rect.top + rect.height/2,
                            width: rect.width,
                            height: rect.height
                        };
                    """, end_element)
                    
                    # Ensure coordinates are within bounds
                    target_x = min(max(10, rect['x']), window_width - 10)
                    target_y = min(max(10, rect['y']), window_height - 10)
                    
                    # Try absolute positioning (more reliable than relative)
                    driver.execute_script(f"""
                        const event = new MouseEvent('mousemove', {{
                            'view': window,
                            'bubbles': true,
                            'cancelable': true,
                            'clientX': {target_x},
                            'clientY': {target_y}
                        }});
                        document.elementFromPoint({target_x}, {target_y}).dispatchEvent(event);
                    """)
                    
                    # If click needed, use JavaScript
                    if random.random() < 0.8:
                        driver.execute_script("arguments[0].click();", end_element)
                    
                    return  # Success with fallback, exit function
                except Exception as e:
                    logger.warning(f"Coordinate-based movement failed: {e}")
                    
                    # FALLBACK 2: Last resort - direct JavaScript click with no mouse movement
                    try:
                        driver.execute_script("arguments[0].click();", end_element)
                        logger.info("Used direct JavaScript click as last resort")
                        return
                    except Exception as e:
                        logger.error(f"All movement methods failed: {e}")
                        return
        else:
            # No specific element target - just move mouse to a safe random position
            safe_x = random.randint(50, window_width - 50)
            safe_y = random.randint(50, window_height - 50)
            
            try:
                # Move to absolute position (safer than offsets)
                driver.execute_script(f"""
                    const event = new MouseEvent('mousemove', {{
                        'view': window,
                        'bubbles': true,
                        'cancelable': true,
                        'clientX': {safe_x},
                        'clientY': {safe_y}
                    }});
                    document.elementFromPoint({safe_x}, {safe_y}).dispatchEvent(event);
                """)
            except Exception as e:
                logger.warning(f"Random mouse movement failed: {e}")
                # No fallback needed if this is just random movement
    
    except Exception as e:
        logger.warning(f"Mouse movement completely failed: {e}")
        # If there's an end element, try the direct click as a last resort
        if end_element:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", end_element)
                driver.execute_script("arguments[0].click();", end_element)
            except:
                pass

def enhance_fingerprint_protection(driver):
    """Add protection against various fingerprinting techniques"""
    # Canvas, WebGL, AudioContext fingerprinting protection
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            // Canvas fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                if (this.width > 16 && this.height > 16) {
                    const ctx = this.getContext('2d');
                    const imageData = ctx.getImageData(0, 0, this.width, this.height);
                    const data = imageData.data;
                    
                    // Add subtle noise to canvas data
                    for (let i = 0; i < data.length; i += 4) {
                        data[i] = data[i] + (Math.random() * 4 - 2);     // red
                        data[i+1] = data[i+1] + (Math.random() * 4 - 2); // green
                        data[i+2] = data[i+2] + (Math.random() * 4 - 2); // blue
                    }
                    
                    ctx.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, arguments);
            };
            
            // WebGL fingerprinting
            const getParameterProxyHandler = {
                apply: function(target, gl, args) {
                    const param = args[0];
                    
                    // Add noise to certain WebGL parameters
                    if (param === 37445) { // MAX_VERTEX_UNIFORM_VECTORS
                        return target.apply(gl, args) + Math.floor(Math.random() * 5);
                    }
                    if (param === 3379) { // MAX_TEXTURE_SIZE
                        return target.apply(gl, args) - Math.floor(Math.random() * 100);
                    }
                    
                    return target.apply(gl, args);
                }
            };
            
            // Apply WebGL proxy if WebGL is available
            if (typeof WebGLRenderingContext !== 'undefined') {
                WebGLRenderingContext.prototype.getParameter = new Proxy(
                    WebGLRenderingContext.prototype.getParameter,
                    getParameterProxyHandler
                );
            }
            
            // Hardware concurrency and device memory
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => Math.min(8, navigator.hardwareConcurrency || 4)
            });
            
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => Math.min(8, navigator.deviceMemory || 4)
            });
        '''
    })

def realistic_typing(text, element, error_probability=0.01, correction=True):
    """
    More realistic typing with variable speeds based on character pairs,
    occasional errors, and human-like correction behavior.
    """
    # Reduce base typing speed
    base_delay = random.uniform(0.02, 0.08)  # Was 0.05-0.15
    
    # Common typing speed variations by character pairs (simplified)
    slow_pairs = ['th', 'ch', 'ph', 'wh', 'qu', 'tr']
    fast_pairs = ['er', 'on', 'an', 'in', 'es', 'en']
    
    # Typing flow variables
    flow_state = random.random()  # How "in the flow" the typist is
    previous_char = None
    
    for i, char in enumerate(text):
        # Check for potential error
        make_error = random.random() < error_probability
        
        if make_error and correction:
            # Type wrong character
            wrong_chars = 1 if random.random() < 0.8 else 2  # Sometimes 2 wrong chars
            for _ in range(wrong_chars):
                # Choose wrong character (often adjacent on keyboard)
                keyboard_row = "qwertyuiop asdfghjkl zxcvbnm"
                if char.lower() in keyboard_row:
                    char_idx = keyboard_row.find(char.lower())
                    radius = 1 if random.random() < 0.6 else 2
                    start_idx = max(0, char_idx - radius)
                    end_idx = min(len(keyboard_row), char_idx + radius + 1)
                    wrong_char = random.choice(keyboard_row[start_idx:end_idx].replace(" ", ""))
                else:
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Delete wrong characters
            for _ in range(wrong_chars):
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.1, 0.2))
            
            # Brief pause after correction
            time.sleep(random.uniform(0.2, 0.5))
        
        # Calculate typing delay for this character
        delay = base_delay
        
        # Adjust for character context
        if previous_char and previous_char + char in slow_pairs:
            delay *= random.uniform(1.1, 1.5)  # Slow down for difficult combinations
        elif previous_char and previous_char + char in fast_pairs:
            delay *= random.uniform(0.7, 0.9)  # Speed up for common combinations
        
        # Adjust for typing flow (gradually changes)
        flow_state += random.uniform(-0.1, 0.1)
        flow_state = max(0.7, min(1.3, flow_state))  # Keep within reasonable bounds
        delay *= flow_state
        
        # Specific character adjustments
        if char.isupper() or char in '@#$%^&*()_+{}|:"<>?~':
            delay *= random.uniform(1.2, 1.5)  # Slow down for uppercase and special chars
        elif char == ' ':
            delay *= random.uniform(0.8, 1.2)  # Variable space timing
        
        # Type the character
        element.send_keys(char)
        time.sleep(delay)
        previous_char = char
        
        # Occasional pause while typing (thinking, distraction)
        if random.random() < 0.02:  # 2% chance of pause
            time.sleep(random.uniform(0.5, 1.5))
