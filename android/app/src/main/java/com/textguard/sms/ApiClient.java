package com.textguard.sms;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import androidx.security.crypto.EncryptedSharedPreferences;
import androidx.security.crypto.MasterKey;

import org.json.JSONObject;

import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.concurrent.TimeUnit;

import okhttp3.CertificatePinner;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * ApiClient
 * Handles all HTTP communication with the TextGuard Django backend.
 * Configurable server URL via app settings.
 */
public class ApiClient {

    private static final String TAG = "TextGuard:ApiClient";
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");

    private final OkHttpClient client;
    private final String baseUrl;

    public ApiClient(Context context) {
        // Use EncryptedSharedPreferences to protect stored API URL
        SharedPreferences prefs;
        try {
            MasterKey masterKey = new MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build();
            prefs = EncryptedSharedPreferences.create(
                context,
                "textguard_secure_prefs",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            );
        } catch (GeneralSecurityException | IOException e) {
            Log.e(TAG, "EncryptedSharedPreferences failed, falling back: " + e.getMessage());
            prefs = context.getSharedPreferences("textguard_prefs", Context.MODE_PRIVATE);
        }

        this.baseUrl = prefs.getString("api_url", "http://192.168.0.103:8000/api");

        // Build OkHttpClient with security settings
        OkHttpClient.Builder builder = new OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .writeTimeout(10, TimeUnit.SECONDS);

        // Certificate pinning for production HTTPS deployments
        // Replace with your actual domain and certificate hash when deploying
        // Generate hash: openssl s_client -connect yourdomain.com:443 | openssl x509 -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64
        String productionDomain = "yourdomain.com"; // Replace with actual domain
        if (this.baseUrl.contains(productionDomain)) {
            CertificatePinner pinner = new CertificatePinner.Builder()
                .add(productionDomain, "sha256/REPLACE_WITH_YOUR_CERT_HASH=")
                .build();
            builder.certificatePinner(pinner);
        }

        this.client = builder.build();
    }

    /**
     * Analyze an SMS message via the backend API.
     * Returns parsed AnalysisResult or null on failure.
     */
    public AnalysisResult analyzeSms(String message, String language) {
        try {
            JSONObject body = new JSONObject();
            body.put("message", message);
            body.put("language", language != null ? language : "en");

            RequestBody requestBody = RequestBody.create(body.toString(), JSON);

            Request request = new Request.Builder()
                    .url(baseUrl + "/predict/")
                    .post(requestBody)
                    .addHeader("Content-Type", "application/json")
                    .build();

            try (Response response = client.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    Log.e(TAG, "API error: " + response.code());
                    return null;
                }

                String responseBody = response.body() != null ? response.body().string() : null;
                if (responseBody == null) return null;

                return parseResult(responseBody);
            }

        } catch (IOException e) {
            Log.e(TAG, "Network error: " + e.getMessage());
            return null;
        } catch (Exception e) {
            Log.e(TAG, "Parse error: " + e.getMessage());
            return null;
        }
    }

    private AnalysisResult parseResult(String json) throws Exception {
        JSONObject obj = new JSONObject(json);

        AnalysisResult result = new AnalysisResult();
        result.category    = obj.optString("category", "unknown");
        result.confidence  = obj.optDouble("confidence", 0.0);
        result.isPhishing  = obj.optBoolean("is_phishing", false);
        result.riskLevel   = obj.optString("risk_level", "low");
        result.riskScore   = obj.optDouble("risk_score", 0.0);
        result.explanation = obj.optString("explanation", "");
        result.messageId   = obj.optString("message_id", "");

        // Urgency
        if (obj.has("urgency_analysis")) {
            JSONObject urgency = obj.getJSONObject("urgency_analysis");
            result.urgencyLevel = urgency.optString("level", "low");
        }

        // Suspicious keywords
        if (obj.has("suspicious_keywords")) {
            StringBuilder keywords = new StringBuilder();
            for (int i = 0; i < obj.getJSONArray("suspicious_keywords").length(); i++) {
                if (i > 0) keywords.append(", ");
                keywords.append(obj.getJSONArray("suspicious_keywords").getString(i));
            }
            result.suspiciousKeywords = keywords.toString();
        }

        return result;
    }

    /** Simple data class for analysis results */
    public static class AnalysisResult {
        public String category;
        public double confidence;
        public boolean isPhishing;
        public String riskLevel;
        public double riskScore;
        public String explanation;
        public String messageId;
        public String urgencyLevel;
        public String suspiciousKeywords;

        public int getRiskScorePercent() {
            return (int) Math.round(riskScore * 100);
        }

        public boolean isHighRisk() {
            return isPhishing || "spam".equals(category) || "high".equals(riskLevel);
        }

        public boolean isMediumRisk() {
            return "medium".equals(riskLevel) || "promotion".equals(category);
        }
    }
}
