import re
from rest_framework import serializers
from .models import SMSLog, UserFeedback

# Allowed category values — strict whitelist
VALID_CATEGORIES = {'spam', 'promotion', 'otp', 'important', 'personal'}
# UUID pattern for message IDs
_UUID_RE = re.compile(r'^\d+$')


class SMSPredictionSerializer(serializers.Serializer):
    """Strict input validation for SMS prediction requests."""

    message = serializers.CharField(
        required=True,
        min_length=1,
        max_length=1000,
        trim_whitespace=True,
    )
    language = serializers.ChoiceField(
        choices=['en', 'hi', 'mr'],
        default='en',
        required=False,
    )

    def validate_message(self, value):
        # Reject empty after stripping
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value

    def validate_language(self, value):
        if value not in ('en', 'hi', 'mr'):
            return 'en'
        return value


class SMSResultSerializer(serializers.Serializer):
    """Output serializer — controls exactly what fields are returned."""
    category            = serializers.CharField()
    confidence          = serializers.FloatField()
    is_phishing         = serializers.BooleanField()
    phishing_score      = serializers.FloatField()
    suspicious_keywords = serializers.ListField(child=serializers.CharField())
    suspicious_urls     = serializers.ListField(child=serializers.CharField())
    highlighted_words   = serializers.ListField(child=serializers.DictField())
    model_comparison    = serializers.DictField()
    message_id          = serializers.CharField()


class FeedbackSerializer(serializers.Serializer):
    """Strict feedback serializer with whitelist validation."""

    message_id         = serializers.CharField(max_length=20)
    original_category  = serializers.ChoiceField(choices=list(VALID_CATEGORIES))
    corrected_category = serializers.ChoiceField(choices=list(VALID_CATEGORIES))

    def validate_message_id(self, value):
        # Only allow numeric IDs
        if not _UUID_RE.match(str(value)):
            raise serializers.ValidationError("Invalid message ID format")
        return value

    def validate(self, data):
        # original and corrected must differ
        if data['original_category'] == data['corrected_category']:
            raise serializers.ValidationError(
                "Corrected category must differ from original"
            )
        return data


class SMSLogSerializer(serializers.ModelSerializer):
    """Read-only serializer — never expose message content."""
    class Meta:
        model = SMSLog
        fields = ['id', 'category', 'confidence', 'is_phishing',
                  'phishing_score', 'risk_level', 'timestamp', 'language']
        read_only_fields = fields
