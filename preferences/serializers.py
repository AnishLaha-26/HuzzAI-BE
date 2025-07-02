from rest_framework import serializers
from .models import Preferences

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = [
            'id',
            'sex',
            'age_group',
            'dating_goal',
            'recent_dates',
            'rizz_styles',
            'chat_platform',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        # Get the user from the context (passed from the view)
        user = self.context['request'].user
        # Create and return a new Preference instance with the user
        return Preference.objects.create(user=user, **validated_data)
        
    def update(self, instance, validated_data):
        # Update the existing instance with the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
