import React from "react";
import Link from "next/link";
import { useData } from "../context/DataContext";
import LoadingSpinner from "./LoadingSpinner";
import ErrorMessage from "./ErrorMessage";

export default function RecentTransactions() {
  const { recentTransactions, loading, error } = useData();

  // Format transaction data
  const formatTransaction = (transaction) => {
    // Debug: print the data structure of the first transaction
    if (recentTransactions.length > 0 && recentTransactions[0] === transaction) {
      console.log('First transaction data structure:', transaction);
    }
    
    return {
      title: `${transaction.item_name || 'Unknown'} (${transaction.subcategory || 'Other'})`,
      desc: transaction.vendor || 'No vendor',
      date: transaction.transaction_date ? new Date(transaction.transaction_date).toISOString().split('T')[0] : 'Unknown date',
      amount: `-$${parseFloat(transaction.amount || 0).toFixed(2)}`
    };
  };

  // Show loading state
  if (loading) {
    return (
      <div>
        <div style={{ fontWeight: 700, fontSize: 26, marginBottom: 18 }}>Recent Transactions</div>
        <LoadingSpinner size="small" />
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div>
        <div style={{ fontWeight: 700, fontSize: 26, marginBottom: 18 }}>Recent Transactions</div>
        <ErrorMessage message={error} onRetry={() => window.location.reload()} />
      </div>
    );
  }

  // If no data, show default data
  const displayTransactions = recentTransactions.length > 0 
    ? recentTransactions.slice(0, 4).map(formatTransaction)
    : [
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

  return (
    <div>
      <div style={{ fontWeight: 700, fontSize: 26, marginBottom: 18 }}>Recent Transactions</div>
      <div>
        {displayTransactions.map((t, i) => (
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