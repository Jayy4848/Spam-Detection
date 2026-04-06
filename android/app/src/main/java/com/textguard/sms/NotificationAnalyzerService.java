package com.textguard.sms;

import android.app.Notification;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.util.Log;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * NotificationAnalyzerService
 *
 * Listens to ALL incoming notifications on the device.
 * Filters for SMS/messaging/banking apps and sends content to TextGuard API.
 *
 * Requires user to grant "Notification Access" in Android Settings.
 */
public class NotificationAnalyzerService extends NotificationListenerService {

    private static final String TAG = "TextGuard:NotifListener";

    // Apps whose notifications we care about
    private static final Set<String> TARGET_PACKAGES = new HashSet<>(Arrays.asList(
        // SMS apps
        "com.google.android.apps.messaging",
        "com.samsung.android.messaging",
        "com.android.mms",
        "com.miui.sms",
        // WhatsApp
        "com.whatsapp",
        "com.whatsapp.w4b",
        // Banking apps
        "com.sbi.lotusintouch",
        "com.csam.icici.bank.imobile",
        "com.hdfc.mobilebanking",
        "com.axis.mobile",
        "net.one97.paytm",
        "com.phonepe.app",
        "in.amazon.mShop.android.shopping",
        // Generic — catch all messaging
        "com.google.android.gm"
    ));

    // Packages to always ignore
    private static final Set<String> IGNORE_PACKAGES = new HashSet<>(Arrays.asList(
        "com.textguard.sms",           // ourselves
        "android",
        "com.android.systemui",
        "com.android.settings",
        "com.google.android.gms"
    ));

    // Minimum text length to bother analyzing
    private static final int MIN_TEXT_LENGTH = 10;

    private ExecutorService executor;
    private ApiClient apiClient;

    @Override
    public void onCreate() {
        super.onCreate();
        executor  = Executors.newFixedThreadPool(2);
        apiClient = new ApiClient(this);
        Log.i(TAG, "NotificationAnalyzerService started");
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        if (sbn == null) return;

        String packageName = sbn.getPackageName();

        // Skip ignored packages
        if (IGNORE_PACKAGES.contains(packageName)) return;

        // Check if monitoring is enabled
        SharedPreferences prefs = getSharedPreferences("textguard_prefs", MODE_PRIVATE);
        if (!prefs.getBoolean("monitor_enabled", true)) return;

        // Check if notification analysis is enabled
        if (!prefs.getBoolean("notif_analysis_enabled", true)) return;

        // Only analyze target packages OR if "analyze all" is enabled
        boolean analyzeAll = prefs.getBoolean("analyze_all_notifs", false);
        if (!analyzeAll && !TARGET_PACKAGES.contains(packageName)) return;

        Notification notification = sbn.getNotification();
        if (notification == null) return;

        // Extract text from notification
        String title = "";
        String text  = "";

        Bundle extras = notification.extras;
        if (extras != null) {
            CharSequence titleSeq = extras.getCharSequence(Notification.EXTRA_TITLE);
            CharSequence textSeq  = extras.getCharSequence(Notification.EXTRA_TEXT);
            CharSequence bigText  = extras.getCharSequence(Notification.EXTRA_BIG_TEXT);

            title = titleSeq != null ? titleSeq.toString() : "";
            text  = bigText  != null ? bigText.toString()  :
                    textSeq  != null ? textSeq.toString()  : "";
        }

        // Skip if no meaningful content
        String combined = (title + " " + text).trim();
        if (combined.length() < MIN_TEXT_LENGTH) return;

        // Skip if it's our own analysis notification
        if (title.contains("TextGuard") || title.contains("Risk SMS")) return;

        final String finalTitle   = title;
        final String finalText    = text;
        final String finalPkg     = packageName;
        final String finalCombined = combined;

        Log.d(TAG, "Notification from: " + packageName + " | " + title);

        // Analyze in background
        executor.execute(() -> {
            ApiClient.AnalysisResult result = apiClient.analyzeSms(finalCombined, "en");

            if (result != null) {
                Log.d(TAG, "Result: " + result.category + " risk=" + result.getRiskScorePercent() + "%");

                // Broadcast to MainActivity
                Intent broadcast = new Intent(SmsAnalysisService.ACTION_RESULT);
                broadcast.putExtra("sender",   getAppName(finalPkg));
                broadcast.putExtra("message",  finalCombined);
                broadcast.putExtra("category", result.category);
                broadcast.putExtra("confidence",  result.confidence);
                broadcast.putExtra("is_phishing", result.isPhishing);
                broadcast.putExtra("risk_level",  result.riskLevel);
                broadcast.putExtra("risk_score",  result.getRiskScorePercent());
                broadcast.putExtra("explanation", result.explanation);
                broadcast.putExtra("suspicious_keywords", result.suspiciousKeywords);
                broadcast.putExtra("source", "notification");
                sendBroadcast(broadcast);

                // Show alert notification only for high/medium risk
                if (result.isHighRisk() || result.isMediumRisk()) {
                    Intent serviceIntent = new Intent(this, SmsAnalysisService.class);
                    serviceIntent.putExtra("message", finalCombined);
                    serviceIntent.putExtra("sender",  getAppName(finalPkg));
                    startService(serviceIntent);
                }
            }
        });
    }

    @Override
    public void onNotificationRemoved(StatusBarNotification sbn) {
        // Not needed
    }

    private String getAppName(String packageName) {
        // Map package names to readable names
        switch (packageName) {
            case "com.whatsapp":                        return "WhatsApp";
            case "com.whatsapp.w4b":                   return "WhatsApp Business";
            case "com.google.android.apps.messaging":  return "Messages";
            case "com.samsung.android.messaging":      return "Samsung Messages";
            case "com.sbi.lotusintouch":               return "SBI YONO";
            case "com.csam.icici.bank.imobile":        return "ICICI iMobile";
            case "com.hdfc.mobilebanking":             return "HDFC Bank";
            case "net.one97.paytm":                    return "Paytm";
            case "com.phonepe.app":                    return "PhonePe";
            default:
                // Return last part of package name
                String[] parts = packageName.split("\\.");
                return parts.length > 0 ? parts[parts.length - 1] : packageName;
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (executor != null) executor.shutdown();
        Log.i(TAG, "NotificationAnalyzerService stopped");
    }
}
