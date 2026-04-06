from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, F
from django.utils import timezone
from datetime import timedelta

from .models import SMSLog, UserFeedback, ThreatPattern, ModelPerformance


class ThreatIntelligenceView(APIView):
    """API endpoint for threat intelligence"""
    
    def get(self, request):
        # Get recent threat patterns
        recent_patterns = ThreatPattern.objects.filter(
            is_active=True,
            last_seen__gte=timezone.now() - timedelta(days=7)
        ).order_by('-frequency')[:20]
        
        patterns_data = [{
            'pattern': p.pattern_text,
            'type': p.pattern_type,
            'severity': p.severity,
            'frequency': p.frequency,
            'first_seen': p.first_seen.isoformat(),
            'last_seen': p.last_seen.isoformat()
        } for p in recent_patterns]
        
        # Get high-risk messages from last 24 hours
        high_risk_messages = SMSLog.objects.filter(
            risk_level__in=['high', 'critical'],
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Calculate threat trends
        today = timezone.now().date()
        threat_trend = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = SMSLog.objects.filter(
                timestamp__date=date,
                is_phishing=True
            ).count()
            threat_trend.append({
                'date': date.isoformat(),
                'count': count
            })
        
        return Response({
            'threat_patterns': patterns_data,
            'high_risk_count_24h': high_risk_messages,
            'threat_trend_7days': threat_trend[::-1],
            'total_active_patterns': len(patterns_data)
        }, status=status.HTTP_200_OK)


class ModelPerformanceView(APIView):
    """API endpoint for model performance metrics"""
    
    def get(self, request):
        # Get latest performance metrics
        latest_metrics = ModelPerformance.objects.order_by('-timestamp').first()
        
        # Calculate real-time accuracy from feedback
        total_feedback = UserFeedback.objects.count()
        correct_predictions = UserFeedback.objects.filter(
            original_category=F('corrected_category')
        ).count() if total_feedback > 0 else 0
        
        feedback_accuracy = (correct_predictions / total_feedback * 100) if total_feedback > 0 else 0
        
        # Get category-wise performance
        category_performance = {}
        for category in ['spam', 'promotion', 'otp', 'important', 'personal']:
            logs = SMSLog.objects.filter(category=category)
            if logs.exists():
                avg_conf = logs.aggregate(Avg('confidence'))['confidence__avg']
                category_performance[category] = {
                    'count': logs.count(),
                    'avg_confidence': round(avg_conf, 4) if avg_conf else 0
                }
        
        # Performance over time
        performance_history = ModelPerformance.objects.order_by('-timestamp')[:10]
        history_data = [{
            'timestamp': p.timestamp.isoformat(),
            'accuracy': p.accuracy,
            'model_name': p.model_name
        } for p in performance_history]
        
        return Response({
            'current_accuracy': latest_metrics.accuracy if latest_metrics else 0.93,
            'feedback_accuracy': round(feedback_accuracy, 2),
            'total_predictions': SMSLog.objects.count(),
            'total_feedback': total_feedback,
            'category_performance': category_performance,
            'performance_history': history_data[::-1]
        }, status=status.HTTP_200_OK)


class AdvancedStatsView(APIView):
    """API endpoint for advanced statistics"""
    
    def get(self, request):
        # Time-based analysis
        now = timezone.now()
        today = now.date()
        
        # Get messages by risk level
        risk_distribution = SMSLog.objects.values('risk_level').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Sentiment distribution
        positive_sentiment = SMSLog.objects.filter(sentiment_score__gt=0.3).count()
        negative_sentiment = SMSLog.objects.filter(sentiment_score__lt=-0.3).count()
        neutral_sentiment = SMSLog.objects.filter(
            sentiment_score__gte=-0.3,
            sentiment_score__lte=0.3
        ).count()
        
        # Urgency distribution
        critical_urgency = SMSLog.objects.filter(urgency_score__gt=0.8).count()
        high_urgency = SMSLog.objects.filter(
            urgency_score__gt=0.6,
            urgency_score__lte=0.8
        ).count()
        medium_urgency = SMSLog.objects.filter(
            urgency_score__gt=0.4,
            urgency_score__lte=0.6
        ).count()
        low_urgency = SMSLog.objects.filter(urgency_score__lte=0.4).count()
        
        # Messages with URLs and phone numbers
        messages_with_urls = SMSLog.objects.filter(has_urls=True).count()
        messages_with_phones = SMSLog.objects.filter(has_phone_numbers=True).count()
        messages_with_financial = SMSLog.objects.filter(has_financial_terms=True).count()
        
        # Average scores
        avg_sentiment = SMSLog.objects.aggregate(Avg('sentiment_score'))['sentiment_score__avg'] or 0
        avg_urgency = SMSLog.objects.aggregate(Avg('urgency_score'))['urgency_score__avg'] or 0
        avg_confidence = SMSLog.objects.aggregate(Avg('confidence'))['confidence__avg'] or 0
        
        # Hourly distribution (last 24 hours)
        hourly_stats = []
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            count = SMSLog.objects.filter(
                timestamp__gte=hour_start,
                timestamp__lt=hour_end
            ).count()
            hourly_stats.append({
                'hour': hour_start.strftime('%H:00'),
                'count': count
            })
        
        return Response({
            'risk_distribution': list(risk_distribution),
            'sentiment_distribution': {
                'positive': positive_sentiment,
                'negative': negative_sentiment,
                'neutral': neutral_sentiment
            },
            'urgency_distribution': {
                'critical': critical_urgency,
                'high': high_urgency,
                'medium': medium_urgency,
                'low': low_urgency
            },
            'feature_detection': {
                'urls': messages_with_urls,
                'phone_numbers': messages_with_phones,
                'financial_terms': messages_with_financial
            },
            'average_scores': {
                'sentiment': round(avg_sentiment, 4),
                'urgency': round(avg_urgency, 4),
                'confidence': round(avg_confidence, 4)
            },
            'hourly_distribution': hourly_stats[::-1]
        }, status=status.HTTP_200_OK)


class ExportDataView(APIView):
    """API endpoint for data export"""
    
    def get(self, request):
        export_type = request.query_params.get('type', 'summary')
        
        if export_type == 'summary':
            # Export summary statistics
            total_messages = SMSLog.objects.count()
            spam_count = SMSLog.objects.filter(category='spam').count()
            phishing_count = SMSLog.objects.filter(is_phishing=True).count()
            
            return Response({
                'export_type': 'summary',
                'generated_at': timezone.now().isoformat(),
                'statistics': {
                    'total_messages': total_messages,
                    'spam_count': spam_count,
                    'phishing_count': phishing_count,
                    'spam_percentage': round(spam_count / total_messages * 100, 2) if total_messages > 0 else 0
                }
            }, status=status.HTTP_200_OK)
        
        elif export_type == 'threats':
            # Export threat intelligence
            threats = ThreatPattern.objects.filter(is_active=True).order_by('-frequency')[:50]
            threat_data = [{
                'pattern': t.pattern_text,
                'severity': t.severity,
                'frequency': t.frequency,
                'last_seen': t.last_seen.isoformat()
            } for t in threats]
            
            return Response({
                'export_type': 'threats',
                'generated_at': timezone.now().isoformat(),
                'threats': threat_data
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid export type'}, status=status.HTTP_400_BAD_REQUEST)
