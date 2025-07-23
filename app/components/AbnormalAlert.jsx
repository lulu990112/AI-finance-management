import React from "react";

export default function AbnormalAlert() {
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
        <span role="img" aria-label="alert">🔒</span> Abnormal Spending Alert
      </div>
      <div style={{ color: "#444" }}>
        A $200 overseas transaction has been detected, which is inconsistent with your usual spending habits. Please confirm if this was made by you.
      </div>
      <a href="/ai-report" style={{
        display: "inline-block",
        marginTop: 12,
        background: "#faad14",
        color: "#fff",
        borderRadius: 6,
        padding: "6px 18px",
        fontWeight: 600,
        fontSize: 15,
        textDecoration: "none",
        boxShadow: "0 1px 4px #ffe08f",
        transition: "background 0.2s"
      }}>查看详情</a>
    </div>
  );
} 