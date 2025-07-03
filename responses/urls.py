# responses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'responses', views.ResponseViewSet, basename='response')

urlpatterns = [
    path('', include(router.urls)),
]