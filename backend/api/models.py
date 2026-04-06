from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class SMSLog(models.Model):
    """Store SMS analysis logs without sensitive content"""
    CATEGORY_CHOICES = [
        ('spam', 'Spam'),
        ('promotion', 'Promotion'),
        ('otp', 'OTP'),
        ('important', 'Important'),
        ('personal', 'Personal'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('safe', 'Safe'),
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    confidence = models.FloatField()
    is_phishing = models.BooleanField(default=False)
    phishing_score = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='safe')
    message_hash = models.CharField(max_length=64, db_index=True)  # Removed unique constraint
    timestamp = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=20, default='en')
    
    # Advanced features
    sentiment_score = models.FloatField(default=0.0)
    urgency_score = models.FloatField(default=0.0)
    sender_reputation = models.FloatField(default=0.5)
    message_length = models.IntegerField(default=0)
    has_urls = models.BooleanField(default=False)
    has_phone_numbers = models.BooleanField(default=False)
    has_financial_terms = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['category']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['is_phishing']),
        ]


class UserFeedback(models.Model):
    """Store user feedback for model improvement"""
    sms_log = models.ForeignKey(SMSLog, on_delete=models.CASCADE, related_name='feedbacks')
    original_category = models.CharField(max_length=20)
    corrected_category = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    feedback_quality = models.IntegerField(default=0)  # User rating
    
    class Meta:
        ordering = ['-timestamp']


class ThreatPattern(models.Model):
    """Store identified threat patterns for learning"""
    pattern_type = models.CharField(max_length=50)
    pattern_text = models.TextField()
    severity = models.CharField(max_length=20)
    frequency = models.IntegerField(default=1)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_seen']


class ModelPerformance(models.Model):
    """Track model performance metrics over time"""
    model_name = models.CharField(max_length=50)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)
    training_samples = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']


class SenderProfile(models.Model):
    """Profile senders based on historical behavior"""
    sender_hash = models.CharField(max_length=64, unique=True)
    total_messages = models.IntegerField(default=0)
    spam_count = models.IntegerField(default=0)
    legitimate_count = models.IntegerField(default=0)
    reputation_score = models.FloatField(default=0.5)
    is_blacklisted = models.BooleanField(default=False)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-last_seen']


class AnalyticsSnapshot(models.Model):
    """Store daily analytics snapshots for trend analysis"""
    date = models.DateField(unique=True)
    total_messages = models.IntegerField(default=0)
    spam_count = models.IntegerField(default=0)
    phishing_count = models.IntegerField(default=0)
    avg_confidence = models.FloatField(default=0.0)
    unique_senders = models.IntegerField(default=0)
    high_risk_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
