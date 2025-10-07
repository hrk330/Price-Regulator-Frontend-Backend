from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

def api_documentation(request):
    """API Documentation endpoint"""
    docs = {
        "title": "Price Regulation Monitoring System API",
        "version": "1.0.0",
        "description": "API endpoints for the Price Regulation Monitoring System",
        "base_url": "http://127.0.0.1:8000/api/",
        "endpoints": {
            "authentication": {
                "login": "POST /api/auth/login/",
                "register": "POST /api/auth/register/",
                "me": "GET /api/auth/me/",
                "refresh": "POST /api/auth/refresh/",
                "logout": "POST /api/auth/logout/",
                "sessions": "GET /api/auth/sessions/",
                "revoke_session": "DELETE /api/auth/sessions/{session_id}/revoke/"
            },
            "products": {
                "regulated_products": "GET/POST /api/products/regulated-products/",
                "product_detail": "GET/PUT/DELETE /api/products/regulated-products/{id}/",
                "rate_list_uploads": "GET/POST /api/products/rate-list-uploads/",
                "upload_rate_list": "POST /api/products/upload-rate-list/",
                "preview_pdf": "POST /api/products/preview-pdf-processing/",
                "products_stats": "GET /api/products/stats/"
            },
            "violations": {
                "list": "GET/POST /api/violations/",
                "detail": "GET/PUT/DELETE /api/violations/{id}/"
            },
            "cases": {
                "list": "GET/POST /api/cases/",
                "detail": "GET/PUT/DELETE /api/cases/{id}/"
            },
            "reports": {
                "list": "GET/POST /api/reports/",
                "detail": "GET/PUT/DELETE /api/reports/{id}/",
                "generate": "POST /api/reports/generate/"
            }
        },
        "authentication": {
            "type": "JWT",
            "header": "Authorization: Bearer <token>",
            "note": "Use login endpoint to get access token"
        },
        "admin": "http://127.0.0.1:8000/admin/"
    }
    return JsonResponse(docs, json_dumps_params={'indent': 2})

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/auth/sessions/', include('apps.accounts.session_urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/violations/', include('apps.violations.urls')),
    path('api/cases/', include('apps.cases.urls')),
    path('api/reports/', include('apps.reports.urls')),
    
    # Legacy API docs (JSON format)
    path('api/docs/json/', api_documentation, name='api_docs'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='root_swagger'),  # Root URL shows Swagger UI
]