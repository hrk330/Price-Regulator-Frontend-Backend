"""
PDF Rate List Processing Service
Extracts product information from government rate list PDFs.
"""
import re
import logging
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional
import pdfplumber
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


class PDFRateListProcessor:
    """Process PDF rate lists to extract product information."""
    
    def __init__(self):
        self.products = []
        self.errors = []
    
    def process_pdf(self, pdf_file: UploadedFile) -> Dict[str, Any]:
        """
        Process uploaded PDF file and extract product information.
        
        Args:
            pdf_file: Uploaded PDF file
            
        Returns:
            Dict containing extracted products and processing results
        """
        try:
            # Read PDF content
            with pdfplumber.open(pdf_file) as pdf:
                all_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        all_text += page_text + "\n"
            
            # Extract products from text
            products = self._extract_products_from_text(all_text)
            
            return {
                'success': True,
                'products': products,
                'total_products': len(products),
                'errors': self.errors
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return {
                'success': False,
                'products': [],
                'total_products': 0,
                'errors': [f"Failed to process PDF: {str(e)}"]
            }
    
    def _extract_products_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract product information from PDF text."""
        products = []
        lines = text.split('\n')
        
        # Common patterns for government rate lists
        patterns = [
            # Pattern 1: Product Name Packaging Price (most common format)
            r'^(.+?)\s+(\d+(?:\s*kg|\s*liter|\s*piece|\s*gram|\s*ton)?)\s+([\d,]+(?:\.\d{2})?)\s*$',
            # Pattern 2: Product Name - Price (Rs. format)
            r'^(.+?)\s+-\s+Rs\.?\s*([\d,]+(?:\.\d{2})?)\s*$',
            # Pattern 3: Product Name Price (without Rs.)
            r'^(.+?)\s+([\d,]+(?:\.\d{2})?)\s*$',
            # Pattern 4: Product Name | Price
            r'^(.+?)\s*\|\s*([\d,]+(?:\.\d{2})?)\s*$',
            # Pattern 5: Product Name: Price
            r'^(.+?):\s*([\d,]+(?:\.\d{2})?)\s*$',
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:  # Skip empty or very short lines
                continue
            
            # Skip headers and footers
            if self._is_header_or_footer(line):
                continue
            
            # Try each pattern
            for i, pattern in enumerate(patterns):
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    if i == 0:  # Pattern 1: Product Name Packaging Price
                        product_name = match.group(1).strip()
                        packaging = match.group(2).strip()
                        price_str = match.group(3).strip()
                    else:  # Other patterns: Product Name Price
                        product_name = match.group(1).strip()
                        price_str = match.group(2).strip()
                        packaging = ""
                    
                    # Clean and validate product name
                    product_name = self._clean_product_name(product_name)
                    if not product_name or len(product_name) < 3:
                        continue
                    
                    # Parse price
                    price = self._parse_price(price_str)
                    if price is None:
                        continue
                    
                    # Determine category
                    category = self._determine_category(product_name)
                    
                    # Determine unit from packaging or product name
                    unit = self._determine_unit_from_packaging(packaging) or self._determine_unit(product_name)
                    
                    # Create product entry
                    product = {
                        'name': product_name,
                        'gov_price': price,
                        'category': category,
                        'description': f"Government regulated price for {product_name}",
                        'unit': unit,
                        'source_line': line
                    }
                    
                    # Avoid duplicates
                    if not self._is_duplicate(product, products):
                        products.append(product)
                    
                    break  # Found a match, move to next line
        
        return products
    
    def _clean_product_name(self, name: str) -> str:
        """Clean and normalize product name."""
        # Remove common prefixes/suffixes
        name = re.sub(r'^(Sr\.?\s*No\.?\s*\d+\.?\s*)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^(No\.?\s*\d+\.?\s*)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^(Item\s*\d+\.?\s*)', '', name, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove trailing punctuation
        name = re.sub(r'[.,;:]+$', '', name)
        
        return name
    
    def _parse_price(self, price_str: str) -> Optional[Decimal]:
        """Parse price string to Decimal."""
        try:
            # Remove commas and currency symbols
            price_clean = re.sub(r'[^\d.]', '', price_str)
            if not price_clean:
                return None
            
            price = Decimal(price_clean)
            # Validate reasonable price range (1 to 1,000,000)
            if 1 <= price <= 1000000:
                return price
            return None
            
        except (InvalidOperation, ValueError):
            return None
    
    def _determine_category(self, product_name: str) -> str:
        """Determine product category based on name."""
        name_lower = product_name.lower()
        
        # Food items
        if any(word in name_lower for word in ['wheat', 'rice', 'flour', 'sugar', 'salt', 'oil', 'ghee', 'milk', 'bread']):
            return 'Food Items'
        
        # Agricultural products
        if any(word in name_lower for word in ['fertilizer', 'seed', 'pesticide', 'urea', 'dap', 'npk']):
            return 'Agricultural Products'
        
        # Medicines
        if any(word in name_lower for word in ['tablet', 'medicine', 'syrup', 'injection', 'capsule']):
            return 'Medicines'
        
        # Fuel
        if any(word in name_lower for word in ['petrol', 'diesel', 'gas', 'fuel']):
            return 'Fuel'
        
        # Construction materials
        if any(word in name_lower for word in ['cement', 'steel', 'brick', 'sand']):
            return 'Construction Materials'
        
        # Default category
        return 'General'
    
    def _determine_unit_from_packaging(self, packaging: str) -> Optional[str]:
        """Determine product unit from packaging information."""
        if not packaging:
            return None
        
        packaging_lower = packaging.lower()
        
        if 'kg' in packaging_lower:
            return 'kg'
        elif any(word in packaging_lower for word in ['liter', 'litre', 'ltr']):
            return 'liter'
        elif any(word in packaging_lower for word in ['piece', 'pcs', 'unit']):
            return 'piece'
        elif any(word in packaging_lower for word in ['gram', 'gm', 'g']):
            return 'gram'
        elif any(word in packaging_lower for word in ['ton', 'tonne']):
            return 'ton'
        
        return None
    
    def _determine_unit(self, product_name: str) -> str:
        """Determine product unit based on name."""
        name_lower = product_name.lower()
        
        if any(word in name_lower for word in ['kg', 'kilogram', 'kilo']):
            return 'kg'
        elif any(word in name_lower for word in ['liter', 'litre', 'ltr']):
            return 'liter'
        elif any(word in name_lower for word in ['piece', 'pcs', 'unit']):
            return 'piece'
        elif any(word in name_lower for word in ['gram', 'gm', 'g']):
            return 'gram'
        elif any(word in name_lower for word in ['ton', 'tonne']):
            return 'ton'
        else:
            return 'piece'  # Default unit
    
    def _is_header_or_footer(self, line: str) -> bool:
        """Check if line is a header or footer."""
        line_lower = line.lower()
        
        # Common header/footer patterns
        header_footer_patterns = [
            'government', 'rate list', 'price list', 'schedule',
            'page', 'date', 'sr no', 'item no', 'description',
            'rate', 'price', 'amount', 'total', 'sub total',
            'signature', 'authorized', 'approved', 'department'
        ]
        
        return any(pattern in line_lower for pattern in header_footer_patterns)
    
    def _is_duplicate(self, new_product: Dict[str, Any], existing_products: List[Dict[str, Any]]) -> bool:
        """Check if product is duplicate."""
        new_name = new_product['name'].lower().strip()
        
        for existing in existing_products:
            existing_name = existing['name'].lower().strip()
            # Check for exact match or very similar names
            if new_name == existing_name or self._names_similar(new_name, existing_name):
                return True
        
        return False
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two product names are similar."""
        # Simple similarity check - can be enhanced with fuzzy matching
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        # If more than 70% of words match, consider similar
        if len(words1) > 0 and len(words2) > 0:
            common_words = words1.intersection(words2)
            similarity = len(common_words) / max(len(words1), len(words2))
            return similarity > 0.7
        
        return False


def process_rate_list_pdf(pdf_file: UploadedFile) -> Dict[str, Any]:
    """
    Convenience function to process a rate list PDF.
    
    Args:
        pdf_file: Uploaded PDF file
        
    Returns:
        Dict containing processing results
    """
    processor = PDFRateListProcessor()
    return processor.process_pdf(pdf_file)
