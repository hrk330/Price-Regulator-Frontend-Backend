"""
Web scraping engines for different websites.
Each engine handles the specific structure and parsing logic for different e-commerce sites.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from urllib.parse import urljoin, quote_plus
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Any

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
        
    def parse_price(self, price_text: str) -> Optional[Decimal]:
        """Parse price from text."""
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
            return Decimal(price_clean) if price_clean else None
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
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
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


def get_scraping_engine(website_config: Dict[str, Any]) -> BaseScrapingEngine:
    """Factory function to get the appropriate scraping engine."""
    marketplace = website_config.get('marketplace', 'other').lower()
    
    if marketplace == 'amazon':
        return AmazonScrapingEngine(website_config)
    elif marketplace == 'ebay':
        return EbayScrapingEngine(website_config)
    elif marketplace == 'walmart':
        return WalmartScrapingEngine(website_config)
    else:
        return GenericScrapingEngine(website_config)
