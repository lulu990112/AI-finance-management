import React from "react";
import Link from "next/link";

const transactions = [
  {
    title: "Uber Eats Dinner (Food & Dining)",
    desc: "Daily Meals",
    date: "2024-07-14",
    amount: "-$15.75"
  },
  {
    title: "Amazon Order (Shopping)",
    desc: "Cosmetics, Skincare Products ect.",
    date: "2024-07-14",
    amount: "-$89.99"
  },
  {
    title: "Train Ticket (Transport)",
    desc: "Transport",
    date: "2024-07-13",
    amount: "-$5.50"
  },
  {
    title: "Boots Order (Shopping)",
    desc: "Skincare Products",
    date: "2024-07-13",
    amount: "-$25.00"
  }
];

export default function RecentTransactions() {
  return (
    <div>
      <div style={{ fontWeight: 700, fontSize: 26, marginBottom: 18 }}>Recent Transactions</div>
      <div>
        {transactions.map((t, i) => (
          <div key={i} style={{ marginBottom: 18 }}>
            <div style={{ fontWeight: 600, fontSize: 16 }}>{t.title}</div>
            <div style={{ color: "#888", fontSize: 15 }}>{t.desc}</div>
            <div style={{ color: "#888", fontSize: 14 }}>– {t.date} – {t.amount}</div>
          </div>
        ))}
      </div>
      <Link href="/category-list" style={{
        display: "inline-block",
        background: "#eee",
        border: "none",
        borderRadius: 6,
        padding: "8px 18px",
        fontWeight: 600,
        fontSize: 15,
        marginTop: 8,
        cursor: "pointer",
        textDecoration: "none",
        color: "#222"
      }}>View Details</Link>
    </div>
  );
} 