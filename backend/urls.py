# backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/preferences/', include('preferences.urls')),
    path('api/rizz-analyzer/', include('rizz_analyzer.urls')),  # Rizz Analyzer URLs
    path('api/context-reply/', include('context_reply.urls')),  # Context Reply URLs
]