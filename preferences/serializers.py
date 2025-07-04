from rest_framework import serializers
from .models import Preferences

class PreferenceSerializer(serializers.ModelSerializer):
    # Add these fields to handle frontend field names
    sex = serializers.ChoiceField(
        choices=Preferences.SEX_CHOICES, 
        required=True,
        write_only=True
    )
    age_group = serializers.ChoiceField(
        choices=Preferences.AGE_GROUP_CHOICES,
        required=True,
        write_only=True
    )
    dating_goal = serializers.ChoiceField(
        choices=Preferences.DATING_GOAL_CHOICES,
        required=True,
        write_only=True
    )
    chat_platform = serializers.ChoiceField(
        choices=Preferences.CHAT_PLATFORM_CHOICES,
        required=False,
        write_only=True,
        allow_blank=True
    )
    rizz_styles = serializers.JSONField(
        required=False,
        write_only=True
    )

    class Meta:
        model = Preferences
        fields = [
            'id',
            'sex',
            'age_group',
            'dating_goal',
            'chat_platform',
            'rizz_styles',
            'recent_dates',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        # Get the user from the context (passed from the view)
        user = self.context['request'].user
        # Create and return a new Preferences instance with the user
        return Preferences.objects.create(user=user, **validated_data)
        
    def update(self, instance, validated_data):
        # Update the existing instance with the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

