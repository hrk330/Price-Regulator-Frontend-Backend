"""
Management command to update Kissan website configuration for Selenium.
"""

from django.core.management.base import BaseCommand
from apps.scraping.models import ScrapingWebsite


class Command(BaseCommand):
    help = 'Update Kissan website configuration to use Selenium'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use-selenium',
            action='store_true',
            help='Enable Selenium for Kissan website',
        )
        parser.add_argument(
            '--fallback-selenium',
            action='store_true',
            help='Enable fallback to Selenium if direct requests fail',
        )
        parser.add_argument(
            '--disable-selenium',
            action='store_true',
            help='Disable Selenium for Kissan website',
        )

    def handle(self, *args, **options):
        try:
            # Find Kissan website
            kissan_website = ScrapingWebsite.objects.filter(
                name__icontains='kissan'
            ).first()
            
            if not kissan_website:
                self.stdout.write(
                    self.style.ERROR('Kissan website not found in database')
                )
                return
            
            self.stdout.write(f"Found Kissan website: {kissan_website.name}")
            self.stdout.write(f"Current URL: {kissan_website.base_url}")
            
            # Update configuration based on options
            if options['disable_selenium']:
                kissan_website.use_selenium = False
                kissan_website.fallback_to_selenium = False
                self.stdout.write(
                    self.style.WARNING('Disabling Selenium for Kissan website')
                )
            else:
                if options['use_selenium']:
                    kissan_website.use_selenium = True
                    self.stdout.write(
                        self.style.SUCCESS('Enabling Selenium for Kissan website')
                    )
                
                if options['fallback_selenium']:
                    kissan_website.fallback_to_selenium = True
                    self.stdout.write(
                        self.style.SUCCESS('Enabling fallback to Selenium')
                    )
            
            # Update scraping configuration for better Selenium support
            scraping_config = kissan_website.scraping_config or {}
            
            # Enhanced selectors for Kissan
            scraping_config.update({
                'selectors': {
                    'url': 'a',
                    'name': 'h4, [class*="name"], .product-title, .item-title, .woocommerce-loop-product__title',
                    'image': 'img',
                    'price': '[class*="price"], .price, .cost, .amount, .woocommerce-Price-amount',
                    'availability': '.stock, .availability, [class*="stock"], .woocommerce-loop-product__availability'
                },
                'pagination': {
                    'next_page': '.pagination-next, .next-page, a:contains("Next")'
                },
                'marketplace': 'other',
                'search_params': {
                    'query_param': 's'
                },
                'product_container_selector': '.product'
            })
            
            kissan_website.scraping_config = scraping_config
            
            # Add Selenium-specific configuration
            selenium_config = {
                'headless': True,  # Set to False for debugging
                'implicit_wait': 10,
                'page_load_timeout': 30,
                'screenshot_on_error': True,
                'disable_images': True,  # Speed up loading
                'disable_css': False,    # Keep CSS for proper layout
                'disable_js': False      # Keep JS for dynamic content
            }
            
            kissan_website.selenium_config = selenium_config
            
            # Update headers for better compatibility (working headers from our tests)
            working_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            kissan_website.headers = working_headers
            
            # Save changes
            kissan_website.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated Kissan website configuration:\n'
                    f'- Use Selenium: {kissan_website.use_selenium}\n'
                    f'- Fallback to Selenium: {kissan_website.fallback_to_selenium}\n'
                    f'- Product container selector: {scraping_config.get("product_container_selector", "Not set")}\n'
                    f'- Selenium config: {len(selenium_config)} settings'
                )
            )
            
            # Show current configuration
            self.stdout.write('\nCurrent configuration:')
            self.stdout.write(f'  Name: {kissan_website.name}')
            self.stdout.write(f'  Base URL: {kissan_website.base_url}')
            self.stdout.write(f'  Search URL: {kissan_website.search_url_template}')
            self.stdout.write(f'  Use Selenium: {kissan_website.use_selenium}')
            self.stdout.write(f'  Fallback to Selenium: {kissan_website.fallback_to_selenium}')
            self.stdout.write(f'  Rate limit delay: {kissan_website.rate_limit_delay}s')
            self.stdout.write(f'  Is active: {kissan_website.is_active}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating Kissan configuration: {str(e)}')
            )
            raise
