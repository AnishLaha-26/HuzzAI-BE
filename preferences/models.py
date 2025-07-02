from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

class Preferences(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    AGE_GROUP_CHOICES = [
        ('<18', 'Under 18'),
        ('18-24', '18-24'),
        ('25-34', '25-34'),
        ('35-44', '35-44'),
        ('45+', '45+'),
    ]

    DATING_GOAL_CHOICES = [
        ('LTR', 'Long-term relationship'),
        ('STD', 'Short-term dating'),
        ('FRD', 'Friendship'),
        ('CAS', 'Casual'),
    ]
    
    CHAT_PLATFORM_CHOICES = [
        ('TD', 'Tinder'),
        ('IG', 'Instagram'),
        ('TI', 'TikTok'),
        ('WH', 'WhatsApp'),
        ('TE', 'Telegram'),
        ('OT', 'Other'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    age_group = models.CharField(max_length=5, choices=AGE_GROUP_CHOICES)
    dating_goal = models.CharField(max_length=3, choices=DATING_GOAL_CHOICES)
    recent_dates = models.JSONField(
        help_text="List of recent date activities or preferences",
        null=True,
        blank=True,
        default=list
    )
    rizz_styles = models.JSONField(default=dict, help_text='Preferred communication styles and preferences')
    chat_platform = models.CharField(max_length=3, choices=CHAT_PLATFORM_CHOICES, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"