# backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/preferences/', include('preferences.urls')),
    path('api/analyzer/', include('analyzer.urls')),  # Analyzer URLs
    path('api/', include('responses.urls')),
]