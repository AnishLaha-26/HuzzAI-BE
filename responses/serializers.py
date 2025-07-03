# responses/serializers.py
from rest_framework import serializers
from .models import Response

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['id', 'original_text', 'mood', 'spice_level', 'generated_response', 'created_at']
        read_only_fields = ['id', 'created_at']