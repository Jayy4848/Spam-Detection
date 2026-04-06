package com.textguard.sms;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

/**
 * BootReceiver
 * Ensures SMS monitoring resumes automatically after device reboot.
 */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (!Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) return;

        SharedPreferences prefs = context.getSharedPreferences("textguard_prefs", Context.MODE_PRIVATE);
        boolean enabled = prefs.getBoolean("monitor_enabled", true);

        // SmsReceiver is always registered via manifest — no action needed here
        // This is just a hook for future foreground service startup if needed
    }
}
