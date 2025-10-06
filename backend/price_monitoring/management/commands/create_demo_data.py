from django.core.management.base import BaseCommand
from apps.products.models import RegulatedProduct
from apps.scraping.models import ScrapedProduct, ScrapingJob
from apps.violations.models import Violation
from apps.cases.models import Case
from apps.accounts.models import User
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Create demo data for testing'

    def handle(self, *args, **options):
        # Create demo products
        products_data = [
            {
                'name': 'Essential Medicine - Paracetamol 500mg',
                'category': 'Pharmaceuticals',
                'gov_price': Decimal('2.50'),
                'description': 'Government regulated price for essential medicine',
                'unit': 'tablet'
            },
            {
                'name': 'Basic Food Item - Rice 1kg',
                'category': 'Food',
                'gov_price': Decimal('1.20'),
                'description': 'Government regulated price for basic food item',
                'unit': 'kg'
            },
            {
                'name': 'Fuel - Petrol per liter',
                'category': 'Fuel',
                'gov_price': Decimal('0.85'),
                'description': 'Government regulated fuel price',
                'unit': 'liter'
            },
            {
                'name': 'Educational Book - Primary School',
                'category': 'Education',
                'gov_price': Decimal('5.00'),
                'description': 'Government regulated price for educational materials',
                'unit': 'book'
            },
            {
                'name': 'Public Transport - Bus Ticket',
                'category': 'Transport',
                'gov_price': Decimal('0.50'),
                'description': 'Government regulated public transport fare',
                'unit': 'ticket'
            }
        ]

        created_products = []
        for product_data in products_data:
            product, created = RegulatedProduct.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                created_products.append(product)
                self.stdout.write(f'Created product: {product.name}')

        # Create demo scraped products
        marketplaces = ['amazon', 'ebay', 'walmart', 'target']
        scraped_products = []
        
        for product in created_products:
            for marketplace in marketplaces:
                # Simulate some products being overpriced
                if random.random() > 0.6:  # 40% chance of violation
                    listed_price = product.gov_price * Decimal(random.uniform(1.1, 2.0))
                else:
                    listed_price = product.gov_price * Decimal(random.uniform(0.8, 1.1))
                
                scraped_product = ScrapedProduct.objects.create(
                    product_name=f"{product.name} - {marketplace.title()}",
                    marketplace=marketplace,
                    listed_price=listed_price,
                    url=f"https://{marketplace}.com/product/{random.randint(1000, 9999)}",
                    image_url=f"https://example.com/images/{random.randint(1, 100)}.jpg",
                    description=f"Found on {marketplace} marketplace",
                    availability=True
                )
                scraped_products.append(scraped_product)

        self.stdout.write(f'Created {len(scraped_products)} scraped products')

        # Create violations for overpriced items
        violations_created = 0
        for scraped_product in scraped_products:
            # Find the corresponding regulated product
            regulated_product = None
            for product in created_products:
                if product.name in scraped_product.product_name:
                    regulated_product = product
                    break
            
            if regulated_product and scraped_product.listed_price > regulated_product.gov_price:
                # Calculate violation severity
                price_difference = scraped_product.listed_price - regulated_product.gov_price
                percentage_over = (price_difference / regulated_product.gov_price) * 100
                
                if percentage_over <= 20:
                    severity = 'low'
                    proposed_penalty = 100
                elif percentage_over <= 50:
                    severity = 'medium'
                    proposed_penalty = 500
                else:
                    severity = 'high'
                    proposed_penalty = 1000
                
                violation = Violation.objects.create(
                    regulated_product=regulated_product,
                    scraped_product=scraped_product,
                    violation_type='price_exceeded',
                    severity=severity,
                    proposed_penalty=proposed_penalty,
                    status='pending'
                )
                violations_created += 1

        self.stdout.write(f'Created {violations_created} violations')

        # Create some confirmed violations and cases
        investigator = User.objects.filter(role='investigator').first()
        if investigator and violations_created > 0:
            # Confirm some violations
            pending_violations = Violation.objects.filter(status='pending')[:3]
            for violation in pending_violations:
                violation.status = 'confirmed'
                violation.confirmed_by = investigator
                violation.save()
                
                # Create case
                Case.objects.create(
                    violation=violation,
                    investigator=investigator,
                    status='open',
                    notes=f"Case created from confirmed violation: {violation.violation_type}"
                )

        self.stdout.write('Created demo cases')

        # Create a scraping job
        scraping_job = ScrapingJob.objects.create(
            name='Demo Scraping Job',
            marketplace='amazon',
            status='completed',
            products_scraped=len(scraped_products),
            errors_count=0
        )

        self.stdout.write('Created demo scraping job')

        self.stdout.write(
            self.style.SUCCESS('Demo data creation completed!')
        )
