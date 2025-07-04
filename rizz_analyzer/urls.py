from django.urls import path
from . import views

app_name = 'rizz_analyzer'  # Add this line for namespacing

urlpatterns = [
    path('analyze-image/', views.AnalyzeImageView.as_view(), name='analyze-image'),
    path('analyze-text/', views.analyze_rizz_text, name='analyze-text'),
]