package com.textguard.sms;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;

import androidx.core.app.NotificationCompat;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * SmsAnalysisService
 * Background service that:
 * 1. Receives SMS text from SmsReceiver
 * 2. Calls the TextGuard API
 * 3. Shows a push notification with the result
 * 4. Broadcasts result to MainActivity if open
 */
public class SmsAnalysisService extends Service {

    private static final String TAG = "TextGuard:Service";
    public static final String CHANNEL_THREAT  = "textguard_threat";
    public static final String CHANNEL_SAFE    = "textguard_safe";
    public static final String ACTION_RESULT   = "com.textguard.sms.RESULT";

    private ExecutorService executor;
    private ApiClient apiClient;

    @Override
    public void onCreate() {
        super.onCreate();
        executor  = Executors.newSingleThreadExecutor();
        apiClient = new ApiClient(this);
        createNotificationChannels();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) return START_NOT_STICKY;

        String message = intent.getStringExtra("message");
        String sender  = intent.getStringExtra("sender");

        if (message == null || message.isEmpty()) return START_NOT_STICKY;

        // Run API call on background thread
        executor.execute(() -> {
            Log.d(TAG, "Analyzing SMS from: " + sender);

            ApiClient.AnalysisResult result = apiClient.analyzeSms(message, "en");

            if (result != null) {
                showResultNotification(sender, message, result);
                broadcastResult(sender, message, result);
                Log.d(TAG, "Analysis done: " + result.category + " (" + result.getRiskScorePercent() + "% risk)");
            } else {
                showErrorNotification(sender);
                Log.e(TAG, "Analysis failed for message from: " + sender);
            }

            stopSelf(startId);
        });

        return START_NOT_STICKY;
    }

    private void showResultNotification(String sender, String message, ApiClient.AnalysisResult result) {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

        String channel;
        String title;
        String icon;
        int priority;

        if (result.isHighRisk()) {
            channel  = CHANNEL_THREAT;
            title    = "🚨 High Risk SMS Detected!";
            icon     = "⚠️";
            priority = NotificationCompat.PRIORITY_HIGH;
        } else if (result.isMediumRisk()) {
            channel  = CHANNEL_SAFE;
            title    = "⚠️ Suspicious SMS";
            icon     = "⚠️";
            priority = NotificationCompat.PRIORITY_DEFAULT;
        } else {
            channel  = CHANNEL_SAFE;
            title    = "✅ SMS Analyzed — Safe";
            icon     = "✅";
            priority = NotificationCompat.PRIORITY_LOW;
        }

        // Truncate message for notification
        String preview = message.length() > 80 ? message.substring(0, 80) + "..." : message;

        String body = String.format(
            "From: %s\nCategory: %s | Risk: %d%%\n%s",
            sender,
            result.category.toUpperCase(),
            result.getRiskScorePercent(),
            preview
        );

        // Tap notification → open MainActivity
        Intent openApp = new Intent(this, MainActivity.class);
        openApp.putExtra("from_notification", true);
        openApp.putExtra("sender", sender);
        openApp.putExtra("message", message);
        openApp.putExtra("category", result.category);
        openApp.putExtra("risk_score", result.getRiskScorePercent());
        openApp.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);

        PendingIntent pendingIntent = PendingIntent.getActivity(
            this, (int) System.currentTimeMillis(), openApp,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, channel)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(title)
            .setContentText("From: " + sender + " — " + result.category.toUpperCase())
            .setStyle(new NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(priority)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true);

        if (result.isHighRisk()) {
            builder.setVibrate(new long[]{0, 500, 200, 500});
        }

        nm.notify((int) System.currentTimeMillis(), builder.build());
    }

    private void showErrorNotification(String sender) {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_SAFE)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("TextGuard — Analysis Failed")
            .setContentText("Could not analyze SMS from " + sender + ". Check server connection.")
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setAutoCancel(true);

        nm.notify((int) System.currentTimeMillis(), builder.build());
    }

    /** Broadcast result to MainActivity if it's currently open */
    private void broadcastResult(String sender, String message, ApiClient.AnalysisResult result) {
        Intent broadcast = new Intent(ACTION_RESULT);
        broadcast.putExtra("sender", sender);
        broadcast.putExtra("message", message);
        broadcast.putExtra("category", result.category);
        broadcast.putExtra("confidence", result.confidence);
        broadcast.putExtra("is_phishing", result.isPhishing);
        broadcast.putExtra("risk_level", result.riskLevel);
        broadcast.putExtra("risk_score", result.getRiskScorePercent());
        broadcast.putExtra("explanation", result.explanation);
        broadcast.putExtra("suspicious_keywords", result.suspiciousKeywords);
        sendBroadcast(broadcast);
    }

    private void createNotificationChannels() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;

        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

        // High priority channel for threats
        NotificationChannel threatChannel = new NotificationChannel(
            CHANNEL_THREAT,
            "Threat Alerts",
            NotificationManager.IMPORTANCE_HIGH
        );
        threatChannel.setDescription("Alerts for spam, phishing, and high-risk SMS");
        threatChannel.enableVibration(true);
        nm.createNotificationChannel(threatChannel);

        // Normal channel for safe messages
        NotificationChannel safeChannel = new NotificationChannel(
            CHANNEL_SAFE,
            "SMS Analysis",
            NotificationManager.IMPORTANCE_DEFAULT
        );
        safeChannel.setDescription("Results for analyzed safe messages");
        nm.createNotificationChannel(safeChannel);
    }

    @Override
    public IBinder onBind(Intent intent) { return null; }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (executor != null) executor.shutdown();
    }
}
