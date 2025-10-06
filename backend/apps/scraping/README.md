# Scraping System Documentation

## Overview

The scraping system is a fully functional web scraping solution for the Price Regulation Monitoring System. It allows administrators to configure target websites, define product lists, and automatically scrape product data to monitor price violations.

## Features

### 1. Website Configuration
- **ScrapingWebsite Model**: Configure target websites with custom scraping rules
- **Multiple Engines**: Built-in engines for Amazon, eBay, Walmart, and generic websites
- **Custom Selectors**: CSS selectors for parsing different website structures
- **Rate Limiting**: Configurable delays between requests
- **Custom Headers**: Support for custom HTTP headers

### 2. Product Management
- **ProductSearchList Model**: Define lists of products to search for
- **Flexible Product Lists**: JSON-based product lists for easy management
- **Admin Interface**: Full Django admin support for managing products

### 3. Scraping Jobs
- **Background Processing**: Celery-based asynchronous scraping
- **Job Tracking**: Monitor scraping progress and status
- **Error Handling**: Comprehensive error logging and recovery
- **Cancellation**: Ability to cancel running jobs

### 4. Data Collection
- **Comprehensive Data**: Product name, price, URL, images, ratings, availability
- **Violation Detection**: Automatic price violation detection
- **Data Persistence**: All scraped data stored in database

## Models

### ScrapingWebsite
```python
- name: Website name
- base_url: Base URL of the website
- search_url_template: URL template with {query} placeholder
- is_active: Whether the website is active
- scraping_config: JSON configuration for scraping rules
- rate_limit_delay: Delay between requests (seconds)
- headers: Custom HTTP headers
```

### ProductSearchList
```python
- name: List name
- description: Description of the product list
- products: JSON array of product names to search
- is_active: Whether the list is active
- created_by: User who created the list
```

### ScrapedProduct
```python
- product_name: Name of the scraped product
- marketplace: Marketplace type (amazon, ebay, walmart, other)
- website: Reference to ScrapingWebsite
- search_query: Original search query used
- listed_price: Current price
- original_price: Original price before discounts
- url: Product URL
- image_url: Product image URL
- description: Product description
- availability: Whether product is available
- stock_status: Stock status text
- seller_name: Seller name
- rating: Product rating
- review_count: Number of reviews
- scraping_job: Reference to the scraping job
```

### ScrapingJob
```python
- name: Job name
- website: Target website
- product_list: Product list to search
- marketplace: Marketplace type
- status: Job status (pending, running, completed, failed, cancelled)
- products_scraped: Number of products scraped
- products_found: Number of products found
- errors_count: Number of errors encountered
- created_by: User who created the job
- task_id: Celery task ID
```

## API Endpoints

### Scraped Products
- `GET /api/scraping/results/` - List scraped products
- Query parameters: marketplace, website, availability, search, date_from, date_to, min_price, max_price

### Scraping Jobs
- `GET /api/scraping/jobs/` - List scraping jobs
- `POST /api/scraping/jobs/` - Create new scraping job
- `GET /api/scraping/jobs/{id}/` - Get job details
- `PATCH /api/scraping/jobs/{id}/` - Update job status
- `POST /api/scraping/jobs/{id}/cancel/` - Cancel running job

### Websites
- `GET /api/scraping/websites/` - List websites
- `POST /api/scraping/websites/` - Create website
- `GET /api/scraping/websites/{id}/` - Get website details
- `PUT /api/scraping/websites/{id}/` - Update website
- `DELETE /api/scraping/websites/{id}/` - Delete website
- `GET /api/scraping/websites/{id}/test/` - Test website scraping

### Product Lists
- `GET /api/scraping/product-lists/` - List product lists
- `POST /api/scraping/product-lists/` - Create product list
- `GET /api/scraping/product-lists/{id}/` - Get product list details
- `PUT /api/scraping/product-lists/{id}/` - Update product list
- `DELETE /api/scraping/product-lists/{id}/` - Delete product list

### Utility Endpoints
- `GET /api/scraping/stats/` - Get scraping statistics
- `POST /api/scraping/trigger/` - Manually trigger scraping
- `POST /api/scraping/cleanup/` - Clean up old data

## Usage Examples

### 1. Setting Up a Website

```python
# Create a new website configuration
website = ScrapingWebsite.objects.create(
    name="My Store",
    base_url="https://mystore.com",
    search_url_template="https://mystore.com/search?q={query}",
    is_active=True,
    rate_limit_delay=1.0,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    scraping_config={
        'marketplace': 'other',
        'product_container_selector': '.product-item',
        'selectors': {
            'name': '.product-name',
            'price': '.product-price',
            'url': '.product-link',
            'image': '.product-image'
        }
    }
)
```

