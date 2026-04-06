from django.contrib import admin
from .models import SMSLog, UserFeedback


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'confidence', 'is_phishing', 'phishing_score', 'language', 'timestamp']
    list_filter = ['category', 'is_phishing', 'language', 'timestamp']
    search_fields = ['message_hash']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'sms_log', 'original_category', 'corrected_category', 'timestamp']
    list_filter = ['original_category', 'corrected_category', 'timestamp']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
