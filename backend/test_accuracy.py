#!/usr/bin/env python3
"""Test the actual model accuracy with real messages"""

import os
import sys
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_security.settings')
sys.path.insert(0, '.')
django.setup()

from ml_models.classifier import SMSClassifier
from ml_models.phishing_detector import PhishingDetector

# Initialize
classifier = SMSClassifier()
phishing = PhishingDetector()

# Test messages with expected categories
test_cases = [
    ("WINNER!! You won $1000! Click here now!", "spam"),
    ("Your OTP is 123456. Valid for 10 minutes.", "otp"),
    ("Hi! How are you? Lets meet tomorrow.", "personal"),
    ("50% off this weekend! Shop now.", "promotion"),
    ("Your account debited Rs.5000. Balance: Rs.15000", "important"),
    ("Congratulations! Free iPhone. Call now!", "spam"),
    ("Verification code: 789012. Use to login.", "otp"),
    ("Thanks for your help yesterday!", "personal"),
    ("Flash sale! 70% discount today only!", "promotion"),
    ("Payment received Rs.2500. Thank you.", "important"),
]

print("=" * 60)
print("MODEL ACCURACY TEST - REAL MESSAGES")
print("=" * 60)
print()

correct = 0
total = len(test_cases)

for i, (msg, expected) in enumerate(test_cases, 1):
    result = classifier.predict(msg, 'en')
    phish = phishing.detect(msg, 'en')
    
    predicted = result['category']
    confidence = result['confidence']
    phish_score = phish['score']
    
    is_correct = predicted == expected
    correct += is_correct
    
    print(f"Test {i}/{total}:")
    print(f"  Message: {msg[:60]}...")
    print(f"  Expected: {expected}")
    print(f"  Predicted: {predicted}")
    print(f"  Confidence: {confidence:.2%}")
    print(f"  Phishing Score: {phish_score:.2%}")
    print(f"  Result: {'✓ CORRECT' if is_correct else '✗ WRONG'}")
    print()

accuracy = (correct / total) * 100
print("=" * 60)
print(f"REAL-WORLD TEST ACCURACY: {accuracy:.1f}% ({correct}/{total} correct)")
print("=" * 60)
