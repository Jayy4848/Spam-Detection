package com.textguard.sms;

import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

public class SmsLogAdapter extends RecyclerView.Adapter<SmsLogAdapter.ViewHolder> {

    private final List<SmsLogItem> items;

    public SmsLogAdapter(List<SmsLogItem> items) {
        this.items = items;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
            .inflate(R.layout.item_sms_log, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        SmsLogItem item = items.get(position);

        holder.sender.setText(item.sender);
        holder.timestamp.setText(item.timestamp);
        holder.preview.setText(item.getPreview());
        holder.category.setText(item.category.toUpperCase());
        holder.riskScore.setText(item.riskScore + "%");
        holder.confidence.setText(String.format("%.0f%% confident", item.confidence * 100));

        // Color code by risk
        if (item.isHighRisk()) {
            holder.riskBadge.setText("HIGH RISK");
            holder.riskBadge.setBackgroundColor(Color.parseColor("#FFEBEE"));
            holder.riskBadge.setTextColor(Color.parseColor("#C62828"));
            holder.riskScore.setTextColor(Color.parseColor("#C62828"));
            holder.cardBorder.setBackgroundColor(Color.parseColor("#EF4444"));
        } else if (item.isMediumRisk()) {
            holder.riskBadge.setText("MEDIUM RISK");
            holder.riskBadge.setBackgroundColor(Color.parseColor("#FFFDE7"));
            holder.riskBadge.setTextColor(Color.parseColor("#F57F17"));
            holder.riskScore.setTextColor(Color.parseColor("#F59E0B"));
            holder.cardBorder.setBackgroundColor(Color.parseColor("#F59E0B"));
        } else {
            holder.riskBadge.setText("SAFE");
            holder.riskBadge.setBackgroundColor(Color.parseColor("#E8F5E9"));
            holder.riskBadge.setTextColor(Color.parseColor("#2E7D32"));
            holder.riskScore.setTextColor(Color.parseColor("#10B981"));
            holder.cardBorder.setBackgroundColor(Color.parseColor("#10B981"));
        }

        // Show phishing warning
        if (item.isPhishing) {
            holder.phishingWarning.setVisibility(View.VISIBLE);
        } else {
            holder.phishingWarning.setVisibility(View.GONE);
        }

        // Show keywords if present
        if (item.suspiciousKeywords != null && !item.suspiciousKeywords.isEmpty()) {
            holder.keywords.setVisibility(View.VISIBLE);
            holder.keywords.setText("⚠️ " + item.suspiciousKeywords);
        } else {
            holder.keywords.setVisibility(View.GONE);
        }
    }

    @Override
    public int getItemCount() { return items.size(); }

    static class ViewHolder extends RecyclerView.ViewHolder {
        View cardBorder;
        TextView sender, timestamp, preview, category, riskBadge, riskScore, confidence, phishingWarning, keywords;

        ViewHolder(View view) {
            super(view);
            cardBorder      = view.findViewById(R.id.cardBorder);
            sender          = view.findViewById(R.id.tvSender);
            timestamp       = view.findViewById(R.id.tvTimestamp);
            preview         = view.findViewById(R.id.tvPreview);
            category        = view.findViewById(R.id.tvCategory);
            riskBadge       = view.findViewById(R.id.tvRiskBadge);
            riskScore       = view.findViewById(R.id.tvRiskScore);
            confidence      = view.findViewById(R.id.tvConfidence);
            phishingWarning = view.findViewById(R.id.tvPhishingWarning);
            keywords        = view.findViewById(R.id.tvKeywords);
        }
    }
}
