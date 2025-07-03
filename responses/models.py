# responses/models.py
from django.db import models
from django.conf import settings

class Response(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    original_text = models.TextField()
    mood = models.CharField(max_length=20)
    spice_level = models.IntegerField()
    generated_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Response in {self.mood} mood (Spice: {self.spice_level}/10) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

# responses/serializers.py
from rest_framework import serializers
from .models import Response

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['id', 'original_text', 'mood', 'generated_response', 'created_at']
        read_only_fields = ['id', 'created_at']

# responses/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response as DRF_Response
from rest_framework.permissions import IsAuthenticated
from .models import Response
from .serializers import ResponseSerializer

class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return DRF_Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

# responses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'responses', views.ResponseViewSet, basename='response')

urlpatterns = [
    path('', include(router.urls)),
]

# responses/apps.py
from django.apps import AppConfig

class ResponsesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'responses'