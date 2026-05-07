import os
import re
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from django.conf import settings

# Optional imports for BERT
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False


class SMSClassifier:
    """Multi-model SMS classifier with ensemble of 5 ML models"""
    
    def __init__(self):
        self.models_dir = settings.ML_MODELS_DIR
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        try:
            # Load label encoder
            encoder_path = os.path.join(self.models_dir, 'label_encoder.pkl')
            if os.path.exists(encoder_path):
                with open(encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
            else:
                self.label_encoder = None
            
            # Load all 5 models (with TF-IDF vectorizer)
            self.models = {}
            model_names = [
                'naive_bayes_tfidf',
                'logistic_regression_tfidf',
                'random_forest_tfidf',
                'gradient_boosting_tfidf',
                'svm_tfidf'
            ]
            
            for model_name in model_names:
                model_path = os.path.join(self.models_dir, f'{model_name}_model.pkl')
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    print(f"Loaded model: {model_name}")
                else:
                    print(f"Model not found: {model_name}")
            
            # Load best model as fallback
            best_model_path = os.path.join(self.models_dir, 'best_model.pkl')
            if os.path.exists(best_model_path) and 'naive_bayes_tfidf' not in self.models:
                with open(best_model_path, 'rb') as f:
                    self.models['naive_bayes_tfidf'] = pickle.load(f)
                print("Loaded best model as Naive Bayes")
            
            # Load BERT model (optional)
            if not BERT_AVAILABLE:
                self.tokenizer = None
                self.bert_model = None
                return
                
            try:
                bert_path = os.path.join(self.models_dir, 'bert_model')
                if os.path.exists(bert_path):
                    self.tokenizer = AutoTokenizer.from_pretrained(bert_path)
                    self.bert_model = AutoModelForSequenceClassification.from_pretrained(bert_path)
                else:
                    self.tokenizer = None
                    self.bert_model = None
            except Exception as e:
                print(f"BERT model loading failed: {e}")
                self.tokenizer = None
                self.bert_model = None
                
        except Exception as e:
            print(f"Model loading error: {e}")
            self.models = {}
            self.label_encoder = None
            self.tokenizer = None
            self.bert_model = None
    
    def preprocess_text(self, text, language='en'):
        """Preprocess SMS text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Handle Hinglish/multilingual text
        if language in ['hi', 'mr']:
            # Keep unicode characters for Indian languages
            pass
        
        return text
    
    def predict_all_models(self, text):
        """Get predictions from all 5 models"""
        predictions = {}
        
        for model_name, model in self.models.items():
            try:
                prediction = model.predict([text])[0]
                probabilities = model.predict_proba([text])[0]
                confidence = float(max(probabilities))
                
                # Convert numeric prediction to category name
                if self.label_encoder:
                    category = self.label_encoder.inverse_transform([prediction])[0]
                else:
                    category = prediction
                
                predictions[model_name] = {
                    'category': category,
                    'confidence': confidence,
                    'probabilities': {
                        self.label_encoder.inverse_transform([i])[0] if self.label_encoder else str(i): float(prob)
                        for i, prob in enumerate(probabilities)
                    }
                }
            except Exception as e:
                print(f"Error predicting with {model_name}: {e}")
                predictions[model_name] = {
                    'category': 'error',
                    'confidence': 0.0,
                    'probabilities': {}
                }
        
        return predictions
    
    def predict_naive_bayes(self, text):
        """Predict using Naive Bayes model (backward compatibility)"""
        if 'naive_bayes_tfidf' not in self.models:
            return self._rule_based_classification(text)
        
        try:
            model = self.models['naive_bayes_tfidf']
            prediction = model.predict([text])[0]
            probabilities = model.predict_proba([text])[0]
            confidence = float(max(probabilities))
            
            # Convert numeric prediction to category name
            if self.label_encoder:
                category = self.label_encoder.inverse_transform([prediction])[0]
            else:
                category = prediction
            
            return {
                'category': category,
                'confidence': confidence,
                'probabilities': {
                    self.label_encoder.inverse_transform([i])[0] if self.label_encoder else str(i): float(prob)
                    for i, prob in enumerate(probabilities)
                }
            }
        except Exception as e:
            print(f"Naive Bayes prediction error: {e}")
            return self._rule_based_classification(text)
    
    def predict_bert(self, text):
        """Predict using BERT model"""
        if self.bert_model is None or self.tokenizer is None:
            return None
        
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)[0]
                prediction = torch.argmax(probabilities).item()
            
            categories = ['spam', 'promotion', 'otp', 'important', 'personal']
            
            return {
                'category': categories[prediction],
                'confidence': float(probabilities[prediction]),
                'probabilities': {
                    cat: float(prob)
                    for cat, prob in zip(categories, probabilities)
                }
            }
        except Exception as e:
            print(f"BERT prediction error: {e}")
            return None
    
    def _rule_based_classification(self, text):
        """Fallback rule-based classification"""
        text_lower = text.lower()
        
        # OTP detection
        otp_patterns = [
            r'\b\d{4,6}\b',  # 4-6 digit codes
            r'otp',
            r'verification code',
            r'security code'
        ]
        if any(re.search(pattern, text_lower) for pattern in otp_patterns):
            return {
                'category': 'otp',
                'confidence': 0.85,
                'probabilities': {'otp': 0.85, 'important': 0.10, 'personal': 0.05}
            }
        
        # Spam detection
        spam_keywords = [
            'win', 'winner', 'prize', 'free', 'claim', 'congratulations',
            'click here', 'urgent', 'limited time', 'act now', 'call now'
        ]
        spam_score = sum(1 for keyword in spam_keywords if keyword in text_lower)
        if spam_score >= 2:
            return {
                'category': 'spam',
                'confidence': min(0.7 + spam_score * 0.05, 0.95),
                'probabilities': {'spam': 0.80, 'promotion': 0.15, 'personal': 0.05}
            }
        
        # Promotion detection
        promo_keywords = ['offer', 'discount', 'sale', 'deal', 'shop', 'buy']
        if any(keyword in text_lower for keyword in promo_keywords):
            return {
                'category': 'promotion',
                'confidence': 0.75,
                'probabilities': {'promotion': 0.75, 'spam': 0.15, 'personal': 0.10}
            }
        
        # Important detection
        important_keywords = ['bank', 'account', 'payment', 'transaction', 'alert']
        if any(keyword in text_lower for keyword in important_keywords):
            return {
                'category': 'important',
                'confidence': 0.80,
                'probabilities': {'important': 0.80, 'otp': 0.10, 'personal': 0.10}
            }
        
        # Default to personal
        return {
            'category': 'personal',
            'confidence': 0.70,
            'probabilities': {'personal': 0.70, 'important': 0.20, 'spam': 0.10}
        }
    
    def _fallback_prediction(self, text):
        """
        Fallback prediction when no models are loaded
        Uses simple keyword-based classification
        """
        text_lower = text.lower()
        
        # Spam detection
        spam_keywords = ['win', 'winner', 'prize', 'free', 'click here', 'claim', 'congratulations', 'offer']
        if any(keyword in text_lower for keyword in spam_keywords):
            return {
                'category': 'spam',
                'confidence': 0.75,
                'probabilities': {'spam': 0.75, 'promotion': 0.15, 'personal': 0.10}
            }
        
        # OTP detection
        otp_keywords = ['otp', 'verification code', 'verify', 'code is']
        if any(keyword in text_lower for keyword in otp_keywords):
            return {
                'category': 'otp',
                'confidence': 0.85,
                'probabilities': {'otp': 0.85, 'important': 0.10, 'personal': 0.05}
            }
        
        # Promotion detection
        promo_keywords = ['sale', 'discount', 'offer', 'deal', 'shop']
        if any(keyword in text_lower for keyword in promo_keywords):
            return {
                'category': 'promotion',
                'confidence': 0.70,
                'probabilities': {'promotion': 0.70, 'spam': 0.20, 'personal': 0.10}
            }
        
        # Important detection
        important_keywords = ['bank', 'account', 'payment', 'transaction', 'alert']
        if any(keyword in text_lower for keyword in important_keywords):
            return {
                'category': 'important',
                'confidence': 0.80,
                'probabilities': {'important': 0.80, 'otp': 0.10, 'personal': 0.10}
            }
        
        # Default to personal
        return {
            'category': 'personal',
            'confidence': 0.70,
            'probabilities': {'personal': 0.70, 'important': 0.20, 'spam': 0.10}
        }
    
    def predict(self, text, language='en'):
        """
        Predict SMS category using ensemble of all models
        Returns prediction with confidence scores from all models
        """
        if not self.models:
            return self._fallback_prediction(text)
        
        # Preprocess text
        processed_text = self.preprocess_text(text, language)
        
        # Get predictions from all models
        all_predictions = {}
        all_probabilities = {}
        
        for model_name, model in self.models.items():
            try:
                # Get prediction
                pred = model.predict([processed_text])[0]
                
                # Get probability if available
                if hasattr(model.named_steps['classifier'], 'predict_proba'):
                    proba = model.predict_proba([processed_text])[0]
                    all_probabilities[model_name] = proba
                elif hasattr(model.named_steps['classifier'], 'decision_function'):
                    # For SVM, convert decision function to probabilities
                    decision = model.decision_function([processed_text])[0]
                    # Softmax to convert to probabilities
                    exp_scores = np.exp(decision - np.max(decision))
                    proba = exp_scores / exp_scores.sum()
                    all_probabilities[model_name] = proba
                else:
                    # Create one-hot probability
                    proba = np.zeros(len(self.label_encoder.classes_))
                    proba[pred] = 1.0
                    all_probabilities[model_name] = proba
                
                all_predictions[model_name] = pred
                
            except Exception as e:
                print(f"Error with model {model_name}: {e}")
                continue
        
        if not all_predictions:
            return self._fallback_prediction(text)
        
        # Ensemble voting: Average probabilities from all models
        avg_probabilities = np.mean(list(all_probabilities.values()), axis=0)
        
        # Get final prediction (class with highest average probability)
        final_prediction = np.argmax(avg_probabilities)
        final_confidence = float(avg_probabilities[final_prediction])
        
        # Get category name
        if self.label_encoder:
            category = self.label_encoder.inverse_transform([final_prediction])[0]
        else:
            category = str(final_prediction)
        
        # Prepare individual model predictions for comparison
        model_predictions = {}
        for model_name, pred_idx in all_predictions.items():
            if self.label_encoder:
                pred_category = self.label_encoder.inverse_transform([pred_idx])[0]
            else:
                pred_category = str(pred_idx)
            
            model_predictions[model_name] = {
                'category': pred_category,
                'confidence': float(all_probabilities[model_name][pred_idx])
            }
        
        return {
            'category': category,
            'confidence': final_confidence,
            'model_predictions': model_predictions,
            'ensemble_method': 'average_probability'
        }
        """Predict SMS category using ensemble of all models"""
        # Preprocess
        processed_text = self.preprocess_text(text, language)
        
        # Get predictions from all 5 models
        all_predictions = self.predict_all_models(processed_text)
        
        # Get BERT prediction
        bert_result = self.predict_bert(processed_text)
        
        # Ensemble: Use voting or averaging
        if all_predictions:
            # Count votes for each category
            category_votes = {}
            category_confidences = {}
            
            for model_name, pred in all_predictions.items():
                if pred['category'] != 'error':
                    cat = pred['category']
                    category_votes[cat] = category_votes.get(cat, 0) + 1
                    if cat not in category_confidences:
                        category_confidences[cat] = []
                    category_confidences[cat].append(pred['confidence'])
            
            # Final category: most votes
            if category_votes:
                final_category = max(category_votes.items(), key=lambda x: x[1])[0]
                # Average confidence from models that predicted this category
                final_confidence = sum(category_confidences[final_category]) / len(category_confidences[final_category])
            else:
                # Fallback to Naive Bayes
                nb_result = all_predictions.get('naive_bayes_tfidf', {})
                final_category = nb_result.get('category', 'personal')
                final_confidence = nb_result.get('confidence', 0.5)
        else:
            # No models loaded, use rule-based
            fallback = self._rule_based_classification(processed_text)
            final_category = fallback['category']
            final_confidence = fallback['confidence']
            all_predictions = {}
        
        # Build model comparison
        model_comparison = {}
        
        # Add all 5 model predictions
        model_display_names = {
            'naive_bayes_tfidf': 'Naive Bayes',
            'logistic_regression_tfidf': 'Logistic Regression',
            'random_forest_tfidf': 'Random Forest',
            'gradient_boosting_tfidf': 'Gradient Boosting',
            'svm_tfidf': 'SVM'
        }
        
        for model_key, display_name in model_display_names.items():
            if model_key in all_predictions:
                model_comparison[display_name.lower().replace(' ', '_')] = {
                    'category': all_predictions[model_key]['category'],
                    'confidence': all_predictions[model_key]['confidence']
                }
        
        # Add BERT if available
        if bert_result:
            model_comparison['bert'] = {
                'category': bert_result['category'],
                'confidence': bert_result['confidence']
            }
        
        return {
            'category': final_category,
            'confidence': round(final_confidence, 4),
            'model_comparison': model_comparison
        }
