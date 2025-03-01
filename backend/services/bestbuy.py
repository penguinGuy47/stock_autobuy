import os
import random
import time
from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)

# ----------------------------
# Helper: Random "human" actions
# ----------------------------
def random_human_actions(page, action_count=3):
    for _ in range(action_count):
        if not page.is_closed():
            action_type = random.choice(["mouse_move", "scroll"])
            if action_type == "mouse_move":
                x = random.randint(0, page.viewport_size["width"])
                y = random.randint(0, page.viewport_size["height"])
                page.mouse.move(x, y, steps=random.randint(5, 15))
            elif action_type == "scroll":
                scroll_amount = random.randint(-200, 200)
                page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            page.wait_for_timeout(random.randint(300, 1000))
        else:
            logger.info("Page closed—skipping human action.")
            break

# ----------------------------
# Helper: Type text with small random pauses
# ----------------------------
def human_type(page, text, selector):
    if not page.is_closed():
        input_box = page.locator(selector)
        input_box.click()
        page.wait_for_timeout(random.randint(200, 500))
        for char in text:
            input_box.press(char)
            time.sleep(random.uniform(0.05, 0.2))
    else:
        logger.info("Page closed—skipping typing.")

# ----------------------------
# Main function for BestBuy product automation
# ----------------------------
def run_product_automation(profile, sku):
    """
    Automates adding a product to the cart and proceeding to checkout on BestBuy.
    Assumes 'profile' is a dict with keys 'username' and 'password'.
    'sku' is the product SKU (provided via the billing field from the Products modal).
    """
    # Use a session file based on the username for persistence.
    session_file = f"{profile['username']}_bestbuy_session.json"
    email = profile['username']
    password = profile['password']
    
    with sync_playwright() as p:
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        try:
            if os.path.exists(session_file):
                logger.info(f"[{email}] Loading session from {session_file}")
                context = browser.new_context(
                    storage_state=session_file,
                    user_agent=user_agent,
                    viewport={"width": 1366, "height": 768},
                    screen={"width": 1366, "height": 768},
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-User": "?1",
                        "Sec-Fetch-Dest": "document",
                    }
                )
            else:
                logger.info(f"[{email}] No session found—creating new context.")
                context = browser.new_context(
                    user_agent=user_agent,
                    viewport={"width": 1366, "height": 768},
                    screen={"width": 1366, "height": 768},
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-User": "?1",
                        "Sec-Fetch-Dest": "document",
                    }
                )

            page = context.new_page()

            page.add_init_script(script="""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type) {
                    const ctx = originalGetContext.call(this, type);
                    if (type === '2d') {
                        const originalFillText = ctx.fillText;
                        ctx.fillText = function(...args) {
                            const x = args[1] + (Math.random() - 0.5) * 0.1;
                            originalFillText.call(this, args[0], x, args[2]);
                        };
                    }
                    return ctx;
                };
            """)

            # Navigate to BestBuy home and check if already signed in.
            page.goto("https://www.bestbuy.com/", timeout=30000)
            random_human_actions(page, action_count=3)

            try:
                page.wait_for_timeout(2000)
                signed_in = page.evaluate('document.body.innerText.includes("Hi,")')
                if signed_in:
                    logger.info(f"[{email}] Already signed in—skipping login.")
                else:
                    raise Exception("Not signed in")
            except Exception:
                signed_in = False
                logger.info(f"[{email}] Not signed in—proceeding with login.")
                page.goto("https://www.bestbuy.com/identity/global/signin", timeout=10000)
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                random_human_actions(page, action_count=3)
                human_type(page, email, "input#fld-e")
                page.mouse.move(random.randint(600, 800), random.randint(400, 600), steps=10)
                page.wait_for_timeout(random.randint(300, 1000))
                page.click("button.cia-form__controls__submit[data-track='Sign In - Continue']", timeout=10000)
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                random_human_actions(page, action_count=2)
                page.wait_for_selector("text='Use password'", timeout=10000)
                page.mouse.move(random.randint(200, 400), random.randint(300, 500), steps=10)
                page.wait_for_timeout(random.randint(400, 900))
                page.click("text='Use password'")
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                human_type(page, password, "input#fld-p1")
                page.wait_for_timeout(random.randint(500, 1200))
                view_password_selector = "#show-hide-password-toggle"
                if not page.is_closed() and page.query_selector(view_password_selector):
                    page.mouse.move(random.randint(700, 900), random.randint(500, 700), steps=10)
                    page.wait_for_timeout(random.randint(300, 800))
                    page.click(view_password_selector)
                    page.wait_for_timeout(random.randint(300, 800))
                    page.click(view_password_selector)
                if not page.is_closed():
                    page.mouse.move(random.randint(700, 900), random.randint(500, 700), steps=10)
                    page.wait_for_timeout(random.randint(300, 800))
                    page.click("button.cia-form__controls__submit", timeout=10000)
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                try:
                    if not page.is_closed() and page.query_selector("button.cia-form__controls__submit"):
                        page.wait_for_timeout(random.randint(300, 800))
                        page.click("button.cia-form__controls__submit", timeout=2000)
                        logger.info(f"[{email}] Clicked 'Continue' on welcome back page.")
                except Exception:
                    pass
                try:
                    if not page.is_closed():
                        page.wait_for_timeout(2000)
                        signed_in = page.evaluate('document.body.innerText.includes("Hi,")')
                        if signed_in:
                            logger.info(f"[{email}] Signed in successfully.")
                            context.storage_state(path=session_file)
                            logger.info(f"[{email}] Session saved to {session_file}")
                        else:
                            logger.info(f"[{email}] Failed to verify login—session not saved.")
                    else:
                        logger.info(f"[{email}] Page closed—failed to verify login.")
                except Exception as e:
                    logger.info(f"[{email}] Failed to verify login: {e}")

            if not page.is_closed():
                random_human_actions(page, action_count=2)
                # Navigate to product page using the provided SKU
                url = f"https://www.bestbuy.com/site/{sku}.p?skuId={sku}"
                logger.info(f"[{email}] Navigating to: {url}")
                page.goto(url, timeout=30000, wait_until="commit")
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                page.wait_for_timeout(random.randint(1000, 3000))
                random_human_actions(page, action_count=2)
                primary_selector = "button[data-test-id='add-to-cart']"
                fallback_selector = f"button.add-to-cart-button[data-sku-id='{sku}'][data-button-state='ADD_TO_CART']"
                max_attempts = 3
                button_clicked = False
                for attempt in range(max_attempts):
                    try:
                        if not page.is_closed():
                            logger.info(f"[{email}] Waiting for 'Add to Cart' button for SKU {sku} (attempt {attempt + 1}/{max_attempts})...")
                            button = page.query_selector(primary_selector)
                            if not button:
                                logger.info(f"[{email}] Primary selector '{primary_selector}' not found, trying fallback...")
                                button = page.query_selector(fallback_selector)
                            if button:
                                button.scroll_into_view_if_needed()
                                page.wait_for_timeout(random.randint(500, 1500))
                                button_text = button.inner_text().lower()
                                sku_id = button.get_attribute("data-sku-id") or "N/A"
                                logger.info(f"[{email}] Button found - Text: {button_text}, SKU-ID: {sku_id}")
                                if "add to cart" in button_text:
                                    page_sku = page.query_selector(f"[data-sku-id='{sku}']")
                                    if page_sku or sku_id == sku or sku_id == "N/A":
                                        button.click()
                                        logger.info(f"[{email}] Clicked 'Add to Cart' for SKU {sku}.")
                                        page.wait_for_timeout(1000)
                                        button_clicked = True
                                        break
                                    else:
                                        logger.info(f"[{email}] Button found, but SKU mismatch (expected {sku}, got {sku_id}).")
                                else:
                                    logger.info(f"[{email}] Button found but not 'Add to Cart' (text: {button_text}).")
                            else:
                                logger.info(f"[{email}] No 'Add to Cart' button found.")
                        else:
                            logger.info(f"[{email}] Page closed—skipping add to cart.")
                            break
                    except Exception as e:
                        logger.info(f"[{email}] Button interaction failed (attempt {attempt + 1}/{max_attempts}): {e}")
                    if not button_clicked and attempt < max_attempts - 1:
                        wait_time = random.randint(3000, 5000)
                        logger.info(f"[{email}] Waiting for {wait_time} ms before refreshing the page.")
                        page.wait_for_timeout(wait_time)
                        logger.info(f"[{email}] Refreshing the page for next attempt.")
                        page.reload(wait_until="domcontentloaded", timeout=15000)
                        random_human_actions(page, action_count=2)
                # Go to cart and attempt checkout
                if not page.is_closed():
                    page.goto("https://www.bestbuy.com/cart", timeout=10000)
                    logger.info(f"[{email}] Navigated to cart.")
                    random_human_actions(page, action_count=1)
                    try:
                        if not page.is_closed():
                            page.click("button[data-track='Checkout - Top']", timeout=10000)
                            logger.info(f"[{email}] Clicked checkout.")
                    except Exception as e:
                        logger.info(f"[{email}] Checkout failed: {e}")
                    if not page.is_closed():
                        page.wait_for_timeout(5000)
                else:
                    logger.info(f"[{email}] Page closed—stopping automation.")
            else:
                logger.info(f"[{email}] Page closed—stopping automation.")
            return {'status': 'success', 'message': f'Product automation completed for SKU {sku}.'}
        except Exception as e:
            logger.error(f"[{email}] Error during BestBuy automation: {e}")
            return {'status': 'failure', 'message': f'Failed to automate product for SKU {sku}.', 'error': str(e)}
        finally:
            if 'browser' in locals() and browser.is_connected():
                browser.close()
