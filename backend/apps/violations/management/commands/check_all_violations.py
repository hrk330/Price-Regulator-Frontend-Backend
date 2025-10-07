from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decimal import Decimal
from apps.scraping.models import ScrapedProduct
from apps.products.models import RegulatedProduct
from apps.violations.models import Violation, ViolationCheckReport
from apps.scraping.tasks import is_product_match
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check all existing scraped products for price violations against regulated products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing violation check reports before running new check',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of scraped products to check (for testing)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting comprehensive violation check...')
        )
        
        # Clear existing reports if requested
        if options['clear_existing']:
            if options['dry_run']:
                count = ViolationCheckReport.objects.count()
                self.stdout.write(f"Would clear {count} existing violation check reports")
            else:
                count = ViolationCheckReport.objects.count()
                ViolationCheckReport.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(f"Cleared {count} existing violation check reports")
                )
        
        # Get all scraped products
        scraped_products = ScrapedProduct.objects.all()
        if options['limit']:
            scraped_products = scraped_products[:options['limit']]
        
        total_scraped = scraped_products.count()
        self.stdout.write(f"Checking {total_scraped} scraped products...")
        
        # Get all regulated products
        regulated_products = RegulatedProduct.objects.filter(is_active=True)
        total_regulated = regulated_products.count()
        self.stdout.write(f"Against {total_regulated} regulated products...")
        
        if total_scraped == 0:
            raise CommandError('No scraped products found in database')
        
        if total_regulated == 0:
            raise CommandError('No active regulated products found in database')
        
        # Statistics
        stats = {
            'total_checked': 0,
            'violations_found': 0,
            'compliant_products': 0,
            'no_matches': 0,
            'new_violations_created': 0,
            'reports_created': 0,
        }
        
        # Process each scraped product with batch optimization
        batch_size = 50
        processed_count = 0
        
        for i, scraped_product in enumerate(scraped_products, 1):
            if i % 10 == 0:  # Show progress every 10 products
                self.stdout.write(f"[{i}/{total_scraped}] Checking: {scraped_product.product_name}")
            
            best_match = None
            best_match_score = 0
            
            # Find best matching regulated product
            for regulated_product in regulated_products:
                if is_product_match(scraped_product.product_name, regulated_product.name):
                    # Calculate match score (simple scoring for now)
                    score = self._calculate_match_score(
                        scraped_product.product_name, 
                        regulated_product.name
                    )
                    if score > best_match_score:
                        best_match = regulated_product
                        best_match_score = score
            
            # Create violation check report
            if best_match:
                report_data = self._create_violation_report(
                    scraped_product, best_match, options['dry_run']
                )
                stats['reports_created'] += 1
                
                if report_data['has_violation']:
                    stats['violations_found'] += 1
                    if report_data.get('violation_created'):
                        stats['new_violations_created'] += 1
                else:
                    stats['compliant_products'] += 1
            else:
                # No matching regulated product found
                if not options['dry_run']:
                    ViolationCheckReport.objects.create(
                        scraped_product=scraped_product,
                        compliance_status='no_match',
                        notes=f"No matching regulated product found for '{scraped_product.product_name}'"
                    )
                stats['no_matches'] += 1
                stats['reports_created'] += 1
            
            stats['total_checked'] += 1
        
        # Display results
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('VIOLATION CHECK COMPLETED'))
        self.stdout.write('='*60)
        self.stdout.write(f"Total Products Checked: {stats['total_checked']}")
        self.stdout.write(f"Violations Found: {stats['violations_found']}")
        self.stdout.write(f"Compliant Products: {stats['compliant_products']}")
        self.stdout.write(f"No Matching Regulated Product: {stats['no_matches']}")
        self.stdout.write(f"New Violation Records Created: {stats['new_violations_created']}")
        self.stdout.write(f"Check Reports Created: {stats['reports_created']}")
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('\nThis was a DRY RUN - no changes were made to the database')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll changes have been saved to the database')
            )
            self.stdout.write(
                'You can now view the results in Django admin under "Violation Check Reports"'
            )

    def _calculate_match_score(self, scraped_name, regulated_name):
        """Calculate a simple match score between two product names."""
        import difflib
        
        # Normalize names
        scraped_norm = scraped_name.lower().strip()
        regulated_norm = regulated_name.lower().strip()
        
        # Calculate similarity
        similarity = difflib.SequenceMatcher(None, scraped_norm, regulated_norm).ratio()
        
        # Boost score for keyword matches
        scraped_words = set(scraped_norm.split())
        regulated_words = set(regulated_norm.split())
        common_words = scraped_words.intersection(regulated_words)
        
        if common_words:
            keyword_boost = len(common_words) / max(len(scraped_words), len(regulated_words))
            similarity += keyword_boost * 0.3
        
        return similarity

    def _create_violation_report(self, scraped_product, regulated_product, dry_run=False):
        """Create a violation check report for a matched product pair."""
        violation_threshold = regulated_product.price_violation_threshold
        scraped_price = scraped_product.listed_price
        regulated_price = regulated_product.gov_price
        
        # Calculate differences
        price_difference = scraped_price - regulated_price
        percentage_difference = (price_difference / regulated_price) * 100 if regulated_price > 0 else 0
        
        # Determine compliance status
        has_violation = scraped_price > violation_threshold
        compliance_status = 'violation' if has_violation else 'ok'
        
        # Calculate severity and penalty if violation
        violation_severity = None
        proposed_penalty = None
        
        if has_violation:
            if percentage_difference <= 20:
                violation_severity = 'low'
                proposed_penalty = Decimal('100')
            elif percentage_difference <= 50:
                violation_severity = 'medium'
                proposed_penalty = Decimal('500')
            elif percentage_difference <= 100:
                violation_severity = 'high'
                proposed_penalty = Decimal('1000')
            else:
                violation_severity = 'critical'
                proposed_penalty = Decimal('2000')
        
        # Create notes
        notes = f"Scraped: Rs.{scraped_price} | Regulated: Rs.{regulated_price} | "
        notes += f"Difference: Rs.{price_difference} ({percentage_difference:.1f}%)"
        
        if has_violation:
            notes += f" | Severity: {violation_severity} | Penalty: Rs.{proposed_penalty}"
        
        violation_created = False
        
        if not dry_run:
            # Create or update violation check report
            report, created = ViolationCheckReport.objects.get_or_create(
                regulated_product=regulated_product,
                scraped_product=scraped_product,
                defaults={
                    'has_violation': has_violation,
                    'compliance_status': compliance_status,
                    'price_difference': price_difference,
                    'percentage_difference': Decimal(str(round(percentage_difference, 2))),
                    'violation_severity': violation_severity,
                    'proposed_penalty': proposed_penalty,
                    'notes': notes,
                }
            )
            
            # Create violation record if needed
            if has_violation:
                violation, violation_created = Violation.objects.get_or_create(
                    regulated_product=regulated_product,
                    scraped_product=scraped_product,
                    status='pending',
                    defaults={
                        'violation_type': 'price_exceeded',
                        'severity': violation_severity,
                        'proposed_penalty': proposed_penalty,
                        'notes': notes,
                    }
                )
                
                if violation_created:
                    report.violation_record = violation
                    report.save()
        else:
            # Dry run - just show what would be created
            self.stdout.write(f"  Would create report: {compliance_status}")
            if has_violation:
                self.stdout.write(f"  Would create violation: {violation_severity} severity")
                violation_created = True
        
        return {
            'has_violation': has_violation,
            'compliance_status': compliance_status,
            'violation_created': violation_created,
        }
