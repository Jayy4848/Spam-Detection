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
    """Multi-model SMS classifier with Naive Bayes and BERT"""
    
    def __init__(self):
        self.models_dir = settings.ML_MODELS_DIR
        self.load_models()
    
    def load_models(self):
        """Load trained models"""
        try:
            # Load Naive Bayes model
            nb_path = os.path.join(self.models_dir, 'naive_bayes_model.pkl')
            vectorizer_path = os.path.join(self.models_dir, 'tfidf_vectorizer.pkl')
            
            if os.path.exists(nb_path) and os.path.exists(vectorizer_path):
                with open(nb_path, 'rb') as f:
                    self.nb_model = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            else:
                # Initialize with default models
                self.nb_model = None
                self.vectorizer = None
            
            # Load BERT model (using lightweight DistilBERT)
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
                    # Use pre-trained model as fallback
                    self.tokenizer = None
                    self.bert_model = None
            except Exception as e:
                print(f"BERT model loading failed: {e}")
                self.tokenizer = None
                self.bert_model = None
                
        except Exception as e:
            print(f"Model loading error: {e}")
            self.nb_model = None
            self.vectorizer = None
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
    
    def predict_naive_bayes(self, text):
        """Predict using Naive Bayes model"""
        if self.nb_model is None or self.vectorizer is None:
            # Fallback rule-based classification
            return self._rule_based_classification(text)
        
        try:
            text_vectorized = self.vectorizer.transform([text])
            prediction = self.nb_model.predict(text_vectorized)[0]
            probabilities = self.nb_model.predict_proba(text_vectorized)[0]
            confidence = float(max(probabilities))
            
            return {
                'category': prediction,
                'confidence': confidence,
                'probabilities': {
                    cat: float(prob) 
                    for cat, prob in zip(self.nb_model.classes_, probabilities)
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
    
    def predict(self, text, language='en'):
        """Predict SMS category using multiple models"""
        # Preprocess
        processed_text = self.preprocess_text(text, language)
        
        # Get predictions from both models
        nb_result = self.predict_naive_bayes(processed_text)
        bert_result = self.predict_bert(processed_text)
        
        # Ensemble: Use BERT if available, otherwise Naive Bayes
        if bert_result:
            final_category = bert_result['category']
            final_confidence = (nb_result['confidence'] + bert_result['confidence']) / 2
        else:
            final_category = nb_result['category']
            final_confidence = nb_result['confidence']
        
        return {
            'category': final_category,
            'confidence': round(final_confidence, 4),
            'model_comparison': {
                'naive_bayes': {
                    'category': nb_result['category'],
                    'confidence': round(nb_result['confidence'], 4)
                },
                'bert': {
                    'category': bert_result['category'] if bert_result else 'N/A',
                    'confidence': round(bert_result['confidence'], 4) if bert_result else 0
                }
            }
        }
