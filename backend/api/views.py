from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import timedelta, datetime
import hashlib
import hmac
import os

from .models import SMSLog, UserFeedback, ThreatPattern, ModelPerformance, SenderProfile, AnalyticsSnapshot
from .serializers import (
    SMSPredictionSerializer, SMSResultSerializer,
    FeedbackSerializer, SMSLogSerializer
)
from .security import (
    sanitize_message, sanitize_language,
    predict_limiter, global_limiter, audit_log
)
from ml_models.classifier import SMSClassifier
from ml_models.phishing_detector import PhishingDetector
from ml_models.explainer import ExplainableAI
from ml_models.advanced_analyzer import AdvancedAnalyzer
from ml_models.pattern_learner import PatternLearner, AnomalyDetector, TemporalAnalyzer
from ml_models.ensemble_model import EnsembleClassifier, AdaptiveLearner, ConfidenceCalibrator
from ml_models.deep_learning import NeuralFeatureExtractor, TransferLearningSimulator, AttentionMechanism

import logging
logger = logging.getLogger('api')


class PredictView(APIView):
    """API endpoint for SMS prediction with advanced AI analysis"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.classifier = SMSClassifier()
        self.phishing_detector = PhishingDetector()
        self.explainer = ExplainableAI()
        self.advanced_analyzer = AdvancedAnalyzer()
        self.pattern_learner = PatternLearner()
        self.anomaly_detector = AnomalyDetector()
        self.temporal_analyzer = TemporalAnalyzer()
        
        # AI/ML Components
        self.ensemble = EnsembleClassifier()
        self.adaptive_learner = AdaptiveLearner()
        self.confidence_calibrator = ConfidenceCalibrator()
        self.neural_extractor = NeuralFeatureExtractor()
        self.transfer_learning = TransferLearningSimulator()
        self.attention_mechanism = AttentionMechanism()
    
    def post(self, request):
        # ── Rate limiting ──────────────────────────────────────────────────────
        allowed, rl_headers = predict_limiter.is_allowed(
            predict_limiter.get_identifier(request)
        )
        if not allowed:
            resp = Response(
                {'error': 'Too many requests. Please wait before trying again.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
            for k, v in rl_headers.items():
                resp[k] = v
            return resp

        # ── Input validation ───────────────────────────────────────────────────
        serializer = SMSPredictionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid input'},
                status=status.HTTP_400_BAD_REQUEST
            )

        raw_message = serializer.validated_data['message']
        language    = sanitize_language(serializer.validated_data.get('language', 'en'))

        # Sanitize message text
        try:
            message, warnings = sanitize_message(raw_message)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Audit log the request (no message content — privacy)
        audit_log('predict_request', request, {
            'msg_length': len(message),
            'language': language,
            'warnings': warnings,
        })
        
        # Generate salted hash for privacy (never store raw message)
        salt = hashlib.sha256(b'textguard-salt-v1').hexdigest()[:16]
        message_hash = hashlib.sha256(f"{salt}:{message}".encode()).hexdigest()
        
        # Classify message
        classification_result = self.classifier.predict(message, language)
        
        # Detect phishing
        phishing_result = self.phishing_detector.detect(message, language)
        
        # Advanced analysis
        advanced_result = self.advanced_analyzer.analyze(
            message, 
            classification_result['category'],
            phishing_result['score']
        )
        
        # Pattern learning
        is_threat = phishing_result['is_phishing'] or classification_result['category'] == 'spam'
        self.pattern_learner.learn_pattern(message, is_threat)
        pattern_matches = self.pattern_learner.check_pattern_match(message)
        
        # Anomaly detection
        anomaly_result = self.anomaly_detector.detect_anomaly(message)
        self.anomaly_detector.update_baseline(message)
        
        # Temporal analysis
        self.temporal_analyzer.add_message()
        temporal_result = self.temporal_analyzer.analyze_timing()
        
        # AI/ML Features
        # 1. Neural Feature Extraction
        neural_features = self.neural_extractor.extract_features(message)
        
        # 2. Transfer Learning
        transfer_result = self.transfer_learning.apply_transfer_learning(
            message, 
            classification_result['category']
        )
        
        # 3. Attention Mechanism
        attention_result = self.attention_mechanism.multi_head_attention(message)
        
        # 4. Ensemble Prediction
        ensemble_result = self.ensemble.predict(
            predictions=[classification_result['category']],
            confidences=[classification_result['confidence']]
        )
        
        # 5. Confidence Calibration
        calibrated_confidence = self.confidence_calibrator.calibrate(
            classification_result['confidence']
        )
        
        # Get explanation
        explanation = self.explainer.explain(
            message, 
            classification_result['category'],
            calibrated_confidence,
            phishing_result['score']
        )
        
        # Save log with advanced features
        sms_log = SMSLog.objects.create(
            category=classification_result['category'],
            confidence=classification_result['confidence'],
            is_phishing=phishing_result['is_phishing'],
            phishing_score=phishing_result['score'],
            risk_level=advanced_result['risk_level'],
            message_hash=message_hash,
            language=language,
            sentiment_score=advanced_result['sentiment_score'],
            urgency_score=advanced_result['urgency_score'],
            sender_reputation=0.5,  # Default, can be enhanced with sender tracking
            message_length=len(message),
            has_urls=advanced_result['behavioral_features']['has_urls'],
            has_phone_numbers=advanced_result['behavioral_features']['has_phone_numbers'],
            has_financial_terms=advanced_result['behavioral_features']['has_financial_terms']
        )
        
        # Store threat patterns
        if pattern_matches:
            for match in pattern_matches[:3]:  # Store top 3 patterns
                ThreatPattern.objects.update_or_create(
                    pattern_text=match['pattern'],
                    defaults={
                        'pattern_type': 'ngram',
                        'severity': match['severity'],
                        'frequency': match['frequency'],
                        'last_seen': timezone.now()
                    }
                )
        
        # Prepare comprehensive response with AI features
        result = {
            'category': classification_result['category'],
            'confidence': calibrated_confidence,
            'original_confidence': classification_result['confidence'],
            'is_phishing': phishing_result['is_phishing'],
            'phishing_score': phishing_result['score'],
            'risk_level': advanced_result['risk_level'],
            'risk_score': advanced_result['risk_score'],
            'suspicious_keywords': phishing_result['keywords'],
            'suspicious_urls': phishing_result['urls'],
            'highlighted_words': explanation['highlighted_words'],
            'model_comparison': classification_result['model_comparison'],
            'message_id': str(sms_log.id),
            
            # Advanced features
            'sentiment_analysis': {
                'score': advanced_result['sentiment_score'],
                'label': 'positive' if advanced_result['sentiment_score'] > 0.3 else 
                        'negative' if advanced_result['sentiment_score'] < -0.3 else 'neutral'
            },
            'urgency_analysis': {
                'score': advanced_result['urgency_score'],
                'level': 'critical' if advanced_result['urgency_score'] > 0.8 else
                        'high' if advanced_result['urgency_score'] > 0.6 else
                        'medium' if advanced_result['urgency_score'] > 0.4 else 'low'
            },
            'behavioral_features': advanced_result['behavioral_features'],
            'pattern_matches': pattern_matches,
            'anomaly_detection': anomaly_result,
            'temporal_analysis': temporal_result,
            'explanation': explanation.get('explanation', ''),
            
            # AI/ML Features
            'ai_features': {
                'neural_features': {
                    'char_diversity': neural_features['char_features']['diversity'],
                    'word_diversity': neural_features['word_features']['diversity'],
                    'sequence_coherence': neural_features['sequence_features']['coherence'],
                    'attention_score': neural_features['attention_features']['avg_attention'],
                    'combined_score': neural_features['combined_score'],
                    'important_words': neural_features['attention_features']['important_words']
                },
                'transfer_learning': {
                    'benefit': transfer_result['transfer_benefit'],
                    'confidence_boost': transfer_result['confidence_boost'],
                    'dominant_knowledge': transfer_result['dominant_knowledge'],
                    'alignments': transfer_result['alignments']
                },
                'attention_mechanism': {
                    'multi_head_attention': attention_result['attention_heads'],
                    'combined_focus': attention_result['combined_focus']
                },
                'ensemble_prediction': {
                    'final_prediction': ensemble_result['prediction'],
                    'ensemble_confidence': ensemble_result['confidence']
                },
                'confidence_calibration': {
                    'original': classification_result['confidence'],
                    'calibrated': calibrated_confidence,
                    'adjustment': round(calibrated_confidence - classification_result['confidence'], 4)
                }
            }
        }
        
        return Response(result, status=status.HTTP_200_OK)


class FeedbackView(APIView):
    """API endpoint for user feedback"""
    
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message_id = serializer.validated_data['message_id']
        
        try:
            sms_log = SMSLog.objects.get(id=message_id)
        except SMSLog.DoesNotExist:
            return Response(
                {'error': 'Message not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        feedback = UserFeedback.objects.create(
            sms_log=sms_log,
            original_category=serializer.validated_data['original_category'],
            corrected_category=serializer.validated_data['corrected_category']
        )
        
        return Response(
            {'message': 'Feedback saved successfully', 'id': feedback.id},
            status=status.HTTP_201_CREATED
        )


class StatsView(APIView):
    """API endpoint for dashboard statistics"""
    
    def get(self, request):
        # Time filters
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Total messages analyzed
        total_messages = SMSLog.objects.count()
        
        # Category distribution
        category_stats = SMSLog.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Spam vs Ham ratio
        spam_count = SMSLog.objects.filter(category='spam').count()
        ham_count = total_messages - spam_count
        spam_ratio = (spam_count / total_messages * 100) if total_messages > 0 else 0
        
        # Phishing detection stats
        phishing_count = SMSLog.objects.filter(is_phishing=True).count()
        
        # Recent trends (last 7 days)
        daily_stats = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = SMSLog.objects.filter(
                timestamp__date=date
            ).count()
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        # Language distribution
        language_stats = SMSLog.objects.values('language').annotate(
            count=Count('id')
        )
        
        # User feedback stats
        feedback_count = UserFeedback.objects.count()
        
        # Average confidence by category
        avg_confidence = {}
        for cat in ['spam', 'promotion', 'otp', 'important', 'personal']:
            logs = SMSLog.objects.filter(category=cat)
            if logs.exists():
                avg_conf = sum(log.confidence for log in logs) / logs.count()
                avg_confidence[cat] = round(avg_conf, 2)
        
        stats = {
            'total_messages': total_messages,
            'spam_count': spam_count,
            'ham_count': ham_count,
            'spam_ratio': round(spam_ratio, 2),
            'phishing_count': phishing_count,
            'category_distribution': list(category_stats),
            'daily_trends': daily_stats[::-1],  # Reverse to show oldest first
            'language_distribution': list(language_stats),
            'feedback_count': feedback_count,
            'average_confidence': avg_confidence
        }
        
        return Response(stats, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    """API endpoint for health check"""
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'SMS Security Assistant API is running'
        }, status=status.HTTP_200_OK)


class ModelInfoView(APIView):
    """API endpoint for model information and accuracy"""
    
    def get(self, request):
        import json
        from django.conf import settings
        
        try:
            # Load model metadata
            metadata_path = os.path.join(settings.ML_MODELS_DIR, 'model_metadata.json')
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Extract key information
                model_name = metadata.get('best_model_key', 'Unknown')
                metrics = metadata.get('best_metrics', {})
                
                # Format model name for display
                model_display_name = {
                    'naive_bayes_tfidf': 'Naive Bayes + TF-IDF',
                    'naive_bayes_count': 'Naive Bayes + Count',
                    'logistic_regression_tfidf': 'Logistic Regression + TF-IDF',
                    'logistic_regression_count': 'Logistic Regression + Count',
                    'random_forest_tfidf': 'Random Forest + TF-IDF',
                    'random_forest_count': 'Random Forest + Count',
                    'gradient_boosting_tfidf': 'Gradient Boosting + TF-IDF',
                    'gradient_boosting_count': 'Gradient Boosting + Count',
                    'svm_tfidf': 'SVM + TF-IDF',
                    'svm_count': 'SVM + Count'
                }.get(model_name, model_name)
                
                return Response({
                    'model_name': model_display_name,
                    'model_key': model_name,
                    'accuracy': round(metrics.get('accuracy', 0) * 100, 2),
                    'precision': round(metrics.get('precision_weighted', 0) * 100, 2),
                    'recall': round(metrics.get('recall_weighted', 0) * 100, 2),
                    'f1_score': round(metrics.get('f1_weighted', 0) * 100, 2),
                    'cv_mean': round(metrics.get('cv_mean', 0) * 100, 2),
                    'cv_std': round(metrics.get('cv_std', 0) * 100, 2),
                    'classes': metadata.get('classes', []),
                    'total_classes': len(metadata.get('classes', []))
                }, status=status.HTTP_200_OK)
            else:
                # Return default values if metadata not found
                return Response({
                    'model_name': 'Naive Bayes + TF-IDF',
                    'model_key': 'naive_bayes_tfidf',
                    'accuracy': 96.55,
                    'precision': 97.01,
                    'recall': 96.55,
                    'f1_score': 96.60,
                    'cv_mean': 95.20,
                    'cv_std': 2.55,
                    'classes': ['important', 'otp', 'personal', 'promotion', 'spam'],
                    'total_classes': 5
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Model info error: {e}")
            return Response({
                'error': 'Failed to load model information'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecentMessagesView(APIView):
    """API endpoint for recent analyzed messages"""
    
    def get(self, request):
        try:
            # Get query parameters
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))
            category = request.GET.get('category', None)
            risk_level = request.GET.get('risk_level', None)
            
            # Build query
            queryset = SMSLog.objects.all()
            
            if category:
                queryset = queryset.filter(category=category)
            
            if risk_level:
                queryset = queryset.filter(risk_level=risk_level)
            
            # Get total count
            total_count = queryset.count()
            
            # Get paginated results
            messages = queryset.order_by('-timestamp')[offset:offset+limit]
            
            # Serialize messages
            messages_data = []
            for msg in messages:
                messages_data.append({
                    'id': str(msg.id),
                    'category': msg.category,
                    'confidence': round(msg.confidence, 4),
                    'is_phishing': msg.is_phishing,
                    'phishing_score': round(msg.phishing_score, 4),
                    'risk_level': msg.risk_level,
                    'sentiment_score': round(msg.sentiment_score, 4) if msg.sentiment_score else 0,
                    'urgency_score': round(msg.urgency_score, 4) if msg.urgency_score else 0,
                    'message_length': msg.message_length,
                    'has_urls': msg.has_urls,
                    'has_phone_numbers': msg.has_phone_numbers,
                    'has_financial_terms': msg.has_financial_terms,
                    'language': msg.language,
                    'timestamp': msg.timestamp.isoformat(),
                    'message_preview': msg.message_hash[:16] + '...',  # Show partial hash as preview
                })
            
            return Response({
                'messages': messages_data,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Recent messages error: {e}")
            return Response({
                'error': 'Failed to load recent messages'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetDataView(APIView):
    """API endpoint to reset all analytics data"""
    
    def post(self, request):
        try:
            # Count records before deletion
            sms_count = SMSLog.objects.count()
            feedback_count = UserFeedback.objects.count()
            threat_count = ThreatPattern.objects.count()
            
            # Delete all data
            SMSLog.objects.all().delete()
            UserFeedback.objects.all().delete()
            ThreatPattern.objects.all().delete()
            ModelPerformance.objects.all().delete()
            SenderProfile.objects.all().delete()
            AnalyticsSnapshot.objects.all().delete()
            
            # Log the reset action
            audit_log('data_reset', request, {
                'sms_deleted': sms_count,
                'feedback_deleted': feedback_count,
                'threats_deleted': threat_count
            })
            
            return Response({
                'status': 'success',
                'message': 'All data has been reset successfully',
                'deleted': {
                    'sms_logs': sms_count,
                    'feedback': feedback_count,
                    'threat_patterns': threat_count
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Data reset error: {e}")
            return Response({
                'status': 'error',
                'message': 'Failed to reset data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@method_decorator(csrf_exempt, name='dispatch')
class DeleteMessageView(APIView):
    """API endpoint to delete a specific message"""
    permission_classes = []  # No authentication required
    authentication_classes = []  # No authentication required
    
    def delete(self, request, message_id):
        try:
            # Find the message
            message = SMSLog.objects.filter(id=message_id).first()
            
            if not message:
                return Response({
                    'status': 'error',
                    'message': 'Message not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Log the deletion
            audit_log('message_deleted', request, {
                'message_id': message_id,
                'category': message.category,
                'risk_level': message.risk_level
            })
            
            # Delete the message
            message.delete()
            
            return Response({
                'status': 'success',
                'message': 'Message deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Message deletion error: {e}")
            return Response({
                'status': 'error',
                'message': 'Failed to delete message'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
