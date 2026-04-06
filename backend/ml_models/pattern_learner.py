"""
Pattern Learning Module
Implements online learning and pattern recognition
"""

import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta


class PatternLearner:
    """Learn and identify emerging threat patterns"""
    
    def __init__(self):
        self.patterns = defaultdict(lambda: {'count': 0, 'examples': [], 'severity': 'low'})
        self.ngram_cache = {}
    
    def extract_ngrams(self, text, n=3):
        """Extract n-grams from text"""
        words = re.findall(r'\b\w+\b', text.lower())
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)
        return ngrams
    
    def learn_pattern(self, text, is_threat=False):
        """Learn patterns from new messages"""
        if not is_threat:
            return
        
        # Extract 2-grams and 3-grams
        bigrams = self.extract_ngrams(text, 2)
        trigrams = self.extract_ngrams(text, 3)
        
        # Update pattern counts
        for ngram in bigrams + trigrams:
            self.patterns[ngram]['count'] += 1
            if len(self.patterns[ngram]['examples']) < 5:
                self.patterns[ngram]['examples'].append(text[:100])
            
            # Update severity based on frequency
            count = self.patterns[ngram]['count']
            if count > 10:
                self.patterns[ngram]['severity'] = 'high'
            elif count > 5:
                self.patterns[ngram]['severity'] = 'medium'
    
    def get_top_patterns(self, limit=10):
        """Get most frequent threat patterns"""
        sorted_patterns = sorted(
            self.patterns.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        return sorted_patterns[:limit]
    
    def check_pattern_match(self, text):
        """Check if text matches known threat patterns"""
        text_lower = text.lower()
        matches = []
        
        for pattern, info in self.patterns.items():
            if pattern in text_lower and info['count'] > 3:
                matches.append({
                    'pattern': pattern,
                    'severity': info['severity'],
                    'frequency': info['count']
                })
        
        return matches


class AnomalyDetector:
    """Detect anomalous message patterns"""
    
    def __init__(self):
        self.baseline_stats = {
            'avg_length': 100,
            'avg_word_count': 15,
            'avg_caps_ratio': 0.1,
            'avg_special_chars': 5
        }
        self.message_history = []
    
    def update_baseline(self, text):
        """Update baseline statistics"""
        self.message_history.append({
            'length': len(text),
            'word_count': len(text.split()),
            'caps_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1),
            'special_chars': len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', text))
        })
        
        # Keep only last 1000 messages
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-1000:]
        
        # Recalculate baseline
        if len(self.message_history) > 10:
            self.baseline_stats['avg_length'] = sum(m['length'] for m in self.message_history) / len(self.message_history)
            self.baseline_stats['avg_word_count'] = sum(m['word_count'] for m in self.message_history) / len(self.message_history)
            self.baseline_stats['avg_caps_ratio'] = sum(m['caps_ratio'] for m in self.message_history) / len(self.message_history)
            self.baseline_stats['avg_special_chars'] = sum(m['special_chars'] for m in self.message_history) / len(self.message_history)
    
    def detect_anomaly(self, text):
        """
        Detect if message is anomalous
        Returns: anomaly_score (0-1) and anomaly_reasons
        """
        length = len(text)
        word_count = len(text.split())
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        special_chars = len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', text))
        
        anomaly_score = 0.0
        reasons = []
        
        # Check length anomaly
        if length > self.baseline_stats['avg_length'] * 2:
            anomaly_score += 0.2
            reasons.append('Unusually long message')
        elif length < self.baseline_stats['avg_length'] * 0.3:
            anomaly_score += 0.1
            reasons.append('Unusually short message')
        
        # Check caps ratio
        if caps_ratio > self.baseline_stats['avg_caps_ratio'] * 3:
            anomaly_score += 0.3
            reasons.append('Excessive capitalization')
        
        # Check special characters
        if special_chars > self.baseline_stats['avg_special_chars'] * 2:
            anomaly_score += 0.2
            reasons.append('Excessive special characters')
        
        # Check for repeated characters
        if re.search(r'(.)\1{4,}', text):
            anomaly_score += 0.2
            reasons.append('Repeated characters detected')
        
        # Check for unusual character sequences
        if re.search(r'[^a-zA-Z0-9\s]{5,}', text):
            anomaly_score += 0.15
            reasons.append('Unusual character sequences')
        
        anomaly_score = min(anomaly_score, 1.0)
        
        return {
            'is_anomalous': anomaly_score > 0.5,
            'anomaly_score': round(anomaly_score, 4),
            'reasons': reasons
        }


class TemporalAnalyzer:
    """Analyze temporal patterns in messages"""
    
    def __init__(self):
        self.message_timestamps = []
        self.hourly_distribution = defaultdict(int)
    
    def add_message(self, timestamp=None):
        """Add message timestamp"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.message_timestamps.append(timestamp)
        hour = timestamp.hour
        self.hourly_distribution[hour] += 1
        
        # Keep only last 7 days
        cutoff = datetime.now() - timedelta(days=7)
        self.message_timestamps = [ts for ts in self.message_timestamps if ts > cutoff]
    
    def detect_burst(self, window_minutes=10, threshold=5):
        """Detect message bursts (potential spam campaigns)"""
        if len(self.message_timestamps) < threshold:
            return False
        
        now = datetime.now()
        recent = [ts for ts in self.message_timestamps if (now - ts).total_seconds() < window_minutes * 60]
        
        return len(recent) >= threshold
    
    def get_peak_hours(self):
        """Get hours with most message activity"""
        if not self.hourly_distribution:
            return []
        
        sorted_hours = sorted(
            self.hourly_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_hours[:3]
    
    def analyze_timing(self):
        """Analyze message timing patterns"""
        if len(self.message_timestamps) < 10:
            return {
                'is_burst': False,
                'messages_last_hour': 0,
                'peak_hours': []
            }
        
        now = datetime.now()
        last_hour = [ts for ts in self.message_timestamps if (now - ts).total_seconds() < 3600]
        
        return {
            'is_burst': self.detect_burst(),
            'messages_last_hour': len(last_hour),
            'peak_hours': self.get_peak_hours(),
            'total_messages_7days': len(self.message_timestamps)
        }
