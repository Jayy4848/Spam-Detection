from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
import hashlib

from .models import SMSLog, UserFeedback, ThreatPattern, ModelPerformance, SenderProfile, AnalyticsSnapshot
from .serializers import (
    SMSPredictionSerializer, SMSResultSerializer,
    FeedbackSerializer, SMSLogSerializer
)
from ml_models.classifier import SMSClassifier
from ml_models.phishing_detector import PhishingDetector
from ml_models.explainer import ExplainableAI
from ml_models.advanced_analyzer import AdvancedAnalyzer
from ml_models.pattern_learner import PatternLearner, AnomalyDetector, TemporalAnalyzer
from ml_models.ensemble_model import EnsembleClassifier, AdaptiveLearner, ConfidenceCalibrator
from ml_models.deep_learning import NeuralFeatureExtractor, TransferLearningSimulator, AttentionMechanism


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
        serializer = SMSPredictionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message = serializer.validated_data['message']
        language = serializer.validated_data.get('language', 'en')
        
        # Generate hash for privacy
        message_hash = hashlib.sha256(message.encode()).hexdigest()
        
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
