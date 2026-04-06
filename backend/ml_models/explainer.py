import re
import numpy as np


class ExplainableAI:
    """Provide explanations for SMS classifications"""
    
    def __init__(self):
        # Category-specific important words
        self.category_keywords = {
            'spam': [
                'win', 'winner', 'prize', 'free', 'claim', 'congratulations',
                'click', 'urgent', 'limited', 'offer', 'call now', 'act now'
            ],
            'promotion': [
                'offer', 'discount', 'sale', 'deal', 'shop', 'buy',
                'save', 'special', 'exclusive', 'limited', 'today only'
            ],
            'otp': [
                'otp', 'code', 'verification', 'verify', 'authenticate',
                'security', 'pin', 'password', 'login', 'access'
            ],
            'important': [
                'bank', 'account', 'payment', 'transaction', 'alert',
                'statement', 'balance', 'credit', 'debit', 'due'
            ],
            'personal': [
                'hi', 'hello', 'how', 'thanks', 'please', 'meet',
                'call', 'message', 'talk', 'see', 'love', 'miss'
            ]
        }
    
    def tokenize(self, text):
        """Simple tokenization"""
        # Split by whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def calculate_word_importance(self, text, category):
        """Calculate importance score for each word"""
        tokens = self.tokenize(text)
        word_scores = {}
        
        # Get category keywords
        category_words = self.category_keywords.get(category, [])
        
        for token in tokens:
            score = 0.0
            
            # Exact match with category keywords
            if token in category_words:
                score = 0.9
            # Partial match
            elif any(keyword in token or token in keyword for keyword in category_words):
                score = 0.6
            # Contains numbers (important for OTP)
            elif category == 'otp' and re.search(r'\d', token):
                score = 0.8
            # All caps (often important or spam)
            elif token.isupper() and len(token) > 2:
                score = 0.5
            # Default low importance
            else:
                score = 0.2
            
            word_scores[token] = score
        
        return word_scores
    
    def highlight_words(self, text, category):
        """Highlight important words in text"""
        word_scores = self.calculate_word_importance(text, category)
        
        # Create highlighted version
        highlighted = []
        words = text.split()
        
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word.lower())
            score = word_scores.get(clean_word, 0.0)
            
            # Determine highlight level
            if score >= 0.7:
                level = 'high'
            elif score >= 0.4:
                level = 'medium'
            else:
                level = 'low'
            
            highlighted.append({
                'word': word,
                'score': round(score, 2),
                'level': level
            })
        
        return highlighted
    
    def generate_explanation(self, category, confidence, phishing_score=0.0):
        """Generate human-readable explanation"""
        explanations = {
            'spam': "This message contains typical spam indicators like promotional language, urgency triggers, or suspicious links.",
            'promotion': "This appears to be a promotional message with marketing content about offers, discounts, or sales.",
            'otp': "This message contains a one-time password or verification code for authentication purposes.",
            'important': "This is an important message, likely from a bank, service provider, or official source requiring attention.",
            'personal': "This appears to be a personal message from someone you know or a casual conversation."
        }
        
        base_explanation = explanations.get(category, "Unable to determine message type.")
        
        # Add confidence information
        confidence_text = f" Confidence: {confidence*100:.1f}%."
        
        # Add phishing warning if applicable
        phishing_text = ""
        if phishing_score >= 0.5:
            phishing_text = f" ⚠️ Warning: This message shows signs of phishing (risk score: {phishing_score*100:.0f}%). Be cautious about clicking links or sharing personal information."
        
        return base_explanation + confidence_text + phishing_text
    
    def explain(self, text, category, confidence=0.0, phishing_score=0.0):
        """Main explanation method"""
        highlighted_words = self.highlight_words(text, category)
        explanation_text = self.generate_explanation(category, confidence, phishing_score)
        
        # Extract key indicators
        word_scores = self.calculate_word_importance(text, category)
        top_indicators = sorted(
            word_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'highlighted_words': highlighted_words,
            'explanation': explanation_text,
            'top_indicators': [
                {'word': word, 'score': round(score, 2)}
                for word, score in top_indicators
            ]
        }
