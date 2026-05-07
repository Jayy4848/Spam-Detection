from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import JsonResponse

# Use a non-obvious admin URL from settings
admin_url = getattr(settings, 'ADMIN_URL', 'secure-admin-panel/')

def api_root(request):
    """Root endpoint showing API information"""
    return JsonResponse({
        'message': 'TextGuard AI - SMS Security API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health/',
            'model_info': '/api/model-info/',
            'stats': '/api/stats/',
            'predict': '/api/predict/ (POST)',
            'feedback': '/api/feedback/ (POST)',
            'reset': '/api/reset/ (POST)',
            'recent_messages': '/api/recent-messages/',
            'delete_message': '/api/messages/<id>/ (DELETE)'
        },
        'documentation': 'Visit http://localhost:3000 for the web interface',
        'accuracy': '96.55%'
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path(admin_url, admin.site.urls),
    path('api/', include('api.urls')),
]
