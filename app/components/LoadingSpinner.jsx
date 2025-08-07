import React from "react";

export default function LoadingSpinner({ size = "medium", text = "加载中..." }) {
  const spinnerSize = {
    small: 16,
    medium: 24,
    large: 32
  }[size] || 24;

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "20px"
    }}>
      <div style={{
        width: spinnerSize,
        height: spinnerSize,
        border: "2px solid #f3f3f3",
        borderTop: "2px solid #3498db",
        borderRadius: "50%",
        animation: "spin 1s linear infinite",
        marginBottom: "8px"
      }}></div>
      <div style={{ color: "#666", fontSize: "14px" }}>{text}</div>
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
} 