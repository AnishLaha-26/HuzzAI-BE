from django.urls import path
from . import views

urlpatterns = [
    path('analyze-image/', views.ContextReplyImageView.as_view(), name='context_reply_analyze_image'),
]
