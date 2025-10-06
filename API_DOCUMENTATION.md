# API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication

All API endpoints require authentication using JWT tokens. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "device_id": "unique_device_id"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "session_id": "uuid-string"
}
```

### Logout
```http
POST /api/auth/logout/
Content-Type: application/json

{
  "device_id": "unique_device_id"
}
```

### Refresh Token
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "device_id": "unique_device_id"
}
```

### Get Current User
```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

## Products API

### List Products
```http
GET /api/products/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `search` - Search by product name or description
- `category` - Filter by category
- `is_active` - Filter by active status (true/false)
- `page` - Page number for pagination
- `page_size` - Number of items per page

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Essential Medicine - Paracetamol 500mg",
      "category": "Pharmaceuticals",
      "gov_price": "2.50",
      "description": "Government regulated price for essential medicine",
      "unit": "tablet",
      "is_active": true,
      "price_violation_threshold": "2.75",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Product (Admin Only)
```http
POST /api/products/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "New Product",
  "category": "Category",
  "gov_price": "10.00",
  "description": "Product description",
  "unit": "piece"
}
```

### Update Product (Admin Only)
```http
PUT /api/products/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Product Name",
  "gov_price": "12.00"
}
```

### Delete Product (Admin Only)
```http
DELETE /api/products/{id}/
Authorization: Bearer <access_token>
```

### Get Product Categories
```http
GET /api/products/categories/
Authorization: Bearer <access_token>
```

## Violations API

### List Violations
```http
GET /api/violations/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` - Filter by status (pending/confirmed/dismissed)
- `severity` - Filter by severity (low/medium/high/critical)
- `product_id` - Filter by regulated product ID
- `violation_type` - Filter by violation type
- `date_from` - Filter from date (YYYY-MM-DD)
- `date_to` - Filter to date (YYYY-MM-DD)

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "regulated_product": {
        "id": 1,
        "name": "Essential Medicine - Paracetamol 500mg",
        "category": "Pharmaceuticals",
        "gov_price": "2.50"
      },
      "scraped_product": {
        "id": 1,
        "product_name": "Paracetamol 500mg - Amazon",
        "marketplace": "amazon",
        "listed_price": "3.50",
        "url": "https://amazon.com/product/123"
      },
      "violation_type": "price_exceeded",
      "severity": "medium",
      "proposed_penalty": "500.00",
      "status": "pending",
      "notes": "",
      "confirmed_by": null,
      "confirmed_at": null,
      "price_difference": "1.00",
      "percentage_over": 40.0,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Confirm Violation (Investigator Only)
```http
POST /api/violations/{id}/confirm/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Violation confirmed and case created",
  "violation_id": 1,
  "case_id": 1,
  "case_created": true
}
```

### Dismiss Violation (Investigator Only)
```http
POST /api/violations/{id}/dismiss/
Authorization: Bearer <access_token>
```

### Get Violation Statistics
```http
GET /api/violations/stats/
Authorization: Bearer <access_token>
```

## Cases API

### List Cases
```http
GET /api/cases/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` - Filter by status (open/in_progress/closed/resolved)
- `investigator_id` - Filter by investigator ID
- `product_id` - Filter by product ID
- `date_from` - Filter from date
- `date_to` - Filter to date

### Create Case
```http
POST /api/cases/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "violation": 1,
  "notes": "Initial case notes"
}
```

### Update Case
```http
PUT /api/cases/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "in_progress",
  "notes": "Updated case notes",
  "resolution_notes": "Case resolution details",
  "final_penalty": "400.00"
}
```

### Close Case
```http
POST /api/cases/{id}/close/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "resolution_notes": "Case closed with resolution",
  "final_penalty": "400.00"
}
```

### Add Case Note
```http
POST /api/cases/{id}/notes/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "New case note content"
}
```

## Scraping API

### List Scraped Products
```http
GET /api/scraping/results/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `marketplace` - Filter by marketplace
- `availability` - Filter by availability (true/false)
- `search` - Search by product name
- `date_from` - Filter from date
- `date_to` - Filter to date

### List Scraping Jobs
```http
GET /api/scraping/jobs/
Authorization: Bearer <access_token>
```

### Trigger Scraping Job (Admin Only)
```http
POST /api/scraping/trigger/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "marketplace": "amazon"
}
```

### Get Scraping Statistics
```http
GET /api/scraping/stats/
Authorization: Bearer <access_token>
```

## Reports API

### Get Summary Report
```http
GET /api/reports/summary/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `date_from` - Filter from date
- `date_to` - Filter to date

**Response:**
```json
{
  "total_products": 25,
  "total_violations": 150,
  "total_cases": 45,
  "total_penalties": 25000.00,
  "violations_by_severity": {
    "low": 50,
    "medium": 75,
    "high": 25
  },
  "violations_by_status": {
    "pending": 30,
    "confirmed": 80,
    "dismissed": 40
  },
  "cases_by_status": {
    "open": 15,
    "in_progress": 20,
    "closed": 10
  },
  "recent_activity": {
    "violations": 12,
    "cases": 5,
    "scraped_products": 200
  }
}
```

### Export Data
```http
GET /api/reports/export/?type=violations
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `type` - Export type (violations/cases/products)

Returns a CSV file download.

### Get Dashboard Metrics
```http
GET /api/reports/dashboard-metrics/
Authorization: Bearer <access_token>
```

## Sessions API

### List Active Sessions
```http
GET /api/sessions/
Authorization: Bearer <access_token>
```

### Revoke Session
```http
DELETE /api/sessions/{session_id}/revoke/
Authorization: Bearer <access_token>
```

## Error Responses

All API endpoints return appropriate HTTP status codes and error messages:

```json
{
  "error": "Error message description",
  "detail": "Detailed error information"
}
```

### Common Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate-limited to prevent abuse. Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with the following parameters:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

Pagination metadata is included in list responses:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```
