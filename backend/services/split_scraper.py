import requests
from bs4 import BeautifulSoup
import re
import yfinance as yf
from dateutil import parser
from datetime import datetime, timedelta
import time
import random
import os
import json
import logging
from utils.sleep import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File path for storing cached data
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'split_scraper_cache.json')
# File path for storing symbols without news data
NO_NEWS_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'split_scraper_no_news_cache.json')

# Function to save scraped data to cache file
def save_split_data(data):
    """Save the scraped data to a cache file"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully saved {len(data)} items to cache file")
    except Exception as e:
        logger.error(f"Error saving data to cache file: {e}")

# Function to save symbols with no news data
def save_no_news_symbols(data):
    """Save symbols that don't have news data to a separate cache file"""
    try:
        with open(NO_NEWS_CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully saved {len(data)} items to no-news cache file")
    except Exception as e:
        logger.error(f"Error saving data to no-news cache file: {e}")

# Function to load cached data
def load_split_data():
    """Load previously scraped data from cache file"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} items from cache file")
            return data
        else:
            logger.info("No cache file found")
            return []
    except Exception as e:
        logger.error(f"Error loading data from cache file: {e}")
        return []

# Function to load symbols without news data
def load_no_news_symbols():
    """Load previously scraped symbols without news data"""
    try:
        if os.path.exists(NO_NEWS_CACHE_FILE):
            with open(NO_NEWS_CACHE_FILE, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} items from no-news cache file")
            return data
        else:
            logger.info("No no-news cache file found")
            return []
    except Exception as e:
        logger.error(f"Error loading data from no-news cache file: {e}")
        return []

# Function to clean old entries from both caches
def clean_old_entries(data, no_news_data):
    """Remove entries older than 7 days from both caches"""
    current_date = datetime.now()
    seven_days_ago = current_date - timedelta(days=7)
    
    # For main data
    recent_data = []
    for item in data:
        try:
            split_date = datetime.strptime(item['split_date'], '%Y-%m-%d')
            if split_date >= seven_days_ago:
                recent_data.append(item)
        except Exception:
            # Keep entries with invalid dates for now
            recent_data.append(item)
    
    # For no-news data
    recent_no_news = []
    for item in no_news_data:
        try:
            if 'scrape_date' in item:
                scrape_date = datetime.strptime(item['scrape_date'], '%Y-%m-%d')
                if scrape_date >= seven_days_ago:
                    recent_no_news.append(item)
            else:
                # Entries without scrape_date should be kept for backward compatibility
                recent_no_news.append(item)
        except Exception:
            # Keep entries with invalid dates for now
            recent_no_news.append(item)
    
    # If data was cleaned, save the cleaned versions
    if len(data) != len(recent_data):
        logger.info(f"Cleaned {len(data) - len(recent_data)} old entries from main cache")
    
    if len(no_news_data) != len(recent_no_news):
        logger.info(f"Cleaned {len(no_news_data) - len(recent_no_news)} old entries from no-news cache")
    
    return recent_data, recent_no_news

# Scrape Stock Analysis for reverse stock splits within the last 6 days
def scrape_stock_analysis(url, check_first_only=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Current date and date 6 days ago
    current_date = datetime.now()
    two_weeks_ago = current_date - timedelta(days=6)
    
    # Try with requests first (faster)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return []
        else:
            table_rows = table.find_all('tr')
            if len(table_rows) <= 1:  # Only header row or no rows
                return []
            else:
                reverse_splits = []
                
                for row in table_rows[1:]:  # Skip header
                    try:
                        columns = row.find_all(['td', 'th'])
                        if len(columns) < 4:  # Need at least date, ticker, type, action
                            continue
                            
                        date_str = columns[0].text.strip()
                        
                        try:
                            # Parse date with potential timezone but convert to naive for comparison
                            parsed_date = parser.parse(date_str)
                            # Convert to naive datetime for comparison if needed
                            if hasattr(parsed_date, 'tzinfo') and parsed_date.tzinfo is not None:
                                action_date = parsed_date.replace(tzinfo=None)
                            else:
                                action_date = parsed_date
                                
                            if action_date < two_weeks_ago:
                                continue  # Skip actions older than 6 days
                        except ValueError:
                            continue  # Skip rows with unparseable dates
                            
                        # Extract ticker symbol
                        symbol_elem = columns[1].find('a')
                        if symbol_elem:
                            symbol = symbol_elem.text.strip().upper()
                        else:
                            symbol = columns[1].text.strip().upper()
                            
                        # Check for split type
                        action_type = columns[2].text.strip().lower()
                        action_detail = columns[3].text.strip().lower()
                        
                        # Look for reverse splits - check for reverse in the type or details
                        if ('reverse' in action_type or 'reverse' in action_detail or 'consolidation' in action_detail) and ('split' in action_type or 'split' in action_detail):
                            try:
                                # Extract the ratio (usually in format "1 for X")
                                ratio_match = re.search(r'1:(\d+)', action_detail)
                                if not ratio_match:
                                    ratio_match = re.search(r'1 for (\d+)', action_detail)
                                if not ratio_match:
                                    ratio_match = re.search(r'1-for-(\d+)', action_detail)
                                    
                                if ratio_match:
                                    ratio = ratio_match.group(1)
                                    
                                    # Format the date consistently
                                    split_date = action_date.strftime('%Y-%m-%d')
                                    
                                    # Add to reverse splits list
                                    reverse_splits.append((symbol, split_date, ratio))
                                    
                                    # If we only need the first symbol, return immediately
                                    if check_first_only and reverse_splits:
                                        return reverse_splits
                            except Exception:
                                continue  # Skip on any parsing errors
                    except Exception:
                        continue  # Skip any row with processing errors
                
                if reverse_splits:
                    return reverse_splits
    except Exception as e:
        logger.error(f"Error scraping Stock Analysis with requests: {str(e)}")
    
    # Fallback to Selenium if requests approach fails or yields no results
    logger.info("Fallback to Selenium for Stock Analysis scraping...")
    try:
        driver, temp_dir = start_headless_driver()
        
        try:
            logger.info(f"Navigating to {url}")
            driver.get(url)
            
            # Wait for the table to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Simulate more human-like behavior
            random_mouse_movements(driver, 2)
            very_short_sleep()
            
            # Find the table
            table = driver.find_element(By.TAG_NAME, "table")
            
            # No table found
            if not table:
                driver.quit()
                return []
                
            # Get all rows
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            # No rows found
            if len(rows) <= 1:  # Just header row
                driver.quit()
                return []
                
            reverse_splits = []
            
            # Process each row (skip header)
            for row in rows[1:]:
                try:
                    # Get columns
                    columns = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(columns) < 4:
                        continue
                        
                    # Get date
                    date_str = columns[0].text.strip()
                    
                    try:
                        # Parse date with potential timezone but convert to naive for comparison
                        parsed_date = parser.parse(date_str)
                        # Convert to naive datetime for comparison if needed
                        if hasattr(parsed_date, 'tzinfo') and parsed_date.tzinfo is not None:
                            action_date = parsed_date.replace(tzinfo=None)
                        else:
                            action_date = parsed_date
                            
                        if action_date < two_weeks_ago:
                            continue  # Skip actions older than 6 days
                    except ValueError:
                        continue  # Skip rows with unparseable dates
                        
                    # Extract ticker symbol
                    symbol = columns[1].text.strip().upper()
                        
                    # Check for split type
                    action_type = columns[2].text.strip().lower()
                    action_detail = columns[3].text.strip().lower()
                    
                    # Look for reverse splits - check for reverse in the type or details
                    if ('reverse' in action_type or 'reverse' in action_detail or 'consolidation' in action_detail) and ('split' in action_type or 'split' in action_detail):
                        try:
                            # Extract the ratio (usually in format "1 for X")
                            ratio_match = re.search(r'1:(\d+)', action_detail)
                            if not ratio_match:
                                ratio_match = re.search(r'1 for (\d+)', action_detail)
                            if not ratio_match:
                                ratio_match = re.search(r'1-for-(\d+)', action_detail)
                                
                            if ratio_match:
                                ratio = ratio_match.group(1)
                                
                                # Format the date consistently
                                split_date = action_date.strftime('%Y-%m-%d')
                                
                                # Add to reverse splits list
                                reverse_splits.append((symbol, split_date, ratio))
                                
                                # If we only need the first symbol, return immediately
                                if check_first_only and reverse_splits:
                                    driver.quit()
                                    return reverse_splits
                        except Exception:
                            continue  # Skip on any parsing errors
                except Exception:
                    continue  # Skip any row with processing errors
                    
            driver.quit()
            return reverse_splits
            
        except Exception as e:
            logger.error(f"Error processing page with Selenium: {str(e)}")
            driver.quit()
            return []
            
    except Exception as e:
        logger.error(f"Error starting Selenium for scraping: {str(e)}")
        try:
            driver.quit()
        except:
            pass
        return []

# Scrape Nasdaq for news release date within the last 6 days
def get_news_release_date_nasdaq(symbol):
    """
    Scrape NASDAQ press releases for reverse split announcements
    Returns the earliest date found or None if no relevant announcement found
    """
    try:
        # Start a headless browser
        driver, temp_dir = start_headless_driver()
        
        # Add randomization to appear more human-like
        disguise_automation(driver)
        
        # NASDAQ company news URL
        url = f"https://www.nasdaq.com/market-activity/stocks/{symbol.lower()}/press-releases"
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load completely, specifically the news items
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".news-headlines"))
        )
        
        # Add some random sleep to mimic human behavior
        time.sleep(random.uniform(1, 3))
        
        # Get all news headlines
        news_items = driver.find_elements(By.CSS_SELECTOR, ".news-headlines article")
        
        # If no news items found, return None
        if not news_items:
            driver.quit()
            return None
        
        # Compile patterns for reverse split news headlines
        reverse_split_patterns = [
            re.compile(r'(?:\breverse\s+split\b|\bconsolidat\w+\b|\bsplit\s+ratio\b)', re.IGNORECASE),
            re.compile(r'(?:\bshare\s+consolidation\b|\bshare\s+combination\b)', re.IGNORECASE),
            re.compile(r'(?:\bstock\s+split\b|\bshare\s+split\b)', re.IGNORECASE)
        ]
        
        earliest_date = None
        
        # Loop through news items to find relevant announcements
        for item in news_items:
            try:
                # Get the headline and date
                headline_element = item.find_element(By.CSS_SELECTOR, "a")
                date_element = item.find_element(By.CSS_SELECTOR, "time")
                
                headline = headline_element.text.strip()
                news_date = date_element.text.strip()
                
                # Check if headline matches reverse split patterns
                if any(pattern.search(headline) for pattern in reverse_split_patterns):
                    # Parse the date
                    parsed_date = parser.parse(news_date)
                    news_date_str = parsed_date.strftime('%Y-%m-%d')
                    
                    # Update earliest date if this is earlier or if earliest_date is not set
                    if earliest_date is None or parsed_date < parser.parse(earliest_date):
                        earliest_date = news_date_str
            except Exception:
                continue
        
        driver.quit()
        return earliest_date
    
    except (TimeoutException, NoSuchElementException, WebDriverException):
        try:
            driver.quit()
        except:
            pass
        return None
    except Exception:
        try:
            driver.quit()
        except:
            pass
        return None

# Fallback to Yahoo Finance for news release date within the last 6 days
def get_news_release_date_yahoo(symbol):
    """
    Scrape Yahoo Finance press releases for reverse split announcements
    Returns the earliest date found or None if no relevant announcement found
    """
    try:
        # Start a headless browser
        driver, temp_dir = start_headless_driver()
        
        # Add randomization to appear more human-like
        disguise_automation(driver)
        
        # Yahoo Finance press releases URL
        url = f"https://finance.yahoo.com/quote/{symbol}/press-releases?p={symbol}"
        
        # Navigate to the URL
        driver.get(url)
        
        try:
            # Handle cookie consent if present
            consent_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='agree']"))
            )
            consent_button.click()
            time.sleep(random.uniform(1, 2))
        except:
            # No consent button or it timed out, continue
            pass
        
        # Wait for press releases to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='press-releases']"))
            )
        except TimeoutException:
            # If press releases don't load, try a different approach with news
            driver.get(f"https://finance.yahoo.com/quote/{symbol}/news?p={symbol}")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul li article"))
            )
        
        # Random delay to mimic human behavior
        time.sleep(random.uniform(2, 4))
        
        # Get press releases or news headlines
        try:
            headlines = driver.find_elements(By.CSS_SELECTOR, "div[data-test='press-releases'] a h3")
            dates = driver.find_elements(By.CSS_SELECTOR, "div[data-test='press-releases'] div.C($tertiaryColor) span")
        except:
            # Try news headlines as fallback
            headlines = driver.find_elements(By.CSS_SELECTOR, "ul li article h3")
            dates = driver.find_elements(By.CSS_SELECTOR, "ul li article div.C($tertiaryColor) span")
        
        # If no headlines found, return None
        if not headlines:
            driver.quit()
            return None
        
        # Compile patterns for reverse split news headlines
        reverse_split_patterns = [
            re.compile(r'(?:\breverse\s+split\b|\bconsolidat\w+\b|\bsplit\s+ratio\b)', re.IGNORECASE),
            re.compile(r'(?:\bshare\s+consolidation\b|\bshare\s+combination\b)', re.IGNORECASE),
            re.compile(r'(?:\bstock\s+split\b|\bshare\s+split\b)', re.IGNORECASE)
        ]
        
        earliest_date = None
        
        # Loop through headlines to find relevant announcements
        for i, headline_elem in enumerate(headlines):
            if i >= len(dates):
                break  # Safety check to ensure we don't go out of bounds
                
            headline = headline_elem.text.strip()
            
            # Check if headline matches reverse split patterns
            if any(pattern.search(headline) for pattern in reverse_split_patterns):
                # Get corresponding date for this headline
                date_text = dates[i].text.strip()
                
                try:
                    # Parse the date, assuming Yahoo Finance format
                    parsed_date = parser.parse(date_text)
                    news_date_str = parsed_date.strftime('%Y-%m-%d')
                    
                    # Update earliest date if this is earlier or if earliest_date is not set
                    if earliest_date is None or parsed_date < parser.parse(earliest_date):
                        earliest_date = news_date_str
                except:
                    continue
        
        driver.quit()
        return earliest_date
        
    except (TimeoutException, NoSuchElementException, WebDriverException):
        try:
            driver.quit()
        except:
            pass
        return None
    except Exception:
        try:
            driver.quit()
        except:
            pass
        return None

def get_current_price(symbol):
    """
    Get the current price of a stock
    """
    try:
        data = yf.Ticker(symbol)
        price = data.fast_info['last_price']
        return round(price, 2) if price is not None else None
    except Exception as e:
        return None

# Main function to gather reverse split data
def find_reverse_split_info(existing_symbols=None):
    """
    Main function to gather reverse stock split data
    
    Args:
        existing_symbols: Optional list of symbols to check against cached data
        
    Returns:
        List of dictionaries with reverse split information
    """
    # Load previously cached data
    cached_data = load_split_data()
    no_news_data = load_no_news_symbols()
    
    # Clean up old entries
    cached_data, no_news_data = clean_old_entries(cached_data, no_news_data)
    
    stock_analysis_url = "https://stockanalysis.com/actions/"
    
    # First, just get the first symbol to check if there's new data
    first_symbol_result = scrape_stock_analysis(stock_analysis_url, check_first_only=True)
    
    # If no data found at all, return cached data or empty list
    if not first_symbol_result:
        logger.info("No reverse stock splits or share consolidations found within the last 6 days.")
        return cached_data or []
    
    # Extract first symbol info
    first_symbol, first_split_date, first_ratio = first_symbol_result[0]
    
    # Check if we have cached data and if the first symbol matches
    if cached_data and first_symbol == cached_data[0]['symbol'] and first_split_date == cached_data[0]['split_date']:
        logger.info(f"No new data available. First symbol {first_symbol} with split date {first_split_date} matches cached data.")
        return cached_data
    
    # If we have new data, perform a full scrape
    logger.info("New data detected. Performing full scrape...")
    reverse_splits = scrape_stock_analysis(stock_analysis_url)
    
    if not reverse_splits:
        logger.info("No reverse stock splits or share consolidations found within the last 6 days.")
        return cached_data or []

    results = []
    no_news_results = []
    total_symbols = len(reverse_splits)
    logger.info(f"Found {total_symbols} potential reverse splits to process")
    
    # Sort symbols by split date (most recent first) to prioritize newer information
    reverse_splits.sort(key=lambda x: x[1], reverse=True)
    
    for i, (symbol, split_date, ratio) in enumerate(reverse_splits, 1):
        # If existing_symbols is provided, only process symbols that are not in that list
        if existing_symbols and symbol in existing_symbols:
            # For existing symbols, use cached data if available
            existing_entry = next((item for item in cached_data if item['symbol'] == symbol), None)
            if existing_entry:
                results.append(existing_entry)
            continue
            
        # Check if this symbol with the same split date already exists in cached data
        existing_entry = next((item for item in cached_data if item['symbol'] == symbol and item['split_date'] == split_date), None)
        
        if existing_entry:
            logger.debug(f"Using cached data for {symbol}")
            results.append(existing_entry)
            continue
        
        # Check if this symbol is in the no-news cache
        no_news_entry = next((item for item in no_news_data if item['symbol'] == symbol and item['split_date'] == split_date), None)
        
        if no_news_entry:
            logger.debug(f"Skipping {symbol} - previously found to have no news data")
            no_news_results.append(no_news_entry)
            continue
            
        logger.info(f"Processing symbol {symbol} ({i}/{total_symbols})")
            
        # First try NASDAQ
        release_date = get_news_release_date_nasdaq(symbol)
        
        # If no result from NASDAQ, try Yahoo Finance
        if not release_date:
            logger.debug(f"No release date found on NASDAQ for {symbol}, trying Yahoo Finance")
            release_date = get_news_release_date_yahoo(symbol)

        if release_date:
            # Get current price
            current_price = get_current_price(symbol)
            logger.info(f"Current price for {symbol}: {current_price}")
            
            # Calculate expected price (if current price is available)
            expected_price = None
            if current_price:
                try:
                    expected_price = float(current_price) * float(ratio)
                except (ValueError, TypeError):
                    pass
            
            # Calculate days between
            days_between = None
            try:
                days_between = (datetime.strptime(split_date, '%Y-%m-%d') - 
                               datetime.strptime(release_date, '%Y-%m-%d')).days
            except Exception:
                pass
                
            logger.info(f"Found data for {symbol}: Release date={release_date}, Split date={split_date}")
                
            results.append({
                'symbol': symbol,
                'split_date': split_date,
                'ratio': ratio,
                'news_release_date': release_date,
                'current_price': current_price,
                'expected_price': expected_price,
                'days_between': days_between
            })
        else:
            logger.info(f"No news release date found for {symbol}")
            # Add to no-news cache for future reference
            no_news_results.append({
                'symbol': symbol,
                'split_date': split_date,
                'ratio': ratio,
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            })
            
        # Add a delay between processing symbols to avoid being rate-limited
        if i < total_symbols:  # Don't delay after the last symbol
            short_sleep()
    
    # If we have results, sort by days between news release and split date
    if results:
        logger.info(f"Processing complete. Found news release dates for {len(results)}/{total_symbols} symbols.")

        # TODO: Add sorting by date, ticker and status
        results.sort(key=lambda x: (datetime.strptime(x['split_date'], '%Y-%m-%d') - 
                                   datetime.strptime(x['news_release_date'], '%Y-%m-%d')).days 
                                   if x.get('days_between') is not None else float('inf'))
    
    # Save the new results to caches
    save_split_data(results)
    save_no_news_symbols(no_news_results)
            
    return results

# Add this at the end of the file
if __name__ == "__main__":
    # This will only run when the script is executed directly, not when imported
    logger.info("Running split_scraper directly")
    results = find_reverse_split_info()
    logger.info(f"Found {len(results)} reverse splits")