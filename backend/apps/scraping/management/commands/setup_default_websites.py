"""
Management command to set up default website configurations for scraping.
"""

from django.core.management.base import BaseCommand
from apps.scraping.models import ScrapingWebsite


class Command(BaseCommand):
    help = 'Set up default website configurations for scraping'

    def handle(self, *args, **options):
        """Create default website configurations."""
        
        default_websites = [
            {
                'name': 'Amazon',
                'base_url': 'https://www.amazon.com',
                'search_url_template': 'https://www.amazon.com/s?k={query}',
                'is_active': True,
                'rate_limit_delay': 2.0,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                'scraping_config': {
                    'marketplace': 'amazon',
                    'product_container_selector': 'div[data-component-type="s-search-result"]',
                    'selectors': {
                        'name': 'h2.a-size-mini, span.a-size-medium',
                        'price': 'span.a-price-whole, span.a-offscreen',
                        'url': 'h2.a-size-mini a, a.a-link-normal',
                        'image': 'img.s-image'
                    }
                }
            },
            {
                'name': 'eBay',
                'base_url': 'https://www.ebay.com',
                'search_url_template': 'https://www.ebay.com/sch/i.html?_nkw={query}',
                'is_active': True,
                'rate_limit_delay': 1.5,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                'scraping_config': {
                    'marketplace': 'ebay',
                    'product_container_selector': 'div.s-item',
                    'selectors': {
                        'name': 'h3.s-item__title',
                        'price': 'span.s-item__price',
                        'url': 'a.s-item__link',
                        'image': 'img.s-item__image'
                    }
                }
            },
            {
                'name': 'Walmart',
                'base_url': 'https://www.walmart.com',
                'search_url_template': 'https://www.walmart.com/search?q={query}',
                'is_active': True,
                'rate_limit_delay': 2.0,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                'scraping_config': {
                    'marketplace': 'walmart',
                    'product_container_selector': 'div[data-testid="item-stack"]',
                    'selectors': {
                        'name': 'span[data-automation-id="product-title"]',
                        'price': 'span[data-automation-id="product-price"]',
                        'url': 'a[data-automation-id="product-title"]',
                        'image': 'img[data-testid="product-image"]'
                    }
                }
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for website_data in default_websites:
            website, created = ScrapingWebsite.objects.get_or_create(
                name=website_data['name'],
                defaults=website_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created website: {website.name}')
                )
            else:
                # Update existing website with new configuration
                for key, value in website_data.items():
                    if key != 'name':
                        setattr(website, key, value)
                website.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated website: {website.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Setup complete! Created: {created_count}, Updated: {updated_count}'
            )
        )
