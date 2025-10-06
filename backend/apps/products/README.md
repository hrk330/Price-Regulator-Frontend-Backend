# Products App - PDF Rate List Import Feature

## 🎯 Overview

The Products app now includes a powerful PDF rate list import feature that allows administrators to upload government rate list PDFs and automatically extract product information to create `RegulatedProduct` entries.

## 🚀 Features

### **1. PDF Rate List Upload**
- Upload government rate list PDFs
- Automatic text extraction and parsing
- Smart product name cleaning and normalization
- Automatic category detection
- Price parsing and validation
- Unit detection based on product names

### **2. Admin Interface**
- Upload PDFs through Django admin
- Preview processing results before importing
- Process uploads with one click
- View detailed processing statistics
- Track upload history and success rates

### **3. API Endpoints**
- `POST /api/products/upload-rate-list/` - Upload and process PDF
- `POST /api/products/preview-pdf-processing/` - Preview without importing
- `GET /api/products/rate-list-uploads/` - List upload history
- `GET /api/products/stats/` - Get processing statistics

## 📋 How to Use

### **Via Django Admin:**

1. **Navigate to Admin Panel**
   - Go to `http://127.0.0.1:8000/admin/`
   - Login with admin credentials

2. **Upload Rate List**
   - Go to "Products" → "Rate List Uploads"
   - Click "Add Rate List Upload"
   - Fill in the name and upload PDF file
   - Click "Save"

3. **Process the Upload**
   - Go to the uploaded rate list
   - Click "Preview" to see what will be imported
   - Click "Process" to import products

### **Via API:**

```python
import requests

# Upload and process PDF
files = {'pdf_file': open('rate_list.pdf', 'rb')}
data = {'name': 'Government Rate List 2025'}

response = requests.post(
    'http://127.0.0.1:8000/api/products/upload-rate-list/',
    files=files,
    data=data,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

print(response.json())
```

## 🔧 Technical Details

### **PDF Processing Engine**

The `PDFRateListProcessor` class handles:

1. **Text Extraction**: Uses `pdfplumber` to extract text from PDFs
2. **Pattern Matching**: Multiple regex patterns to identify product-price pairs
3. **Data Cleaning**: Removes headers, footers, and normalizes text
4. **Category Detection**: Smart categorization based on product names
5. **Unit Detection**: Automatic unit detection (kg, liter, piece, etc.)
6. **Duplicate Prevention**: Avoids importing duplicate products

### **Supported Patterns**

The processor recognizes these patterns:
- `Product Name - Rs. Price`
- `Product Name Price`
- `Product Name | Price`
- `Product Name: Price`

### **Category Detection**

Products are automatically categorized into:
- **Food Items**: wheat, rice, flour, sugar, salt, oil, ghee, milk, bread
- **Agricultural Products**: fertilizer, seed, pesticide, urea, dap, npk
- **Medicines**: tablet, medicine, syrup, injection, capsule
- **Fuel**: petrol, diesel, gas, fuel
- **Construction Materials**: cement, steel, brick, sand
- **General**: Default category for other products

### **Unit Detection**

Units are detected based on product names:
- **kg**: kilogram, kilo
- **liter**: litre, ltr
- **piece**: pcs, unit
- **gram**: gm, g
- **ton**: tonne

## 📊 Processing Results

### **Success Metrics**
- Total products found in PDF
- Successfully imported products
- Success rate percentage
- Processing errors and warnings

### **Error Handling**
- Invalid price formats
- Duplicate product detection
- File format validation
- Processing exceptions

## 🎯 Example Usage

### **Sample PDF Processing Results:**

```
✅ PDF processed successfully!
📊 Total products found: 9
❌ Errors: 0

📦 Sample Products:
1. IMP. UREA - NFML (FFL) 50 kg - Rs. 3839 (kg) - Agricultural Products
2. SARSABZ NP 50 kg - Rs. 8011 (kg) - General
3. FFL SARSABZ UREA 50 kg - Rs. 4400 (kg) - Agricultural Products
4. BABARSHER DAP 50 kg - Rs. 11477 (kg) - Agricultural Products
5. COMPLETE NPK (10-26-26) 50 kg - Rs. 19900 (kg) - Agricultural Products

📈 Category Breakdown:
- Agricultural Products: 6 products
- General: 3 products
```

## 🔒 Security & Permissions

- Only admin users can upload and process PDFs
- File size limit: 10MB
- Only PDF files are accepted
- All uploads are tracked with user attribution

## 🚀 Performance

- Efficient text extraction using `pdfplumber`
- Smart pattern matching with multiple regex patterns
- Duplicate detection to avoid redundant imports
- Batch processing for large PDFs
- Cached processing results

## 📝 Dependencies

- `pdfplumber==0.10.3` - PDF text extraction
- `PyPDF2==3.0.1` - PDF processing utilities
- `Django` - Web framework
- `djangorestframework` - API framework

## 🎉 Benefits

1. **Time Saving**: Bulk import instead of manual entry
2. **Accuracy**: Automated parsing reduces human errors
3. **Consistency**: Standardized product categorization
4. **Tracking**: Complete audit trail of imports
5. **Flexibility**: Preview before importing
6. **Integration**: Seamless integration with violation detection

This feature significantly streamlines the process of adding government-regulated products to the system, making it much easier to maintain an up-to-date database for price violation monitoring.
