package com.textguard.sms;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class SmsLogItem {
    public String sender;
    public String message;
    public String category;
    public double confidence;
    public boolean isPhishing;
    public String riskLevel;
    public int riskScore;
    public String suspiciousKeywords;
    public String timestamp;

    public SmsLogItem(String sender, String message, String category,
                      double confidence, boolean isPhishing,
                      String riskLevel, int riskScore, String suspiciousKeywords) {
        this.sender = sender;
        this.message = message;
        this.category = category;
        this.confidence = confidence;
        this.isPhishing = isPhishing;
        this.riskLevel = riskLevel;
        this.riskScore = riskScore;
        this.suspiciousKeywords = suspiciousKeywords;
        this.timestamp = new SimpleDateFormat("hh:mm:ss a", Locale.getDefault()).format(new Date());
    }

    public boolean isHighRisk() {
        return isPhishing || "spam".equals(category) || "high".equals(riskLevel);
    }

    public boolean isMediumRisk() {
        return "medium".equals(riskLevel) || "promotion".equals(category);
    }

    public String getPreview() {
        return message.length() > 100 ? message.substring(0, 100) + "..." : message;
    }
}
