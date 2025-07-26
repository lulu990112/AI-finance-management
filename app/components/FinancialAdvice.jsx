import React from "react";

export default function FinancialAdvice() {
  return (
    <div style={{
      background: "#fff",
      borderRadius: 10,
      padding: "18px 24px",
      marginBottom: 16,
      boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
      fontSize: 15,
      border: "1px solid #eee"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 600, fontSize: 16, marginBottom: 6 }}>
        <span role="img" aria-label="advice">🌐</span> Financial Advice for This Week
      </div>
      <div style={{ color: "#444" }}>
        We noticed your dining out expenses are up 15% from last week. Try cooking at home 1~2 more times a week to save money. Most of your shopping is on electronics—keep an eye out for deals.
      </div>
      <a href="/ai-report" style={{
        display: "inline-block",
        marginTop: 12,
        background: "#4ecbff",
        color: "#fff",
        borderRadius: 6,
        padding: "6px 18px",
        fontWeight: 600,
        fontSize: 15,
        textDecoration: "none",
        boxShadow: "0 1px 4px #e0e0e0",
        transition: "background 0.2s"
      }}>View Details</a>
    </div>
  );
} 