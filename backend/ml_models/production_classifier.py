"""
Production-Grade SMS Classifier
Handles prediction with caching, monitoring, and error handling
"""

import logging
import time
import hashlib
from typing import Dict, Any, Optional, List
from django.core.cache import cache
from django.conf import settings
import joblib
from pathlib import Path
import numpy as np

from .model_manager import model_manager
from .pipeline import TextPreprocessor

logger = logging.getLogger('ml_models')


class ProductionClassifier:
    """
    Production-ready SMS classifier with:
    - Model caching
    - Performance monitoring
    - Error handling
    - Prediction caching
    - Confidence calibration
    """
    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.model = None
        self.label_encoder = None
        self.model_metadata = None
        self._load_models()
    
    def _load_models(self):
        """Load trained models"""
        try:
            # Load best model
            self.model = model_manager.load_model('best_model.pkl')
            self.label_encoder = model_manager.load_model('label_encoder.pkl')
            
            # Load metadata
            metadata_path = Path(settings.ML_MODELS_DIR) / 'model_metadata.json'
            if metadata_path.exists():
                import json
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                logger.info(f"Loaded model: {self.model_metadata.get('model_key', 'unknown')}")
            
            if self.model is None:
                logger.warning("No trained model found. Please run train_models.py first.")
        
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
    
    def predict(
        self,
        text: str,
        use_cache: bool = True,
        return_probabilities: bool = True
    ) -> Dict[str, Any]:
        """
        Predict SMS category with comprehensive analysis
        
        Args:
            text: Input SMS text
            use_cache: Whether to use cached predictions
            return_probabilities: Whether to return class probabilities
        
        Returns:
            Dictionary with prediction results
        """
        start_time = time.time()
        
        # Check cache
        if use_cache and settings.ENABLE_CACHING:
            cache_key = self._get_cache_key(text)
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for prediction")
                cached_result['cached'] = True
                return cached_result
        
        # Validate model
        if self.model is None or self.label_encoder is None:
            return self._get_fallback_prediction(text)
        
        try:
            # Preprocess
            text_clean = self.preprocessor.preprocess(text)
            
            # Extract features
            statistical_features = self.preprocessor.extract_features(text)
            
            # Predict
            prediction = self.model.predict([text_clean])[0]
            category = self.label_encoder.inverse_transform([prediction])[0]
            
            # Get probabilities
            probabilities = {}
            confidence = 0.0
            
            if hasattr(self.model.named_steps['classifier'], 'predict_proba'):
                proba = self.model.named_steps['classifier'].predict_proba(
                    self.model.named_steps['vectorizer'].transform([text_clean])
                )[0]
                
                for idx, prob in enumerate(proba):
                    class_name = self.label_encoder.inverse_transform([idx])[0]
                    probabilities[class_name] = float(prob)
                
                confidence = float(proba[prediction])
            else:
                # For models without predict_proba
                confidence = 0.85  # Default confidence
                probabilities[category] = confidence
            
            # Compute prediction time
            prediction_time = time.time() - start_time
            
            # Build result
            result = {
                'category': category,
                'confidence': confidence,
                'probabilities': probabilities if return_probabilities else {},
                'statistical_features': statistical_features,
                'prediction_time_ms': round(prediction_time * 1000, 2),
                'model_version': self.model_metadata.get('model_key', 'unknown') if self.model_metadata else 'unknown',
                'cached': False
            }
            
            # Cache result
            if use_cache and settings.ENABLE_CACHING:
                cache.set(cache_key, result, timeout=settings.ML_CACHE_TIMEOUT)
            
            # Log slow predictions
            if prediction_time > 0.5:
                logger.warning(f"Slow prediction: {prediction_time:.3f}s for text length {len(text)}")
            
            return result
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return self._get_fallback_prediction(text, error=str(e))
    
    def predict_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Dict[str, Any]]:
        """
        Batch prediction for multiple texts
        
        Args:
            texts: List of SMS texts
            batch_size: Batch size for processing
        
        Returns:
            List of prediction results
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = [self.predict(text) for text in batch]
            results.extend(batch_results)
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded model"""
        if self.model_metadata:
            return {
                'model_key': self.model_metadata.get('model_key', 'unknown'),
                'metrics': self.model_metadata.get('metrics', {}),
                'classes': self.model_metadata.get('classes', []),
                'loaded': True
            }
        
        return {
            'loaded': False,
            'message': 'No model loaded. Please train models first.'
        }
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        model_version = self.model_metadata.get('model_key', 'v1') if self.model_metadata else 'v1'
        return f"prediction_{model_version}_{text_hash}"
    
    def _get_fallback_prediction(self, text: str, error: str = None) -> Dict[str, Any]:
        """Return fallback prediction when model fails"""
        # Simple rule-based fallback
        text_lower = text.lower()
        
        spam_keywords = ['winner', 'prize', 'free', 'click', 'urgent', 'claim']
        otp_keywords = ['otp', 'verification', 'code', 'authenticate']
        
        spam_score = sum(1 for kw in spam_keywords if kw in text_lower)
        otp_score = sum(1 for kw in otp_keywords if kw in text_lower)
        
        if otp_score > 0:
            category = 'otp'
            confidence = 0.7
        elif spam_score >= 2:
            category = 'spam'
            confidence = 0.6
        else:
            category = 'personal'
            confidence = 0.5
        
        return {
            'category': category,
            'confidence': confidence,
            'probabilities': {category: confidence},
            'statistical_features': self.preprocessor.extract_features(text),
            'prediction_time_ms': 0,
            'model_version': 'fallback',
            'cached': False,
            'fallback': True,
            'error': error
        }
    
    def clear_cache(self):
        """Clear prediction cache"""
        # This would clear all predictions cache
        # In production, you'd want more granular control
        logger.info("Clearing prediction cache")
        cache.clear()


# Singleton instance
production_classifier = ProductionClassifier()
