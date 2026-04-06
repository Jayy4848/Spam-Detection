package com.textguard.sms;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.telephony.SmsMessage;
import android.util.Log;

/**
 * SmsReceiver
 * Intercepts every incoming SMS at the OS level.
 * Triggered automatically by Android when an SMS arrives —
 * no user action needed.
 */
public class SmsReceiver extends BroadcastReceiver {

    private static final String TAG = "TextGuard:SmsReceiver";
    private static final String SMS_RECEIVED = "android.provider.Telephony.SMS_RECEIVED";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (!SMS_RECEIVED.equals(intent.getAction())) return;

        Bundle bundle = intent.getExtras();
        if (bundle == null) return;

        try {
            Object[] pdus = (Object[]) bundle.get("pdus");
            String format = bundle.getString("format");

            if (pdus == null || pdus.length == 0) return;

            // Reconstruct full message from PDU parts (handles multi-part SMS)
            StringBuilder fullMessage = new StringBuilder();
            String sender = null;

            for (Object pdu : pdus) {
                SmsMessage sms = SmsMessage.createFromPdu((byte[]) pdu, format);
                if (sms != null) {
                    fullMessage.append(sms.getMessageBody());
                    if (sender == null) {
                        sender = sms.getDisplayOriginatingAddress();
                    }
                }
            }

            String messageText = fullMessage.toString().trim();
            if (messageText.isEmpty()) return;

            Log.d(TAG, "SMS received from: " + sender);
            Log.d(TAG, "Message: " + messageText.substring(0, Math.min(50, messageText.length())) + "...");

            // Fire background service to analyze this SMS
            Intent serviceIntent = new Intent(context, SmsAnalysisService.class);
            serviceIntent.putExtra("message", messageText);
            serviceIntent.putExtra("sender", sender != null ? sender : "Unknown");
            context.startService(serviceIntent);

        } catch (Exception e) {
            Log.e(TAG, "Error processing SMS: " + e.getMessage());
        }
    }
}
