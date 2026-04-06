"""
Advanced SMS Analysis Module
Includes sentiment analysis, urgency detection, and behavioral patterns
"""

import re
from collections import Counter


class SentimentAnalyzer:
    """Analyze sentiment of SMS messages"""
    
    def __init__(self):
        self.positive_words = [
            'happy', 'great', 'excellent', 'good', 'wonderful', 'amazing',
            'love', 'best', 'thank', 'thanks', 'congratulations', 'success'
        ]
        self.negative_words = [
            'bad', 'terrible', 'worst', 'hate', 'angry', 'sad', 'sorry',
            'problem', 'issue', 'error', 'fail', 'wrong', 'urgent', 'warning'
        ]
        self.neutral_words = [
            'information', 'update', 'notice', 'reminder', 'message'
        ]
    
    def analyze(self, text):
        """
        Analyze sentiment of text
        Returns: score between -1 (negative) and 1 (positive)
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        sentiment_score = (positive_count - negative_count) / total
        return round(sentiment_score, 4)


class UrgencyDetector:
    """Detect urgency level in messages"""
    
    def __init__(self):
        self.urgency_keywords = {
            'critical': ['urgent', 'immediately', 'asap', 'emergency', 'critical', 'now'],
            'high': ['soon', 'quickly', 'hurry', 'fast', 'today', 'tonight'],
            'medium': ['tomorrow', 'this week', 'reminder', 'please'],
            'low': ['whenever', 'no rush', 'at your convenience']
        }
        
        self.urgency_patterns = [
            r'within \d+ (hour|minute|day)',
            r'expire[sd]? (today|tomorrow|soon)',
            r'act now',
            r'limited time',
            r'last chance'
        ]
    
    def detect(self, text):
        """
        Detect urgency level
        Returns: score between 0 (no urgency) and 1 (critical urgency)
        """
        text_lower = text.lower()
        urgency_score = 0.0
        
        # Check keywords
        for level, keywords in self.urgency_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if level == 'critical':
                        urgency_score = max(urgency_score, 1.0)
                    elif level == 'high':
                        urgency_score = max(urgency_score, 0.75)
                    elif level == 'medium':
                        urgency_score = max(urgency_score, 0.5)
                    elif level == 'low':
                        urgency_score = max(urgency_score, 0.25)
        
        # Check patterns
        for pattern in self.urgency_patterns:
            if re.search(pattern, text_lower):
                urgency_score = max(urgency_score, 0.8)
        
        # Check for exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count >= 3:
            urgency_score = max(urgency_score, 0.7)
        elif exclamation_count >= 1:
            urgency_score = max(urgency_score, 0.4)
        
        # Check for all caps words
        words = text.split()
        caps_ratio = sum(1 for word in words if word.isupper() and len(word) > 2) / max(len(words), 1)
        if caps_ratio > 0.3:
            urgency_score = max(urgency_score, 0.6)
        
        return round(urgency_score, 4)


class BehavioralAnalyzer:
    """Analyze behavioral patterns in messages"""
    
    def __init__(self):
        self.financial_terms = [
            'bank', 'account', 'credit', 'debit', 'payment', 'transaction',
            'money', 'cash', 'rupees', 'rs', 'dollar', 'amount', 'balance',
            'loan', 'emi', 'interest', 'refund', 'cashback'
        ]
        
        self.personal_info_patterns = [
            r'\b\d{10}\b',  # Phone numbers
            r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',  # Card numbers
            r'\b[A-Z]{5}\d{4}[A-Z]\b',  # PAN card
            r'\b\d{12}\b',  # Aadhar
        ]
    
    def analyze(self, text):
        """
        Analyze behavioral patterns
        Returns: dict with various behavioral indicators
        """
        text_lower = text.lower()
        
        # Check for financial terms
        has_financial = any(term in text_lower for term in self.financial_terms)
        financial_count = sum(1 for term in self.financial_terms if term in text_lower)
        
        # Check for personal info patterns
        has_personal_info = any(re.search(pattern, text) for pattern in self.personal_info_patterns)
        
        # Check for URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        has_urls = len(urls) > 0
        
        # Check for phone numbers
        phone_pattern = r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        has_phone = bool(re.search(phone_pattern, text))
        
        # Calculate message complexity
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        
        # Check for action requests
        action_words = ['click', 'call', 'reply', 'send', 'share', 'forward', 'download']
        action_count = sum(1 for word in action_words if word in text_lower)
        
        return {
            'has_financial_terms': has_financial,
            'financial_term_count': financial_count,
            'has_personal_info': has_personal_info,
            'has_urls': has_urls,
            'url_count': len(urls),
            'has_phone_numbers': has_phone,
            'message_length': len(text),
            'word_count': len(words),
            'avg_word_length': round(avg_word_length, 2),
            'action_request_count': action_count,
            'complexity_score': round(avg_word_length / 10, 2)
        }


class RiskScorer:
    """Calculate comprehensive risk score"""
    
    def calculate_risk(self, classification, phishing_score, sentiment, urgency, behavioral):
        """
        Calculate overall risk score
        Returns: risk_level and risk_score
        """
        risk_score = 0.0
        
        # Category-based risk
        category_risk = {
            'spam': 0.7,
            'promotion': 0.3,
            'otp': 0.1,
            'important': 0.2,
            'personal': 0.1
        }
        risk_score += category_risk.get(classification, 0.5) * 0.3
        
        # Phishing score contribution
        risk_score += phishing_score * 0.4
        
        # Urgency contribution
        risk_score += urgency * 0.15
        
        # Behavioral factors
        if behavioral['has_urls']:
            risk_score += 0.1
        if behavioral['has_phone_numbers']:
            risk_score += 0.05
        if behavioral['has_financial_terms']:
            risk_score += 0.1
        if behavioral['action_request_count'] > 2:
            risk_score += 0.1
        
        # Sentiment contribution (negative sentiment increases risk)
        if sentiment < -0.3:
            risk_score += 0.1
        
        # Normalize to 0-1
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = 'critical'
        elif risk_score >= 0.6:
            risk_level = 'high'
        elif risk_score >= 0.4:
            risk_level = 'medium'
        elif risk_score >= 0.2:
            risk_level = 'low'
        else:
            risk_level = 'safe'
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 4)
        }


class AdvancedAnalyzer:
    """Main advanced analysis coordinator"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.urgency_detector = UrgencyDetector()
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.risk_scorer = RiskScorer()
    
    def analyze(self, text, classification, phishing_score):
        """
        Perform comprehensive advanced analysis
        """
        # Sentiment analysis
        sentiment_score = self.sentiment_analyzer.analyze(text)
        
        # Urgency detection
        urgency_score = self.urgency_detector.detect(text)
        
        # Behavioral analysis
        behavioral_features = self.behavioral_analyzer.analyze(text)
        
        # Risk scoring
        risk_info = self.risk_scorer.calculate_risk(
            classification, phishing_score, sentiment_score, 
            urgency_score, behavioral_features
        )
        
        return {
            'sentiment_score': sentiment_score,
            'urgency_score': urgency_score,
            'behavioral_features': behavioral_features,
            'risk_level': risk_info['risk_level'],
            'risk_score': risk_info['risk_score']
        }
