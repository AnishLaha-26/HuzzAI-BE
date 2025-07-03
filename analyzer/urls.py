# analyzer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('generate-response/', views.MoodBasedResponseView.as_view(), name='generate-response'),
]