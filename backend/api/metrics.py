"""
System Metrics and Monitoring
Tracks API performance, model performance, and system health
"""

import time
import psutil
from typing import Dict, Any, List
from django.core.cache import cache
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import logging

from .models import SMSLog, UserFeedback

logger = logging.getLogger('api')


class MetricsCollector:
    """Collect and aggregate system metrics"""
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / (1024 * 1024),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024 * 1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}
    
    @staticmethod
    def get_api_metrics(time_window_hours: int = 24) -> Dict[str, Any]:
        """Get API usage metrics"""
        try:
            cutoff_time = timezone.now() - timedelta(hours=time_window_hours)
            
            # Total requests
            total_requests = SMSLog.objects.filter(timestamp__gte=cutoff_time).count()
            
            # Requests by category
            category_distribution = SMSLog.objects.filter(
                timestamp__gte=cutoff_time
            ).values('category').annotate(count=Count('id'))
            
            # Average confidence
            avg_confidence = SMSLog.objects.filter(
                timestamp__gte=cutoff_time
            ).aggregate(Avg('confidence'))['confidence__avg'] or 0
            
            # Phishing detection rate
            phishing_count = SMSLog.objects.filter(
                timestamp__gte=cutoff_time,
                is_phishing=True
            ).count()
            
            phishing_rate = (phishing_count / total_requests * 100) if total_requests > 0 else 0
            
            # High risk messages
            high_risk_count = SMSLog.objects.filter(
                timestamp__gte=cutoff_time,
                risk_level='high'
            ).count()
            
            return {
                'time_window_hours': time_window_hours,
                'total_requests': total_requests,
                'requests_per_hour': total_requests / time_window_hours if time_window_hours > 0 else 0,
                'category_distribution': list(category_distribution),
                'average_confidence': round(avg_confidence, 4),
                'phishing_detection_rate': round(phishing_rate, 2),
                'high_risk_count': high_risk_count
            }
        except Exception as e:
            logger.error(f"Error collecting API metrics: {str(e)}")
            return {}
    
    @staticmethod
    def get_model_performance_metrics() -> Dict[str, Any]:
        """Get model performance metrics based on user feedback"""
        try:
            total_feedback = UserFeedback.objects.count()
            
            if total_feedback == 0:
                return {
                    'total_feedback': 0,
                    'accuracy': 0,
                    'message': 'No feedback data available'
                }
            
            # Calculate accuracy from feedback
            correct_predictions = UserFeedback.objects.filter(
                original_category=models.F('corrected_category')
            ).count()
            
            accuracy = (correct_predictions / total_feedback * 100) if total_feedback > 0 else 0
            
            # Per-category accuracy
            category_accuracy = {}
            for category in ['spam', 'promotion', 'otp', 'important', 'personal']:
                category_feedback = UserFeedback.objects.filter(
                    original_category=category
                )
                category_total = category_feedback.count()
                
                if category_total > 0:
                    category_correct = category_feedback.filter(
                        corrected_category=category
                    ).count()
                    category_accuracy[category] = round(
                        (category_correct / category_total * 100), 2
                    )
            
            return {
                'total_feedback': total_feedback,
                'overall_accuracy': round(accuracy, 2),
                'category_accuracy': category_accuracy,
                'correct_predictions': correct_predictions,
                'incorrect_predictions': total_feedback - correct_predictions
            }
        except Exception as e:
            logger.error(f"Error collecting model performance metrics: {str(e)}")
            return {}
    
    @staticmethod
    def get_performance_stats() -> Dict[str, Any]:
        """Get API performance statistics"""
        try:
            # Get cached performance metrics
            perf_metrics = cache.get('perf_metrics_/api/predict/', [])
            
            if not perf_metrics:
                return {
                    'message': 'No performance data available',
                    'sample_count': 0
                }
            
            avg_time = sum(perf_metrics) / len(perf_metrics)
            min_time = min(perf_metrics)
            max_time = max(perf_metrics)
            
            # Calculate percentiles
            sorted_metrics = sorted(perf_metrics)
            p50 = sorted_metrics[len(sorted_metrics) // 2]
            p95 = sorted_metrics[int(len(sorted_metrics) * 0.95)]
            p99 = sorted_metrics[int(len(sorted_metrics) * 0.99)]
            
            return {
                'sample_count': len(perf_metrics),
                'avg_response_time_ms': round(avg_time * 1000, 2),
                'min_response_time_ms': round(min_time * 1000, 2),
                'max_response_time_ms': round(max_time * 1000, 2),
                'p50_response_time_ms': round(p50 * 1000, 2),
                'p95_response_time_ms': round(p95 * 1000, 2),
                'p99_response_time_ms': round(p99 * 1000, 2)
            }
        except Exception as e:
            logger.error(f"Error collecting performance stats: {str(e)}")
            return {}
    
    @staticmethod
    def get_comprehensive_metrics() -> Dict[str, Any]:
        """Get all metrics in one call"""
        return {
            'timestamp': timezone.now().isoformat(),
            'system': MetricsCollector.get_system_metrics(),
            'api': MetricsCollector.get_api_metrics(),
            'model_performance': MetricsCollector.get_model_performance_metrics(),
            'performance_stats': MetricsCollector.get_performance_stats()
        }


# Import models here to avoid circular import
from django.db import models
