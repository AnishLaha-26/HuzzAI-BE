from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Accounts App (Authentication)
    path('api/accounts/', include('accounts.urls')),

    # Preferences App (Protected)
    path('api/preferences/', include('preferences.urls')),
]
