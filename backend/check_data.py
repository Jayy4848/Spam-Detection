#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_security.settings')
django.setup()

from api.models import SMSLog
from django.db.models import Count

print("=" * 50)
print("DATABASE STATISTICS")
print("=" * 50)

total = SMSLog.objects.count()
print(f"\nTotal Messages Analyzed: {total}")

if total > 0:
    print("\nCategory Breakdown:")
    cats = SMSLog.objects.values('category').annotate(count=Count('id')).order_by('-count')
    for c in cats:
        percentage = (c['count'] / total * 100) if total > 0 else 0
        print(f"  {c['category'].capitalize()}: {c['count']} ({percentage:.1f}%)")
    
    print("\nPhishing Detection:")
    phishing = SMSLog.objects.filter(is_phishing=True).count()
    print(f"  Phishing Attempts: {phishing}")
    
    print("\nRisk Levels:")
    risks = SMSLog.objects.values('risk_level').annotate(count=Count('id'))
    for r in risks:
        print(f"  {r['risk_level'].capitalize()}: {r['count']}")
    
    print("\nRecent Messages:")
    recent = SMSLog.objects.order_by('-timestamp')[:5]
    for msg in recent:
        print(f"  - {msg.category} (confidence: {msg.confidence:.1%}, risk: {msg.risk_level})")
else:
    print("\n⚠️  No data in database yet!")
    print("The dashboard is showing sample/demo data.")

print("\n" + "=" * 50)
