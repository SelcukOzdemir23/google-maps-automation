"""
Google Maps Scraper - A tool to extract business information from Google Maps.

This script allows users to scrape information about businesses from Google Maps
based on search criteria such as location and business type.
"""

import time
import csv
import logging
from typing import Dict, List, Optional, Set

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """Class to handle scraping operations from Google Maps."""

    def __init__(self, headless: bool = False, wait_time: int = 15):
        """
        Initialize the scraper with browser settings.
        
        Args:
            headless: Whether to run the browser in headless mode
            wait_time: Default wait time for Selenium WebDriverWait
        """
        self.wait_time = wait_time
        self.driver = self._setup_driver(headless)
        self.wait = WebDriverWait(self.driver, self.wait_time)
        
    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """
        Set up and return a Chrome WebDriver instance with appropriate options.
        
        Args:
            headless: Whether to run in headless mode
            
        Returns:
            Configured Chrome WebDriver instance
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
        
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        
        return webdriver.Chrome(options=chrome_options)
    
    def scrape_businesses(
        self, 
        country: str, 
        query_type: str = "companies", 
        max_results: int = 100
    ) -> List[Dict[str, str]]:
        """
        Scrape businesses from Google Maps for a specific country and query.
        
        Args:
            country: The country to search in
            query_type: Type of search query (e.g., 'companies', 'restaurants')
            max_results: Maximum number of results to scrape
            
        Returns:
            List of dictionaries containing business information
        """
        search_query = f"{query_type} in {country}"
        results = []
        
        try:
            # Navigate to Google Maps and perform search
            self._navigate_to_google_maps()
            self._handle_cookie_consent()
            self._perform_search(search_query)
            
            # Process search results
            results = self._process_search_results(country, max_results)
            
            logger.info(f"Successfully scraped {len(results)} businesses in {country}")
            return results
            
        except Exception as e:
            logger.error(f"An error occurred during scraping: {str(e)}")
            return results
            
        finally:
            self.close()
    
    def _navigate_to_google_maps(self) -> None:
        """Navigate to the Google Maps website."""
        self.driver.get("https://www.google.com/maps")
    
    def _handle_cookie_consent(self) -> None:
        """Accept cookies if the consent dialog appears."""
        try:
            cookie_accept = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept all')]"))
            )
            cookie_accept.click()
        except TimeoutException:
            # Cookie dialog didn't appear or has different format
            logger.debug("No cookie consent dialog found or it has a different format")
            pass
    
    def _perform_search(self, query: str) -> None:
        """
        Search for the given query on Google Maps.
        
        Args:
            query: The search query to enter
        """
        search_box = self.wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.ENTER)
        
        # Wait for results to load
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
        time.sleep(3)  # Additional wait to ensure all elements are loaded
    
    def _process_search_results(self, country: str, max_results: int) -> List[Dict[str, str]]:
        """
        Process the search results to extract business information.
        
        Args:
            country: The country being searched
            max_results: Maximum number of results to process
            
        Returns:
            List of business information dictionaries
        """
        businesses = []
        processed_results: Set[str] = set()  # Track processed results by name
        scroll_attempts = 0
        max_scroll_attempts = 30
        
        while len(businesses) < max_results and scroll_attempts < max_scroll_attempts:
            try:
                # Find all result elements currently visible
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
                logger.debug(f"Found {len(result_elements)} elements in this batch")
                
                self._process_visible_results(result_elements, businesses, processed_results, max_results, country)
                
                # Check if we've found enough businesses
                if len(businesses) >= max_results:
                    break
                
                # Try to load more results by scrolling
                if not self._scroll_for_more_results(result_elements):
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0  # Reset if we loaded new results
                    
            except Exception as e:
                logger.error(f"Error during scrolling: {str(e)}")
                scroll_attempts += 1
                time.sleep(1)
        
        return businesses
    
    def _process_visible_results(
        self, 
        result_elements: List, 
        businesses: List[Dict[str, str]], 
        processed_results: Set[str],
        max_results: int,
        country: str
    ) -> None:
        """
        Process visible result elements to extract business information.
        
        Args:
            result_elements: List of WebElement results to process
            businesses: List to append extracted business information to
            processed_results: Set of already processed business names
            max_results: Maximum number of results to collect
            country: The country being searched
        """
        for element in result_elements:
            if len(businesses) >= max_results:
                break
                
            try:
                # Extract basic info from the card without clicking
                business_info = self._extract_basic_info_from_card(element, country)
                
                if not business_info or business_info.get('name') in processed_results:
                    continue

                # Remove "back to top" button if present (can interfere with clicking)
                self._remove_back_to_top_button()
                    
                # Click to get detailed info
                element.click()
                time.sleep(1.5)  # Wait for details panel
                
                # Get additional details from the side panel
                detailed_info = self._extract_detailed_info()
                if detailed_info:
                    business_info.update(detailed_info)
                
                # Add to results if new
                if business_info.get('name') not in processed_results:
                    businesses.append(business_info)
                    processed_results.add(business_info.get('name'))
                    logger.info(f"Scraped {len(businesses)}/{max_results}: {business_info.get('name', 'Unknown')}")
                
                # Try to go back to results list
                self._return_to_results_list()
                
            except (StaleElementReferenceException, NoSuchElementException) as e:
                logger.warning(f"Error processing element: {str(e)}")
                continue
    
    def _remove_back_to_top_button(self) -> None:
        """Remove the 'back to top' button that can interfere with clicking elements."""
        try:
            back_to_top = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.RiRi5e")))
            # Execute JavaScript to remove the element
            self.driver.execute_script("arguments[0].remove()", back_to_top)
        except Exception:
            # Element not found, continue
            pass
    
    def _return_to_results_list(self) -> None:
        """Return to the main results list from a business details view."""
        try:
            back_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Back']")
            if back_buttons:
                back_buttons[0].click()
                time.sleep(1)
        except Exception as e:
            logger.warning(f"Could not return to results list: {str(e)}")
            pass
    
    def _scroll_for_more_results(self, current_elements: List) -> bool:
        """
        Scroll down to load more results.
        
        Args:
            current_elements: The current result elements for comparison
            
        Returns:
            Boolean indicating if new results were loaded
        """
        try:
            # Find the feed container and scroll it
            feed = self.driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
            
            # Wait for new results to load
            time.sleep(2)
            
            # Check if we loaded new results
            new_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
            return len(new_elements) > len(current_elements)
            
        except Exception as e:
            logger.warning(f"Error scrolling for more results: {str(e)}")
            return False
    
    def _extract_basic_info_from_card(self, element, country: str) -> Optional[Dict[str, str]]:
        """
        Extract basic business information from a result card.
        
        Args:
            element: The WebElement representing the business card
            country: The country being searched
            
        Returns:
            Dictionary containing basic business information or None if extraction fails
        """
        try:
            # Extract name
            name_element = element.find_element(By.CSS_SELECTOR, "div.qBF1Pd")
            name = name_element.text if name_element else "Unknown"
            
            # Initialize with basic info
            business_info = {
                "name": name,
                "country": country,
                "address": "",
                "phone": "",
                "website": "",
                "category": "",
                "rating": "",
                "num_reviews": "",
            }
            
            # Try to extract rating and review count
            try:
                rating_element = element.find_element(By.CSS_SELECTOR, "span.MW4etd")
                if rating_element:
                    business_info["rating"] = rating_element.text
                    
                review_count_element = element.find_element(By.CSS_SELECTOR, "span.UY7F9")
                if review_count_element:
                    # Clean the review count (remove parentheses)
                    review_count = review_count_element.text
                    business_info["num_reviews"] = review_count.strip("()")
                    
            except (NoSuchElementException, StaleElementReferenceException):
                # Some elements might not be available for all results
                pass
                
            return business_info
            
        except Exception as e:
            logger.warning(f"Error extracting from card: {str(e)}")
            return None
    
    def _extract_detailed_info(self) -> Dict[str, str]:
        """
        Extract additional details from the business details panel.
        
        Returns:
            Dictionary containing detailed business information
        """
        try:
            # Wait for details panel to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.rogA2c")))
            time.sleep(1)  # Give a moment for all details to render
            
            detailed_info = {}
            
            # Extract category
            try:
                detailed_info["category"] = self.driver.find_element(
                    By.CSS_SELECTOR, "button.DkEaL"
                ).text
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            
            # Extract website
            try:
                detailed_info["website"] = self.driver.find_element(
                    By.CSS_SELECTOR, "a[data-item-id^='authority']"
                ).get_attribute("href")
            except (NoSuchElementException, StaleElementReferenceException):
                pass
                
            # Extract address
            try:
                detailed_info["address"] = self.driver.find_element(
                    By.CSS_SELECTOR, "button[data-item-id^='address'] > div > div:nth-of-type(2)"
                ).text
            except (NoSuchElementException, StaleElementReferenceException):
                pass
                
            # Extract phone number
            try:
                detailed_info["phone"] = self.driver.find_element(
                    By.CSS_SELECTOR, "button[data-item-id^='phone'] > div > div:nth-of-type(2)"
                ).text
            except (NoSuchElementException, StaleElementReferenceException):
                pass
                
            return detailed_info
            
        except Exception as e:
            logger.warning(f"Error extracting detailed info: {str(e)}")
            return {}
    
    def close(self) -> None:
        """Close the browser and clean up resources."""
        if self.driver:
            self.driver.quit()


def save_to_csv(data: List[Dict[str, str]], filename: str = "businesses.csv") -> bool:
    """
    Save the scraped business data to a CSV file.
    
    Args:
        data: List of business dictionaries to save
        filename: Name of the output CSV file
        
    Returns:
        Boolean indicating success or failure
    """
    if not data:
        logger.warning("No data to save.")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in data:
                writer.writerow(item)
                
        logger.info(f"Data successfully saved to {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving data to CSV: {str(e)}")
        return False


def get_user_input() -> tuple:
    """
    Get search parameters from user input.
    
    Returns:
        Tuple of (country, query_type, max_results)
    """
    country = input("Enter the country (e.g., United States): ").strip()
    if not country:
        logger.error("No country provided.")
        return None, None, None

    query_type = input("Enter the query type (e.g., companies, restaurants, hotels): ").strip()
    if not query_type:
        logger.error("No query type provided.")
        return country, None, None

    max_results_input = input("Enter the maximum number of results to scrape (default is 15): ").strip()
    if not max_results_input:
        max_results = 15
    else:
        try:
            max_results = int(max_results_input)
        except ValueError:
            logger.warning("Invalid number provided. Defaulting to 15.")
            max_results = 15
    
    return country, query_type, max_results


def main():
    """Main function to execute the scraping process."""
    logger.info("Google Maps Scraper")
    logger.info("-----------------")
    
    # Get user input
    country, query_type, max_results = get_user_input()
    if not country or not query_type:
        logger.error("Missing required input. Exiting.")
        return
    
    # Initialize scraper
    logger.info(f"Starting to scrape {query_type} - {country}...")
    scraper = GoogleMapsScraper(headless=False)
    
    # Perform scraping
    businesses = scraper.scrape_businesses(country, query_type, max_results)
    
    # Save results
    if businesses:
        save_to_csv(businesses, f"{country.lower()}_{query_type}.csv")
    else:
        logger.warning("No businesses were scraped.")


if __name__ == "__main__":
    main()