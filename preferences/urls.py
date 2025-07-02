from django.urls import path
from .views import PreferenceView

urlpatterns = [
    path('', PreferenceView.as_view(), name='preference'),
    # The above URL will handle:
    # GET /api/preferences/ - Get current user's preferences
    # POST /api/preferences/ - Create new preferences
    # PUT /api/preferences/ - Update existing preferences
]
