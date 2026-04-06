"""
Production-Grade API Views V2
Professional implementation with comprehensive features
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
import logging
import hashlib

from .models import SMSLog, UserFeedback
from .serializers import SMSPredictionSerializer, FeedbackSerializer
from .metrics import MetricsCollector
from ml_models.production_classifier import production_classifier
from ml_models.phishing_detector import PhishingDetector
from ml_models.explainer import ExplainableAI

logger = logging.getLogger('api')


class PredictRateThrottle(AnonRateThrottle):
    """Custom throttle for prediction endpoint"""
    rate = '50/minute'


class PredictViewV2(APIView):
    """
    Professional SMS Classification Endpoint
    
    Features:
    - Production-grade classifier with caching
    - Comprehensive error handling
    - Performance monitoring
    - Rate limiting
    - Detailed logging
    """
    
    throttle_classes = [PredictRateThrottle]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.phishing_detector = PhishingDetector()
        self.explainer = ExplainableAI()
    
    def post(self, request):
        """Handle SMS classification request"""
        # Validate input
        serializer = SMSPredictionSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Invalid request data: {serializer.errors}")
            return Response(
                {'error': 'Invalid input', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message = serializer.validated_data['message']
        language = serializer.validated_data.get('language', 'en')
        
        logger.info(f"Processing prediction request (length: {len(message)}, language: {language})")
        
        try:
            # Generate message hash for privacy
            message_hash = hashlib.sha256(message.encode()).hexdigest()
            
            # Get prediction from production classifier
            prediction_result = production_classifier.predict(
                text=message,
                use_cache=settings.ENABLE_CACHING,
                return_probabilities=True
            )
            
            # Phishing detection
            phishing_result = self.phishing_detector.detect(message, language)
            
            # Explainable AI
            explanation = self.explainer.explain(
                message,
                prediction_result['category'],
                prediction_result['confidence'],
                phishing_result['score']
            )
            
            # Determine risk level
            risk_score = self._calculate_risk_score(
                prediction_result,
                phishing_result
            )
            risk_level = self._get_risk_level(risk_score)
            
            # Save to database
            sms_log = SMSLog.objects.create(
                category=prediction_result['category'],
                confidence=prediction_result['confidence'],
                is_phishing=phishing_result['is_phishing'],
                phishing_score=phishing_result['score'],
                risk_level=risk_level,
                message_hash=message_hash,
                language=language,
                sentiment_score=0.0,  # Can be enhanced
                urgency_score=phishing_result['score'],
                sender_reputation=0.5,
                message_length=len(message),
                has_urls=prediction_result['statistical_features']['url_count'] > 0,
                has_phone_numbers=prediction_result['statistical_features']['phone_count'] > 0,
                has_financial_terms=False  # Can be enhanced
            )
            
            # Build comprehensive response
            response_data = {
                'message_id': str(sms_log.id),
                'category': prediction_result['category'],
                'confidence': prediction_result['confidence'],
                'probabilities': prediction_result['probabilities'],
                
                # Phishing detection
                'is_phishing': phishing_result['is_phishing'],
                'phishing_score': phishing_result['score'],
                'suspicious_keywords': phishing_result['keywords'],
                'suspicious_urls': phishing_result['urls'],
                
                # Risk assessment
                'risk_level': risk_level,
                'risk_score': risk_score,
                
                # Explainability
                'highlighted_words': explanation['highlighted_words'],
                'explanation': explanation.get('explanation', ''),
                
                # Statistical features
                'statistical_features': prediction_result['statistical_features'],
                
                # Model metadata
                'model_version': prediction_result['model_version'],
                'prediction_time_ms': prediction_result['prediction_time_ms'],
                'cached': prediction_result['cached'],
                
                # Timestamp
                'timestamp': timezone.now().isoformat()
            }
            
            logger.info(
                f"Prediction successful: category={prediction_result['category']}, "
                f"confidence={prediction_result['confidence']:.4f}, "
                f"time={prediction_result['prediction_time_ms']}ms"
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Internal server error',
                    'message': 'An error occurred while processing your request',
                    'details': str(e) if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _calculate_risk_score(self, prediction_result, phishing_result):
        """Calculate overall risk score"""
        # Weighted combination of factors
        category_risk = {
            'spam': 0.7,
            'promotion': 0.3,
            'otp': 0.1,
            'important': 0.2,
            'personal': 0.1
        }
        
        base_risk = category_risk.get(prediction_result['category'], 0.5)
        phishing_risk = phishing_result['score']
        confidence_factor = prediction_result['confidence']
        
        # Combine risks
        risk_score = (
            base_risk * 0.4 +
            phishing_risk * 0.5 +
            (1 - confidence_factor) * 0.1
        )
        
        return round(risk_score, 4)
    
    def _get_risk_level(self, risk_score):
        """Convert risk score to level"""
        if risk_score >= 0.7:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'


class MetricsView(APIView):
    """
    System Metrics Endpoint
    Provides comprehensive system and model metrics
    """
    
    def get(self, request):
        """Get all system metrics"""
        try:
            metrics = MetricsCollector.get_comprehensive_metrics()
            return Response(metrics, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            return Response(
                {'error': 'Failed to collect metrics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModelInfoView(APIView):
    """
    Model Information Endpoint
    Provides details about the loaded ML model
    """
    
    def get(self, request):
        """Get model information"""
        try:
            model_info = production_classifier.get_model_info()
            return Response(model_info, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return Response(
                {'error': 'Failed to get model information'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CacheClearView(APIView):
    """
    Cache Management Endpoint
    Allows clearing prediction cache
    """
    
    def post(self, request):
        """Clear prediction cache"""
        try:
            production_classifier.clear_cache()
            logger.info("Prediction cache cleared")
            return Response(
                {'message': 'Cache cleared successfully'},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return Response(
                {'error': 'Failed to clear cache'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
