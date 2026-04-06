from django.contrib import admin
from django.urls import path, include
from django.conf import settings

# Use a non-obvious admin URL from settings
admin_url = getattr(settings, 'ADMIN_URL', 'secure-admin-panel/')

urlpatterns = [
    path(admin_url, admin.site.urls),
    path('api/', include('api.urls')),
]