### 2. Creating a Product List

```python
# Create a product search list
product_list = ProductSearchList.objects.create(
    name="Essential Products",
    description="List of essential products to monitor",
    products=[
        "Rice 1kg",
        "Wheat Flour 1kg",
        "Cooking Oil 1L",
        "Sugar 1kg"
    ],
    is_active=True,
    created_by=admin_user
)
```

### 3. Starting a Scraping Job

```python
# Create and start a scraping job
job = ScrapingJob.objects.create(
    name="Daily Price Check",
    website=website,
    product_list=product_list,
    marketplace="other",
    created_by=admin_user
)

# Start the scraping task
from apps.scraping.tasks import scrape_marketplace
task = scrape_marketplace.delay(job.id)
job.task_id = task.id
job.save()
```

### 4. Testing Website Configuration

```python
# Test a website configuration
from apps.scraping.scraping_engines import get_scraping_engine

website_config = {
    'base_url': website.base_url,
    'search_url_template': website.search_url_template,
    'scraping_config': website.scraping_config,
    'rate_limit_delay': website.rate_limit_delay,
    'headers': website.headers,
    'marketplace': 'other'
}

engine = get_scraping_engine(website_config)
results = engine.search_products("test product", max_results=5)
```

## Scraping Engines

### Built-in Engines

1. **AmazonScrapingEngine**: Optimized for Amazon.com
2. **EbayScrapingEngine**: Optimized for eBay.com
3. **WalmartScrapingEngine**: Optimized for Walmart.com
4. **GenericScrapingEngine**: For custom websites with configurable selectors

### Creating Custom Engines

```python
class CustomScrapingEngine(BaseScrapingEngine):
    def search_products(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        # Implement custom scraping logic
        search_url = f"https://custom-site.com/search?q={quote_plus(query)}"
        response = self.make_request(search_url)
        # Parse response and return product data
        return products
```

## Error Handling

The system includes comprehensive error handling:

- **Request Failures**: Automatic retries with exponential backoff
- **Parsing Errors**: Graceful handling of malformed HTML
- **Rate Limiting**: Respects website rate limits
- **Job Failures**: Detailed error logging and status tracking

## Performance Considerations

- **Rate Limiting**: Configurable delays between requests
- **Batch Processing**: Processes multiple products in single jobs
- **Data Cleanup**: Automatic cleanup of old scraped data
- **Caching**: Session-based request caching

## Security Features

- **User Permissions**: Only admins can create/modify scraping configurations
- **Input Validation**: Comprehensive validation of all inputs
- **SQL Injection Protection**: Django ORM protection
- **XSS Protection**: Proper HTML escaping

## Monitoring and Logging

- **Comprehensive Logging**: All scraping activities logged
- **Job Status Tracking**: Real-time job status updates
- **Error Reporting**: Detailed error messages and stack traces
- **Performance Metrics**: Scraping statistics and performance data

## Setup Instructions

1. **Install Dependencies**: Ensure all required packages are installed
2. **Run Migrations**: Apply database migrations
3. **Setup Default Websites**: Run the setup command
4. **Configure Celery**: Ensure Celery is running for background tasks
5. **Create Product Lists**: Set up initial product lists
6. **Test Configuration**: Test website configurations before production use

## Management Commands

```bash
# Setup default website configurations
python manage.py setup_default_websites

# Clean up old scraped data
python manage.py shell
>>> from apps.scraping.tasks import cleanup_old_scraped_products
>>> cleanup_old_scraped_products.delay(30)  # Clean data older than 30 days
```

## Best Practices

1. **Respect Rate Limits**: Always configure appropriate delays
2. **Monitor Jobs**: Regularly check job status and errors
3. **Test Configurations**: Test website configurations before production
4. **Regular Cleanup**: Clean up old data to manage database size
5. **Error Monitoring**: Monitor logs for scraping errors
6. **Backup Data**: Regular backups of scraped data

## Troubleshooting

### Common Issues

1. **No Products Found**: Check website selectors and URL templates
2. **Rate Limiting**: Increase delay between requests
3. **Parsing Errors**: Verify CSS selectors are correct
4. **Job Failures**: Check error messages in job details
5. **Permission Errors**: Ensure user has admin permissions

### Debug Mode

Enable debug logging for detailed scraping information:

```python
import logging
logging.getLogger('apps.scraping').setLevel(logging.DEBUG)
```

## Future Enhancements

- **Machine Learning**: AI-powered product matching
- **Proxy Support**: Rotating proxy support for large-scale scraping
- **Scheduled Jobs**: Automatic scheduled scraping
- **Data Export**: Export scraped data to various formats
- **Real-time Monitoring**: WebSocket-based real-time updates
