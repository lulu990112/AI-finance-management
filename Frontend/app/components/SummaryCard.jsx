import React from "react";
import { useRouter } from "next/navigation";

export default function SummaryCard({ title, icon, value }) {
  const router = useRouter();
  const isExpense = title === 'Total Expenses';
  return (
    <div
      style={{
        background: "#fff",
        borderRadius: 12,
        boxShadow: "0 2px 12px rgba(0,0,0,0.04)",
        padding: "24px 28px",
        minWidth: 220,
        display: "flex",
        flexDirection: "column",
        gap: 10,
        border: "1px solid #eee",
        cursor: isExpense ? 'pointer' : 'default',
        transition: 'box-shadow 0.2s',
        ...(isExpense ? { boxShadow: '0 4px 16px #ffe0e0' } : {})
      }}
      onClick={isExpense ? () => router.push('/trend-dashboard') : undefined}
      title={isExpense ? 'Click to view expense trend' : undefined}
    >
      <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 8 }}>{title}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ fontSize: 22 }}>{icon}</span>
        <span style={{ fontWeight: 700, fontSize: 22, color: title === 'Total Expenses' ? '#ff4d4f' : '#222' }}>{value}</span>
      </div>
    </div>
  );
} 