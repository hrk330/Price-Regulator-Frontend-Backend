"""
Web scraping engines for different websites.
Each engine handles the specific structure and parsing logic for different e-commerce sites.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import logging
import os
import random
from urllib.parse import urljoin, quote_plus
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseScrapingEngine:
    """Base class for all scraping engines."""
    
    def __init__(self, website_config: Dict[str, Any]):
        self.config = website_config
        self.session = requests.Session()
        self.session.headers.update(website_config.get('headers', {}))
        
    def search_products(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for products on the website."""
        raise NotImplementedError
        
    def parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text and return as float (for better JSON serialization)."""
        if not price_text:
            return None
        
        # Handle multiple prices by taking the first one
        lines = price_text.strip().split('\n')
        first_line = lines[0].strip()
        
        # Extract the first price from the line
        # Look for patterns like "Rs.725" or "725" or "Rs 725"
        price_match = re.search(r'(?:Rs\.?\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)', first_line)
        if price_match:
            price_clean = price_match.group(1).replace(',', '')
        else:
            # Fallback to old method
            price_clean = re.sub(r'[^\d.,]', '', first_line)
            price_clean = price_clean.replace(',', '')
            
            # Handle cases where Rs. is removed but leaves a decimal point at the beginning
            if price_clean.startswith('.'):
                price_clean = price_clean[1:]
            
            # If we have multiple numbers, take the first one
            if price_clean and not price_clean.replace('.', '').isdigit():
                # Extract first number sequence
                match = re.search(r'\d+(?:\.\d+)?', price_clean)
                if match:
                    price_clean = match.group()
        
        try:
            # Convert to float instead of Decimal for better JSON serialization
            return float(price_clean) if price_clean else None
        except (InvalidOperation, ValueError):
            logger.warning(f"Could not parse price: {price_text}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def make_request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retries and rate limiting."""
        for attempt in range(retries):
            try:
                time.sleep(self.config.get('rate_limit_delay', 1.0))
                
                # Make request with proper encoding handling
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Ensure proper content encoding
                if response.encoding == 'ISO-8859-1':
                    response.encoding = 'utf-8'
                
                # Check if content is readable
                try:
                    content_preview = response.text[:100]
                    if any(ord(char) > 127 for char in content_preview):
                        logger.warning(f"Content appears to be encoded/binary for URL: {url}")
                        # Try to decode as utf-8
                        response.encoding = 'utf-8'
                except:
                    pass
                
                return response
                
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == retries - 1:
                    logger.error(f"All retry attempts failed for URL: {url}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None


class AmazonScrapingEngine(BaseScrapingEngine):
    """Scraping engine for Amazon."""
    
    def search_products(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for products on Amazon."""
        search_url = f"https://www.amazon.com/s?k={quote_plus(query)}"
        
        response = self.make_request(search_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        # Amazon product containers
        product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for container in product_containers[:max_results]:
            try:
                product_data = self._parse_amazon_product(container)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                logger.error(f"Error parsing Amazon product: {e}")
                continue
        
        return products
    
    def _parse_amazon_product(self, container) -> Optional[Dict[str, Any]]:
        """Parse individual Amazon product."""
        try:
            # Product name
            name_elem = container.find('h2', class_='a-size-mini')
            if not name_elem:
                name_elem = container.find('span', class_='a-size-medium')
            name = self.clean_text(name_elem.get_text()) if name_elem else ""
            
            if not name:
                return None
            
            # Price
            price_elem = container.find('span', class_='a-price-whole')
            if not price_elem:
                price_elem = container.find('span', class_='a-offscreen')
            price_text = price_elem.get_text() if price_elem else ""
            price = self.parse_price(price_text)
            
            if not price:
                return None
            
            # URL
            link_elem = container.find('h2', class_='a-size-mini').find('a') if container.find('h2', class_='a-size-mini') else None
            if not link_elem:
                link_elem = container.find('a', class_='a-link-normal')
            url = urljoin("https://www.amazon.com", link_elem.get('href')) if link_elem else ""
            
            # Image
            img_elem = container.find('img', class_='s-image')
            image_url = img_elem.get('src') if img_elem else ""
            
            # Rating
            rating_elem = container.find('span', class_='a-icon-alt')
            rating = None
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Availability
            availability = not bool(container.find('span', string=re.compile(r'Currently unavailable')))
            
            return {
                'name': name,
                'price': price,
                'url': url,
                'image_url': image_url,
                'rating': rating,
                'availability': availability,
                'marketplace': 'amazon'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Amazon product container: {e}")
            return None


class EbayScrapingEngine(BaseScrapingEngine):
    """Scraping engine for eBay."""
    
    def search_products(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for products on eBay."""
        search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}"
        
        response = self.make_request(search_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        # eBay product containers
        product_containers = soup.find_all('div', class_='s-item')
        
        for container in product_containers[:max_results]:
            try:
                product_data = self._parse_ebay_product(container)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                logger.error(f"Error parsing eBay product: {e}")
                continue
        
        return products
    
    def _parse_ebay_product(self, container) -> Optional[Dict[str, Any]]:
        """Parse individual eBay product."""
        try:
            # Product name
            name_elem = container.find('h3', class_='s-item__title')
            name = self.clean_text(name_elem.get_text()) if name_elem else ""
            
            if not name or "Shop on eBay" in name:
                return None
            
            # Price
            price_elem = container.find('span', class_='s-item__price')
            price_text = price_elem.get_text() if price_elem else ""
            price = self.parse_price(price_text)
            
            if not price:
                return None
            
            # URL
            link_elem = container.find('a', class_='s-item__link')
            url = link_elem.get('href') if link_elem else ""
            
            # Image
            img_elem = container.find('img', class_='s-item__image')
            image_url = img_elem.get('src') if img_elem else ""
            
            # Availability (eBay items are generally available if listed)
            availability = True
            
            return {
                'name': name,
                'price': price,
                'url': url,
                'image_url': image_url,
                'availability': availability,
                'marketplace': 'ebay'
            }
            
        except Exception as e:
            logger.error(f"Error parsing eBay product container: {e}")
            return None


class WalmartScrapingEngine(BaseScrapingEngine):
    """Scraping engine for Walmart."""
    
    def search_products(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for products on Walmart."""
        search_url = f"https://www.walmart.com/search?q={quote_plus(query)}"
        
        response = self.make_request(search_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        # Walmart product containers
        product_containers = soup.find_all('div', {'data-testid': 'item-stack'})
        
        for container in product_containers[:max_results]:
            try:
                product_data = self._parse_walmart_product(container)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                logger.error(f"Error parsing Walmart product: {e}")
                continue
        
        return products
    
    def _parse_walmart_product(self, container) -> Optional[Dict[str, Any]]:
        """Parse individual Walmart product."""
        try:
            # Product name
            name_elem = container.find('span', {'data-automation-id': 'product-title'})
            name = self.clean_text(name_elem.get_text()) if name_elem else ""
            
            if not name:
                return None
            
            # Price
            price_elem = container.find('span', {'data-automation-id': 'product-price'})
            price_text = price_elem.get_text() if price_elem else ""
            price = self.parse_price(price_text)
            
            if not price:
                return None
            
            # URL
            link_elem = container.find('a', {'data-automation-id': 'product-title'})
            url = urljoin("https://www.walmart.com", link_elem.get('href')) if link_elem else ""
            
            # Image
            img_elem = container.find('img', {'data-testid': 'product-image'})
            image_url = img_elem.get('src') if img_elem else ""
            
            # Availability
            availability = not bool(container.find('span', string=re.compile(r'Out of stock')))
            
            return {
                'name': name,
                'price': price,
                'url': url,
                'image_url': image_url,
                'availability': availability,
                'marketplace': 'walmart'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Walmart product container: {e}")
            return None


class GenericScrapingEngine(BaseScrapingEngine):
    """Generic scraping engine for custom websites."""
    
    def search_products(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for products using custom configuration."""
        config = self.config.get('scraping_config', {})
        # Check both top-level and nested search_url_template
        search_url_template = self.config.get('search_url_template') or config.get('search_url_template', '')
        
        if not search_url_template:
            logger.error("No search URL template configured")
            return []
        
        search_url = search_url_template.format(query=quote_plus(query))
        logger.info(f"GenericScrapingEngine: Using search URL: {search_url}")
        
        response = self.make_request(search_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        # Get product containers using configured selector
        container_selector = config.get('product_container_selector', '')
        if not container_selector:
            logger.error("No product container selector configured")
            return []
        
        product_containers = soup.select(container_selector)
        
        for container in product_containers[:max_results]:
            try:
                product_data = self._parse_generic_product(container, config)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                logger.error(f"Error parsing generic product: {e}")
                continue
        
        return products
    
    def _parse_generic_product(self, container, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse individual product using custom selectors."""
        try:
            selectors = config.get('selectors', {})
            
            # Product name
            name_selector = selectors.get('name', '')
            name_elem = container.select_one(name_selector) if name_selector else None
            name = self.clean_text(name_elem.get_text()) if name_elem else ""
            
            if not name:
                return None
            
            # Price
            price_selector = selectors.get('price', '')
            price_elem = container.select_one(price_selector) if price_selector else None
            price_text = price_elem.get_text() if price_elem else ""
            price = self.parse_price(price_text)
            
            if not price:
                return None
            
            # URL
            url_selector = selectors.get('url', '')
            url_elem = container.select_one(url_selector) if url_selector else None
            url = url_elem.get('href') if url_elem else ""
            if url and not url.startswith('http'):
                url = urljoin(self.config.get('base_url', ''), url)
            
            # Image
            image_selector = selectors.get('image', '')
            img_elem = container.select_one(image_selector) if image_selector else None
            image_url = img_elem.get('src') if img_elem else ""
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(self.config.get('base_url', ''), image_url)
            
            # Availability
            availability_selector = selectors.get('availability', '')
            availability = True
            if availability_selector:
                availability_elem = container.select_one(availability_selector)
                if availability_elem:
                    availability_text = availability_elem.get_text().lower()
                    availability = 'out of stock' not in availability_text and 'unavailable' not in availability_text
            
            return {
                'name': name,
                'price': price,
                'url': url,
                'image_url': image_url,
                'availability': availability,
                'marketplace': config.get('marketplace', 'other')
            }
            
        except Exception as e:
            logger.error(f"Error parsing generic product container: {e}")
            return None


class SeleniumScrapingEngine(BaseScrapingEngine):
    """Selenium-based scraping engine for websites with anti-scraping protection."""
    
    def __init__(self, website_config: Dict[str, Any]):
        super().__init__(website_config)
        self.driver = None
        self.selenium_config = getattr(settings, 'SELENIUM_CONFIG', {})
        self.wait = None
        
    def _setup_driver(self):
        """Setup and configure the WebDriver."""
        try:
            browser = self.selenium_config.get('BROWSER', 'chrome').lower()
            
            if browser == 'chrome':
                self.driver = self._setup_chrome_driver()
            elif browser == 'firefox':
                self.driver = self._setup_firefox_driver()
            else:
                raise ValueError(f"Unsupported browser: {browser}")
            
            # Configure timeouts
            self.driver.implicitly_wait(self.selenium_config.get('IMPLICIT_WAIT', 10))
            self.driver.set_page_load_timeout(self.selenium_config.get('PAGE_LOAD_TIMEOUT', 30))
            
            # Set window size
            window_size = self.selenium_config.get('WINDOW_SIZE', (1920, 1080))
            self.driver.set_window_size(window_size[0], window_size[1])
            
            # Setup wait object
            self.wait = WebDriverWait(self.driver, self.selenium_config.get('IMPLICIT_WAIT', 10))
            
            logger.info(f"Selenium WebDriver initialized successfully with {browser}")
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            raise
    
    def _setup_chrome_driver(self):
        """Setup Chrome WebDriver with optimized options."""
        options = ChromeOptions()
        
        # Basic options
        if self.selenium_config.get('HEADLESS', True):
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        if self.selenium_config.get('DISABLE_IMAGES', True):
            options.add_argument('--disable-images')
        if self.selenium_config.get('DISABLE_JS', False):
            options.add_argument('--disable-javascript')
        if self.selenium_config.get('DISABLE_CSS', False):
            options.add_argument('--disable-css')
        
        # User agent
        user_agent = self.selenium_config.get('USER_AGENT', '')
        if user_agent:
            options.add_argument(f'--user-agent={user_agent}')
        
        # Performance optimizations
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # Memory optimizations
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        # Anti-detection measures
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Setup service with correct architecture
        try:
            # Try to get the correct ChromeDriver for the system
            driver_path = ChromeDriverManager().install()
            service = ChromeService(driver_path)
        except Exception as e:
            logger.error(f"Failed to setup ChromeDriver: {str(e)}")
            raise
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _setup_firefox_driver(self):
        """Setup Firefox WebDriver with optimized options."""
        options = FirefoxOptions()
        
        # Basic options
        if self.selenium_config.get('HEADLESS', True):
            options.add_argument('--headless')
        
        # Performance optimizations
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference('general.useragent.override', self.selenium_config.get('USER_AGENT', ''))
        
        if self.selenium_config.get('DISABLE_IMAGES', True):
            options.set_preference('permissions.default.image', 2)
        
        if self.selenium_config.get('DISABLE_JS', False):
            options.set_preference('javascript.enabled', False)
        
        # Setup service
        service = FirefoxService(GeckoDriverManager().install())
        
        return webdriver.Firefox(service=service, options=options)
    
    def _take_screenshot(self, filename_prefix="error"):
        """Take a screenshot for debugging purposes."""
        try:
            screenshot_dir = self.selenium_config.get('SCREENSHOT_DIR')
            if screenshot_dir:
                os.makedirs(screenshot_dir, exist_ok=True)
                timestamp = int(time.time())
                filename = f"{filename_prefix}_{timestamp}.png"
                filepath = os.path.join(screenshot_dir, filename)
                self.driver.save_screenshot(filepath)
                logger.info(f"Screenshot saved: {filepath}")
                return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
        return None
    
    def _random_delay(self, min_delay=1, max_delay=3):
        """Add random delay to mimic human behavior."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def search_products(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for products using Selenium."""
        if not self.driver:
            self._setup_driver()
        
        try:
            config = self.config.get('scraping_config', {})
            search_url_template = self.config.get('search_url_template') or config.get('search_url_template', '')
            
            if not search_url_template:
                logger.error("No search URL template configured")
                return []
            
            search_url = search_url_template.format(query=quote_plus(query))
            logger.info(f"SeleniumScrapingEngine: Using search URL: {search_url}")
            
            # Navigate to search page
            self.driver.get(search_url)
            self._random_delay(2, 4)
            
            # Wait for page to load
            try:
                # Wait for any product container or search results
                container_selector = config.get('product_container_selector', '.product, .item, .result')
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, container_selector)))
            except TimeoutException:
                logger.warning("Timeout waiting for search results to load")
                if self.selenium_config.get('SCREENSHOT_ON_ERROR', True):
                    self._take_screenshot("search_timeout")
            
            # Parse products
            products = self._parse_selenium_products(config, max_results)
            
            return products
            
        except Exception as e:
            logger.error(f"Selenium search failed: {str(e)}")
            if self.selenium_config.get('SCREENSHOT_ON_ERROR', True):
                self._take_screenshot("search_error")
            return []
    
    def _parse_selenium_products(self, config: Dict[str, Any], max_results: int) -> List[Dict[str, Any]]:
        """Parse products from Selenium page."""
        products = []
        
        try:
            container_selector = config.get('product_container_selector', '.product, .item, .result')
            containers = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
            
            logger.info(f"Found {len(containers)} product containers")
            
            for i, container in enumerate(containers[:max_results]):
                try:
                    product_data = self._parse_selenium_product(container, config)
                    if product_data:
                        products.append(product_data)
                        logger.debug(f"Parsed product {i+1}: {product_data.get('name', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Error parsing product container {i+1}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing products: {str(e)}")
        
        return products
    
    def _parse_selenium_product(self, container, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse individual product from Selenium element."""
        try:
            selectors = config.get('selectors', {})
            
            # Product name
            name_selector = selectors.get('name', 'h1, h2, h3, h4, .title, .name, [class*="name"], [class*="title"]')
            name_elem = self._find_element_safe(container, name_selector)
            name = self.clean_text(name_elem.text) if name_elem else ""
            
            if not name:
                return None
            
            # Price
            price_selector = selectors.get('price', '.price, .cost, [class*="price"], [class*="cost"]')
            price_elem = self._find_element_safe(container, price_selector)
            price_text = price_elem.text if price_elem else ""
            price = self.parse_price(price_text)
            
            if not price:
                return None
            
            # URL
            url_selector = selectors.get('url', 'a')
            url_elem = self._find_element_safe(container, url_selector)
            url = url_elem.get_attribute('href') if url_elem else ""
            if url and not url.startswith('http'):
                url = urljoin(self.config.get('base_url', ''), url)
            
            # Image
            image_selector = selectors.get('image', 'img')
            img_elem = self._find_element_safe(container, image_selector)
            image_url = img_elem.get_attribute('src') if img_elem else ""
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(self.config.get('base_url', ''), image_url)
            
            # Availability
            availability_selector = selectors.get('availability', '.stock, .availability, [class*="stock"], [class*="availability"]')
            availability = True
            if availability_selector:
                availability_elem = self._find_element_safe(container, availability_selector)
                if availability_elem:
                    availability_text = availability_elem.text.lower()
                    availability = 'out of stock' not in availability_text and 'unavailable' not in availability_text
            
            return {
                'name': name,
                'price': price,
                'url': url,
                'image_url': image_url,
                'availability': availability,
                'marketplace': config.get('marketplace', 'other')
            }
            
        except Exception as e:
            logger.error(f"Error parsing selenium product: {str(e)}")
            return None
    
    def _find_element_safe(self, parent, selector):
        """Safely find an element with fallback selectors."""
        try:
            return parent.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            # Try common fallback selectors
            fallback_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '.title', '.name', '.product-name', '.item-name',
                '.price', '.cost', '.amount', '.value',
                'a', 'img'
            ]
            
            for fallback in fallback_selectors:
                try:
                    return parent.find_element(By.CSS_SELECTOR, fallback)
                except NoSuchElementException:
                    continue
            
            return None
    
    def close(self):
        """Close the WebDriver and cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None
                self.wait = None
    
    def __del__(self):
        """Ensure WebDriver is closed when object is destroyed."""
        self.close()


class HybridScrapingEngine(BaseScrapingEngine):
    """Hybrid engine that tries direct requests first, falls back to Selenium."""
    
    def __init__(self, website_config: Dict[str, Any]):
        super().__init__(website_config)
        self.selenium_engine = None
        self.use_selenium = website_config.get('use_selenium', False)
        self.fallback_to_selenium = website_config.get('fallback_to_selenium', True)
    
    def search_products(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Try direct request first, fall back to Selenium if needed."""
        
        # If explicitly configured to use Selenium, use it directly
        if self.use_selenium:
            return self._search_with_selenium(query, max_results)
        
        # Try direct HTTP request first
        try:
            logger.info(f"Trying direct HTTP request for query: {query}")
            products = self._search_with_requests(query, max_results)
            
            # Check if we got valid results
            if products and len(products) > 0:
                logger.info(f"Direct request successful, found {len(products)} products")
                return products
            
            # Check if we got encoded/protected content
            if self._is_protected_content():
                logger.warning("Detected protected content, falling back to Selenium")
                if self.fallback_to_selenium:
                    return self._search_with_selenium(query, max_results)
            
        except Exception as e:
            logger.warning(f"Direct request failed: {str(e)}")
            if self.fallback_to_selenium:
                logger.info("Falling back to Selenium")
                return self._search_with_selenium(query, max_results)
        
        return []
    
    def _search_with_requests(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using direct HTTP requests (existing logic)."""
        config = self.config.get('scraping_config', {})
        search_url_template = self.config.get('search_url_template') or config.get('search_url_template', '')
        
        if not search_url_template:
            logger.error("No search URL template configured")
            return []
        
        search_url = search_url_template.format(query=quote_plus(query))
        response = self.make_request(search_url)
        
        if not response:
            return []
        
        # Store response for content analysis
        self._last_response = response
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        container_selector = config.get('product_container_selector', '')
        if not container_selector:
            logger.error("No product container selector configured")
            return []
        
        product_containers = soup.select(container_selector)
        
        for container in product_containers[:max_results]:
            try:
                product_data = self._parse_generic_product(container, config)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                logger.error(f"Error parsing generic product: {e}")
                continue
        
        return products
    
    def _search_with_selenium(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Selenium."""
        if not self.selenium_engine:
            self.selenium_engine = SeleniumScrapingEngine(self.config)
        
        try:
            return self.selenium_engine.search_products(query, max_results)
        except Exception as e:
            logger.error(f"Selenium search failed: {str(e)}")
            return []
    
    def _is_protected_content(self) -> bool:
        """Check if the response contains protected/encoded content."""
        if not hasattr(self, '_last_response'):
            return False
        
        try:
            content = self._last_response.text[:1000]  # Check first 1000 chars
            
            # Check for common protection indicators
            protection_indicators = [
                'cloudflare',
                'datadome',
                'incapsula',
                'distil',
                'perimeterx',
                'bot protection',
                'access denied',
                'blocked',
                'challenge',
                'captcha'
            ]
            
            content_lower = content.lower()
            for indicator in protection_indicators:
                if indicator in content_lower:
                    return True
            
            # Check for encoded/binary content
            if any(ord(char) > 127 for char in content[:100]):
                return True
            
            # Check for very short content (likely protection page)
            if len(content.strip()) < 100:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking protected content: {str(e)}")
            return False
    
    def _parse_generic_product(self, container, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse individual product using custom selectors (from GenericScrapingEngine)."""
        try:
            selectors = config.get('selectors', {})
            
            # Product name
            name_selector = selectors.get('name', '')
            name_elem = container.select_one(name_selector) if name_selector else None
            name = self.clean_text(name_elem.get_text()) if name_elem else ""
            
            if not name:
                return None
            
            # Price
            price_selector = selectors.get('price', '')
            price_elem = container.select_one(price_selector) if price_selector else None
            price_text = price_elem.get_text() if price_elem else ""
            price = self.parse_price(price_text)
            
            if not price:
                return None
            
            # URL
            url_selector = selectors.get('url', '')
            url_elem = container.select_one(url_selector) if url_selector else None
            url = url_elem.get('href') if url_elem else ""
            if url and not url.startswith('http'):
                url = urljoin(self.config.get('base_url', ''), url)
            
            # Image
            image_selector = selectors.get('image', '')
            img_elem = container.select_one(image_selector) if image_selector else None
            image_url = img_elem.get('src') if img_elem else ""
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(self.config.get('base_url', ''), image_url)
            
            # Availability
            availability_selector = selectors.get('availability', '')
            availability = True
            if availability_selector:
                availability_elem = container.select_one(availability_selector)
                if availability_elem:
                    availability_text = availability_elem.get_text().lower()
                    availability = 'out of stock' not in availability_text and 'unavailable' not in availability_text
            
            return {
                'name': name,
                'price': price,
                'url': url,
                'image_url': image_url,
                'availability': availability,
                'marketplace': config.get('marketplace', 'other')
            }
            
        except Exception as e:
            logger.error(f"Error parsing generic product container: {str(e)}")
            return None
    
    def close(self):
        """Close any open resources."""
        if self.selenium_engine:
            self.selenium_engine.close()
            self.selenium_engine = None


def get_scraping_engine(website_config: Dict[str, Any]) -> BaseScrapingEngine:
    """Factory function to get the appropriate scraping engine."""
    marketplace = website_config.get('marketplace', 'other').lower()
    use_selenium = website_config.get('use_selenium', False)
    fallback_to_selenium = website_config.get('fallback_to_selenium', True)
    
    # Check if we should use hybrid approach
    if use_selenium or fallback_to_selenium:
        return HybridScrapingEngine(website_config)
    
    # Use specific engines for known marketplaces
    if marketplace == 'amazon':
        return AmazonScrapingEngine(website_config)
    elif marketplace == 'ebay':
        return EbayScrapingEngine(website_config)
    elif marketplace == 'walmart':
        return WalmartScrapingEngine(website_config)
    else:
        return GenericScrapingEngine(website_config)
