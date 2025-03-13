import logging
from services.split_scraper import load_split_data, load_no_news_symbols, find_reverse_split_info, save_split_data, get_current_price
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SplitController:
    @staticmethod
    def get_reverse_splits(query_params=None):
        """
        Controller method to fetch reverse splits data
        
        Args:
            query_params: Dictionary containing query parameters
            
        Returns:
            Dictionary with results and status code
        """
        if query_params is None:
            query_params = {}
            
        try:
            # Check if cache file exists and has content
            cache_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services', 'split_scraper_no_news_cache.json')
            cache_empty = True
            
            if os.path.exists(cache_file_path):
                try:
                    with open(cache_file_path, 'r') as f:
                        cache_content = json.load(f)
                        if cache_content and len(cache_content) > 0:
                            cache_empty = False
                            logger.info(f"Cache file exists with {len(cache_content)} items")
                        else:
                            logger.info("Cache file exists but is empty")
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error reading cache file: {str(e)}")
            else:
                logger.info("Cache file does not exist")
            
            # Check if we have existing symbols (for incremental update)
            existing_symbols = None
            
            if 'existing' in query_params:
                existing_str = query_params.get('existing', '')
                if existing_str:
                    existing_symbols = existing_str.split(',')
                    logger.info(f"Received request with {len(existing_symbols)} existing symbols")
            
            # First load cached data as a fallback
            cached_results = load_split_data()
            no_news_symbols = load_no_news_symbols()
            logger.info(f"Loaded {len(cached_results)} splits and {len(no_news_symbols)} no-news symbols from cache")
            
            # Always try to scrape for new data
            logger.info(f"Scraping for new reverse split data")
            new_results = find_reverse_split_info(existing_symbols)
            
            if new_results:
                logger.info(f"Found {len(new_results)} new or updated reverse splits")
                # Save the new results to cache
                save_split_data(new_results)
                # Use the new results
                results = new_results
            else:
                logger.info("No new reverse splits found, using cached data")
                results = cached_results
            
            # Check if cache is STILL empty after scraping attempt
            cache_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services', 'split_scraper_no_news_cache.json')
            cache_empty = True
            
            if os.path.exists(cache_file_path):
                try:
                    with open(cache_file_path, 'r') as f:
                        cache_content = json.load(f)
                        if cache_content and len(cache_content) > 0:
                            cache_empty = False
                            logger.info(f"Cache file now exists with {len(cache_content)} items")
                        else:
                            logger.info("Cache file still exists but is empty")
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error reading cache file: {str(e)}")
            else:
                logger.info("Cache file still does not exist after scraping")
            
            # Transform data if needed to ensure all expected fields are present
            for item in results:
                # Ensure these fields are present or set to None
                item.setdefault('days_between', None)
                item.setdefault('current_price', None)
                item.setdefault('expected_price', None)
            
            # Combine both types of data in the response
            all_data = results + no_news_symbols
            logger.info(f"Returning {len(results)} splits and {len(no_news_symbols)} no-news symbols")
                
            return {
                "success": True, 
                "data": all_data,
                "cache_empty": cache_empty
            }, 200
        except Exception as e:
            logger.error(f"Error in reverse splits controller: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}, 500 