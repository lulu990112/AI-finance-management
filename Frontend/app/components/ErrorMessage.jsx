import React from "react";

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div style={{
      background: "#fff2f0",
      border: "1px solid #ffccc7",
      borderRadius: 8,
      padding: "16px",
      margin: "16px 0",
      color: "#cf1322"
    }}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>
        Error: {message}
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            background: "#ff4d4f",
            color: "#fff",
            border: "none",
            borderRadius: 4,
            padding: "8px 16px",
            cursor: "pointer",
            fontSize: 14
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
} 