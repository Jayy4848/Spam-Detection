import re
from urllib.parse import urlparse


class PhishingDetector:
    """Detect phishing and fraud attempts in SMS"""
    
    def __init__(self):
        # Suspicious keywords in multiple languages
        self.suspicious_keywords = {
            'en': [
                'win', 'winner', 'won', 'prize', 'reward', 'claim',
                'urgent', 'immediately', 'act now', 'limited time',
                'click here', 'click link', 'verify', 'confirm',
                'suspended', 'locked', 'blocked', 'expire',
                'kyc', 'update kyc', 'pan card', 'aadhar',
                'bank account', 'credit card', 'debit card',
                'password', 'pin', 'otp', 'cvv',
                'refund', 'cashback', 'lottery', 'jackpot',
                'congratulations', 'selected', 'lucky',
                'free', 'gift', 'bonus', 'offer expires'
            ],
            'hi': [
                'jeet', 'inaam', 'muft', 'gift', 'offer',
                'turant', 'abhi', 'click kare', 'link',
                'kyc', 'update', 'band', 'expire'
            ]
        }
        
        # Suspicious URL patterns
        self.suspicious_domains = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly',
            't.co', 'is.gd', 'buff.ly', 'adf.ly'
        ]
        
        # Phishing patterns
        self.phishing_patterns = [
            r'click\s+(here|link|now)',
            r'verify\s+(your|account|identity)',
            r'update\s+(kyc|pan|aadhar|details)',
            r'account\s+(suspended|locked|blocked)',
            r'expire[sd]?\s+(today|soon|in)',
            r'claim\s+(your|prize|reward)',
            r'won\s+(\d+|prize|lottery)',
            r'urgent(ly)?\s+(required|needed|action)',
            r'confirm\s+(your|identity|account)',
            r'reset\s+(password|pin)'
        ]
    
    def extract_urls(self, text):
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        # Also check for domain-like patterns without http
        domain_pattern = r'\b(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b'
        domains = re.findall(domain_pattern, text)
        
        return urls + domains
    
    def is_suspicious_url(self, url):
        """Check if URL is suspicious"""
        try:
            # Check for URL shorteners
            parsed = urlparse(url if url.startswith('http') else f'http://{url}')
            domain = parsed.netloc or parsed.path.split('/')[0]
            
            if any(susp_domain in domain for susp_domain in self.suspicious_domains):
                return True
            
            # Check for IP addresses
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
                return True
            
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz']
            if any(domain.endswith(tld) for tld in suspicious_tlds):
                return True
            
            return False
        except:
            return False
    
    def detect_suspicious_keywords(self, text, language='en'):
        """Detect suspicious keywords in text"""
        text_lower = text.lower()
        found_keywords = []
        
        # Check English keywords
        for keyword in self.suspicious_keywords['en']:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        # Check language-specific keywords
        if language in self.suspicious_keywords:
            for keyword in self.suspicious_keywords[language]:
                if keyword in text_lower:
                    found_keywords.append(keyword)
        
        return found_keywords
    
    def detect_phishing_patterns(self, text):
        """Detect phishing patterns in text"""
        text_lower = text.lower()
        matched_patterns = []
        
        for pattern in self.phishing_patterns:
            if re.search(pattern, text_lower):
                matched_patterns.append(pattern)
        
        return matched_patterns
    
    def calculate_phishing_score(self, text, language='en'):
        """Calculate phishing risk score (0-1)"""
        score = 0.0
        
        # Suspicious keywords (max 0.4)
        keywords = self.detect_suspicious_keywords(text, language)
        keyword_score = min(len(keywords) * 0.08, 0.4)
        score += keyword_score
        
        # Phishing patterns (max 0.3)
        patterns = self.detect_phishing_patterns(text)
        pattern_score = min(len(patterns) * 0.1, 0.3)
        score += pattern_score
        
        # URLs (max 0.3)
        urls = self.extract_urls(text)
        if urls:
            suspicious_urls = [url for url in urls if self.is_suspicious_url(url)]
            url_score = min(len(suspicious_urls) * 0.15 + len(urls) * 0.05, 0.3)
            score += url_score
        
        return min(score, 1.0)
    
    def detect(self, text, language='en'):
        """Main detection method"""
        # Extract information
        keywords = self.detect_suspicious_keywords(text, language)
        urls = self.extract_urls(text)
        suspicious_urls = [url for url in urls if self.is_suspicious_url(url)]
        patterns = self.detect_phishing_patterns(text)
        
        # Calculate score
        phishing_score = self.calculate_phishing_score(text, language)
        
        # Determine if phishing (threshold: 0.5)
        is_phishing = phishing_score >= 0.5
        
        return {
            'is_phishing': is_phishing,
            'score': round(phishing_score, 4),
            'keywords': keywords[:10],  # Limit to top 10
            'urls': suspicious_urls,
            'risk_level': self._get_risk_level(phishing_score)
        }
    
    def _get_risk_level(self, score):
        """Get risk level based on score"""
        if score >= 0.7:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        elif score >= 0.3:
            return 'low'
        else:
            return 'safe'
