# analyzer/serializers.py
from rest_framework import serializers

class MoodBasedResponseSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    mood = serializers.ChoiceField(
        choices=[
            ('flirty', 'Flirty'),
            ('funny', 'Funny'),
            ('sweet', 'Sweet'),
            ('mysterious', 'Mysterious'),
            ('sarcastic', 'Sarcastic'),
            ('romantic', 'Romantic')
        ],
        required=True
    )
    spiceLevel = serializers.IntegerField(min_value=1, max_value=10, required=True)