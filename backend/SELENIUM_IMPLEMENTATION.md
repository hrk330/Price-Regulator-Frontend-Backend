# Selenium Scraping Implementation

## Overview

This document describes the Selenium-based scraping implementation that has been added to the Price Regulation Monitoring System to handle websites with anti-scraping protection, specifically the Kissan Ghar website.

## Problem Solved

The Kissan Ghar website was returning encoded/protected content when accessed via direct HTTP requests, making it impossible to scrape product information. The Selenium implementation bypasses these protections by using a real browser to render JavaScript and handle dynamic content.

## Architecture

### 1. SeleniumScrapingEngine

A dedicated scraping engine that uses Selenium WebDriver to:
- Launch a real browser (Chrome or Firefox)
- Navigate to search pages
- Wait for dynamic content to load
- Parse product information using CSS selectors
- Handle anti-detection measures

### 2. HybridScrapingEngine

An intelligent engine that:
- First attempts direct HTTP requests (fast)
- Automatically detects protected content
- Falls back to Selenium if needed
- Provides the best of both worlds: speed and reliability

### 3. Enhanced Website Configuration

The `ScrapingWebsite` model now includes:
- `use_selenium`: Force Selenium usage
- `fallback_to_selenium`: Enable automatic fallback
- `selenium_config`: Selenium-specific settings

## Key Features

### Anti-Detection Measures
- Custom User-Agent headers
- Disabled automation indicators
- Random delays between actions
- Optimized browser options

### Performance Optimizations
- Headless mode for server environments
- Disabled images/CSS when possible
- Efficient element selection
- Proper resource cleanup

### Error Handling
- Automatic screenshots on errors
- Comprehensive logging
- Graceful fallbacks
- Resource cleanup

### Browser Support
- Chrome (primary)
- Firefox (fallback)
- Automatic WebDriver management

## Configuration

### Django Settings

```python
SELENIUM_CONFIG = {
    'HEADLESS': True,
    'BROWSER': 'chrome',  # 'chrome' or 'firefox'
    'IMPLICIT_WAIT': 10,
    'PAGE_LOAD_TIMEOUT': 30,
    'WINDOW_SIZE': (1920, 1080),
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'DISABLE_IMAGES': True,
    'DISABLE_CSS': False,
    'DISABLE_JS': False,
    'SCREENSHOT_ON_ERROR': True,
    'SCREENSHOT_DIR': BASE_DIR / 'logs' / 'screenshots',
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 2,
}
```

### Website Configuration

```python
{
    'name': 'Kissan Ghar',
    'base_url': 'https://www.kissanghar.pk/',
    'search_url_template': 'https://www.kissanghar.pk/?s={query}',
    'use_selenium': True,
    'fallback_to_selenium': True,
    'scraping_config': {
        'product_container_selector': '.product, .item, .woocommerce-loop-product__link',
        'selectors': {
            'name': 'h4, [class*="name"], .product-title',
            'price': '[class*="price"], .price, .cost',
            'url': 'a',
            'image': 'img'
        }
    },
    'selenium_config': {
        'headless': True,
        'implicit_wait': 10,
        'screenshot_on_error': True
    }
}
```

## Usage

### 1. Automatic Usage

The system automatically uses Selenium when:
- `use_selenium=True` is set for a website
- Direct requests fail and `fallback_to_selenium=True`

### 2. Manual Testing

```python
from apps.scraping.scraping_engines import HybridScrapingEngine

config = {
    'base_url': 'https://www.kissanghar.pk/',
    'search_url_template': 'https://www.kissanghar.pk/?s={query}',
    'use_selenium': True,
    'scraping_config': {
        'product_container_selector': '.product',
        'selectors': {
            'name': 'h4',
            'price': '.price',
            'url': 'a'
        }
    }
}

engine = HybridScrapingEngine(config)
products = engine.search_products("rice", max_results=10)
engine.close()  # Important: Always close the engine
```

### 3. Management Commands

```bash
# Enable Selenium for Kissan website
python manage.py update_kissan_selenium --use-selenium --fallback-selenium

# Disable Selenium
python manage.py update_kissan_selenium --disable-selenium
```

## Testing

### 1. Basic Setup Test

```bash
python test_selenium_simple.py
```

This tests:
- Selenium imports
- Engine creation
- Configuration validation

### 2. Full Browser Test

```bash
python test_selenium_kissan.py
```

This tests:
- Actual browser automation
- Product scraping
- Error handling

## Dependencies

### Required Packages

```
selenium==4.15.2
webdriver-manager==4.0.1
```

### System Requirements

- Chrome or Firefox browser
- ChromeDriver (automatically managed)
- GeckoDriver (automatically managed)

## Performance Considerations

### Speed vs Reliability Trade-offs

1. **Direct Requests (Fast)**
   - ~1-2 seconds per search
   - Limited by anti-scraping measures
   - Best for simple websites

2. **Selenium (Reliable)**
   - ~5-10 seconds per search
   - Bypasses most protections
   - Best for complex websites

3. **Hybrid Approach (Optimal)**
   - Tries direct first (fast)
   - Falls back to Selenium (reliable)
   - Best of both worlds

### Resource Usage

- **Memory**: ~100-200MB per browser instance
- **CPU**: Moderate during page loading
- **Network**: Standard HTTP traffic
- **Storage**: Screenshots and logs

## Troubleshooting

### Common Issues

1. **WebDriver Not Found**
   - Solution: webdriver-manager handles this automatically
   - Check internet connection for driver downloads

2. **Browser Crashes**
   - Solution: Enable screenshots for debugging
   - Check system resources

3. **Timeout Errors**
   - Solution: Increase `PAGE_LOAD_TIMEOUT`
   - Check network connectivity

4. **No Products Found**
   - Solution: Update CSS selectors
   - Check website structure changes

### Debug Mode

Set `headless=False` in selenium_config to see the browser in action:

```python
'selenium_config': {
    'headless': False,  # Shows browser window
    'screenshot_on_error': True
}
```

## Security Considerations

### Anti-Detection Features

- Randomized delays
- Custom User-Agent
- Disabled automation flags
- Natural browsing patterns

### Rate Limiting

- Respects website rate limits
- Configurable delays between requests
- Automatic retry with backoff

### Data Privacy

- No personal data collection
- Only public product information
- Respects robots.txt (when possible)

## Future Enhancements

### Planned Features

1. **Proxy Support**
   - Rotate IP addresses
   - Geographic distribution

2. **Advanced Anti-Detection**
   - Browser fingerprint randomization
   - CAPTCHA solving integration

3. **Performance Monitoring**
   - Success rate tracking
   - Performance metrics
   - Automatic optimization

4. **Multi-Browser Support**
   - Edge browser support
   - Safari support (macOS)

## Monitoring and Logging

### Log Files

- `logs/django.log`: General application logs
- `logs/screenshots/`: Error screenshots
- Celery logs: Background task logs

### Key Metrics

- Success rate per website
- Average response time
- Error frequency
- Resource usage

## Conclusion

The Selenium implementation provides a robust solution for scraping websites with anti-scraping protection. The hybrid approach ensures optimal performance while maintaining reliability. The system is designed to be easily configurable and maintainable, with comprehensive error handling and monitoring capabilities.

For the Kissan Ghar website specifically, this implementation successfully bypasses the encoded content protection and enables reliable product data extraction.
