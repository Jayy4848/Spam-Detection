package com.textguard.sms;

import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.text.TextUtils;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.switchmaterial.SwitchMaterial;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    private static final int PERMISSION_REQUEST_CODE = 100;

    private SwitchMaterial monitorSwitch;
    private SwitchMaterial notifSwitch;
    private TextView statusText;
    private TextView notifStatusText;
    private TextView totalCount;
    private TextView threatCount;
    private TextView safeCount;
    private RecyclerView messageList;
    private View emptyState;

    private SmsLogAdapter adapter;
    private final List<SmsLogItem> logItems = new ArrayList<>();
    private BroadcastReceiver resultReceiver;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();
        setupRecyclerView();
        setupSwitches();
        setupResultReceiver();
        requestPermissions();
        checkNotificationAccess();

        if (getIntent().getBooleanExtra("from_notification", false)) {
            handleNotificationIntent(getIntent());
        }
    }

    private void initViews() {
        monitorSwitch    = findViewById(R.id.monitorSwitch);
        notifSwitch      = findViewById(R.id.notifSwitch);
        statusText       = findViewById(R.id.statusText);
        notifStatusText  = findViewById(R.id.notifStatusText);
        totalCount       = findViewById(R.id.totalCount);
        threatCount      = findViewById(R.id.threatCount);
        safeCount        = findViewById(R.id.safeCount);
        messageList      = findViewById(R.id.messageList);
        emptyState       = findViewById(R.id.emptyState);

        findViewById(R.id.btnSettings).setOnClickListener(v -> showSettingsDialog());
        findViewById(R.id.btnClear).setOnClickListener(v -> {
            logItems.clear();
            adapter.notifyDataSetChanged();
            updateStats();
            emptyState.setVisibility(View.VISIBLE);
            messageList.setVisibility(View.GONE);
        });

        SharedPreferences prefs = getSharedPreferences("textguard_prefs", MODE_PRIVATE);
        monitorSwitch.setChecked(prefs.getBoolean("monitor_enabled", true));
        notifSwitch.setChecked(prefs.getBoolean("notif_analysis_enabled", true));
        updateSmsStatusUI(monitorSwitch.isChecked());
        updateNotifStatusUI(notifSwitch.isChecked());
    }

    private void setupRecyclerView() {
        adapter = new SmsLogAdapter(logItems);
        messageList.setLayoutManager(new LinearLayoutManager(this));
        messageList.setAdapter(adapter);
    }

    private void setupSwitches() {
        monitorSwitch.setOnCheckedChangeListener((btn, isChecked) -> {
            getSharedPreferences("textguard_prefs", MODE_PRIVATE)
                .edit().putBoolean("monitor_enabled", isChecked).apply();
            updateSmsStatusUI(isChecked);
            Toast.makeText(this,
                isChecked ? "✅ SMS monitoring enabled" : "⏸ SMS monitoring paused",
                Toast.LENGTH_SHORT).show();
        });

        notifSwitch.setOnCheckedChangeListener((btn, isChecked) -> {
            if (isChecked && !isNotificationAccessGranted()) {
                // Redirect to system settings to grant access
                notifSwitch.setChecked(false);
                showNotificationAccessDialog();
                return;
            }
            getSharedPreferences("textguard_prefs", MODE_PRIVATE)
                .edit().putBoolean("notif_analysis_enabled", isChecked).apply();
            updateNotifStatusUI(isChecked);
            Toast.makeText(this,
                isChecked ? "✅ Notification monitoring enabled" : "⏸ Notification monitoring paused",
                Toast.LENGTH_SHORT).show();
        });
    }

    private void setupResultReceiver() {
        resultReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                String sender    = intent.getStringExtra("sender");
                String message   = intent.getStringExtra("message");
                String category  = intent.getStringExtra("category");
                double confidence = intent.getDoubleExtra("confidence", 0);
                boolean isPhishing = intent.getBooleanExtra("is_phishing", false);
                String riskLevel = intent.getStringExtra("risk_level");
                int riskScore    = intent.getIntExtra("risk_score", 0);
                String keywords  = intent.getStringExtra("suspicious_keywords");
                String source    = intent.getStringExtra("source"); // "sms" or "notification"

                SmsLogItem item = new SmsLogItem(
                    (source != null && source.equals("notification") ? "📳 " : "💬 ") + sender,
                    message, category, confidence, isPhishing, riskLevel, riskScore, keywords
                );

                runOnUiThread(() -> {
                    logItems.add(0, item);
                    adapter.notifyItemInserted(0);
                    messageList.scrollToPosition(0);
                    updateStats();
                    emptyState.setVisibility(View.GONE);
                    messageList.setVisibility(View.VISIBLE);
                });
            }
        };
    }

    private void updateSmsStatusUI(boolean enabled) {
        statusText.setText(enabled
            ? "🟢 SMS monitoring active — incoming SMS auto-analyzed"
            : "⏸ SMS monitoring paused");
        statusText.setBackgroundResource(enabled ? R.drawable.bg_status_active : R.drawable.bg_status_inactive);
        statusText.setTextColor(getColor(enabled ? android.R.color.holo_green_dark : android.R.color.darker_gray));
    }

    private void updateNotifStatusUI(boolean enabled) {
        boolean hasAccess = isNotificationAccessGranted();
        if (!hasAccess) {
            notifStatusText.setText("⚠️ Notification access not granted — tap to enable");
            notifStatusText.setBackgroundResource(R.drawable.bg_status_inactive);
            notifStatusText.setTextColor(getColor(android.R.color.holo_orange_dark));
            notifStatusText.setOnClickListener(v -> showNotificationAccessDialog());
        } else {
            notifStatusText.setText(enabled
                ? "🟢 Notification monitoring active — WhatsApp, banking apps, SMS apps analyzed"
                : "⏸ Notification monitoring paused");
            notifStatusText.setBackgroundResource(enabled ? R.drawable.bg_status_active : R.drawable.bg_status_inactive);
            notifStatusText.setTextColor(getColor(enabled ? android.R.color.holo_green_dark : android.R.color.darker_gray));
            notifStatusText.setOnClickListener(null);
        }
    }

    private void updateStats() {
        int total = logItems.size();
        int threats = 0, safe = 0;
        for (SmsLogItem item : logItems) {
            if (item.isHighRisk()) threats++;
            else safe++;
        }
        totalCount.setText(String.valueOf(total));
        threatCount.setText(String.valueOf(threats));
        safeCount.setText(String.valueOf(safe));
    }

    /** Check if NotificationListenerService has been granted access */
    private boolean isNotificationAccessGranted() {
        String flat = Settings.Secure.getString(getContentResolver(), "enabled_notification_listeners");
        if (flat == null || flat.isEmpty()) return false;
        ComponentName cn = new ComponentName(this, NotificationAnalyzerService.class);
        return flat.contains(cn.flattenToString());
    }

    private void checkNotificationAccess() {
        updateNotifStatusUI(
            getSharedPreferences("textguard_prefs", MODE_PRIVATE)
                .getBoolean("notif_analysis_enabled", true)
        );
    }

    private void showNotificationAccessDialog() {
        new AlertDialog.Builder(this)
            .setTitle("🔔 Notification Access Required")
            .setMessage(
                "To analyze notifications from WhatsApp, banking apps, and other apps, " +
                "TextGuard needs Notification Access.\n\n" +
                "Steps:\n" +
                "1. Tap 'Open Settings' below\n" +
                "2. Find 'TextGuard AI' in the list\n" +
                "3. Toggle it ON\n" +
                "4. Come back to the app"
            )
            .setPositiveButton("Open Settings", (d, w) -> {
                startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
            })
            .setNegativeButton("Not Now", null)
            .show();
    }

    private void showSettingsDialog() {
        SharedPreferences prefs = getSharedPreferences("textguard_prefs", MODE_PRIVATE);
        String currentUrl = prefs.getString("api_url", "http://192.168.1.5:8000/api");

        android.widget.EditText input = new android.widget.EditText(this);
        input.setText(currentUrl);
        input.setSelectAllOnFocus(true);

        new AlertDialog.Builder(this)
            .setTitle("⚙️ Server Settings")
            .setMessage("TextGuard backend API URL:\n\nSame WiFi: http://YOUR-PC-IP:8000/api\nCloud: https://your-backend.onrender.com/api")
            .setView(input)
            .setPositiveButton("Save", (dialog, which) -> {
                String newUrl = input.getText().toString().trim();
                if (!newUrl.isEmpty()) {
                    prefs.edit().putString("api_url", newUrl).apply();
                    Toast.makeText(this, "✅ Server URL saved", Toast.LENGTH_SHORT).show();
                }
            })
            .setNegativeButton("Cancel", null)
            .show();
    }

    private void handleNotificationIntent(Intent intent) {
        String sender   = intent.getStringExtra("sender");
        String message  = intent.getStringExtra("message");
        String category = intent.getStringExtra("category");
        int riskScore   = intent.getIntExtra("risk_score", 0);
        if (message != null) {
            SmsLogItem item = new SmsLogItem(sender, message, category, 0.9, false, "medium", riskScore, "");
            logItems.add(0, item);
            adapter.notifyItemInserted(0);
            updateStats();
            emptyState.setVisibility(View.GONE);
            messageList.setVisibility(View.VISIBLE);
        }
    }

    private void requestPermissions() {
        List<String> needed = new ArrayList<>();
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECEIVE_SMS) != PackageManager.PERMISSION_GRANTED)
            needed.add(Manifest.permission.RECEIVE_SMS);
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS) != PackageManager.PERMISSION_GRANTED)
            needed.add(Manifest.permission.READ_SMS);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED)
            needed.add(Manifest.permission.POST_NOTIFICATIONS);
        if (!needed.isEmpty())
            ActivityCompat.requestPermissions(this, needed.toArray(new String[0]), PERMISSION_REQUEST_CODE);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    }

    @Override
    protected void onResume() {
        super.onResume();
        registerReceiver(resultReceiver, new IntentFilter(SmsAnalysisService.ACTION_RESULT));
        checkNotificationAccess(); // Refresh status in case user just granted access
    }

    @Override
    protected void onPause() {
        super.onPause();
        unregisterReceiver(resultReceiver);
    }
}
