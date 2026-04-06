from rest_framework import serializers
from .models import SMSLog, UserFeedback


class SMSPredictionSerializer(serializers.Serializer):
    """Serializer for SMS prediction request"""
    message = serializers.CharField(required=True, max_length=1000)
    language = serializers.ChoiceField(
        choices=['en', 'hi', 'mr'],
        default='en',
        required=False
    )


class SMSResultSerializer(serializers.Serializer):
    """Serializer for SMS prediction result"""
    category = serializers.CharField()
    confidence = serializers.FloatField()
    is_phishing = serializers.BooleanField()
    phishing_score = serializers.FloatField()
    suspicious_keywords = serializers.ListField(child=serializers.CharField())
    suspicious_urls = serializers.ListField(child=serializers.CharField())
    highlighted_words = serializers.ListField(child=serializers.DictField())
    model_comparison = serializers.DictField()
    message_id = serializers.CharField()


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for user feedback"""
    message_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserFeedback
        fields = ['message_id', 'original_category', 'corrected_category', 'timestamp']
        read_only_fields = ['timestamp']


class SMSLogSerializer(serializers.ModelSerializer):
    """Serializer for SMS logs"""
    class Meta:
        model = SMSLog
        fields = ['id', 'category', 'confidence', 'is_phishing', 
                  'phishing_score', 'timestamp', 'language']
