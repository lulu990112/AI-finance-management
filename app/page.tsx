'use client';
import React, { useEffect, useState } from "react";
import { useAuth } from "./components/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import SummaryCard from "./components/SummaryCard";
import ExpenseChart from "./components/ExpenseChart";
import RecentTransactions from "./components/RecentTransactions";
import ValidDate from "./components/ValidDate";
import FinancialAdvice from "./components/FinancialAdvice";
import AbnormalAlert from "./components/AbnormalAlert";

export default function Home() {
  const { user } = useAuth();
  const isMember = user?.isMember || false;
  const [showGmailSuccess, setShowGmailSuccess] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined' && localStorage.getItem('gmail_authorized_success')) {
      setShowGmailSuccess(true);
      localStorage.removeItem('gmail_authorized_success');
      setTimeout(() => setShowGmailSuccess(false), 5000);
    }
  }, []);

  return (
    <ProtectedRoute>
      <div style={{ background: "#fafbfc", minHeight: "100vh" }}>
        <Navbar />
        {showGmailSuccess && (
          <div style={{
            position: 'fixed',
            top: 30,
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#52c41a',
            color: '#fff',
            padding: '16px 32px',
            borderRadius: 8,
            fontWeight: 700,
            fontSize: 20,
            zIndex: 9999,
            boxShadow: '0 2px 12px rgba(0,0,0,0.12)'
          }}>
            Success!
          </div>
        )}
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "32px 16px 0 16px" }}>
          {/* Top main block: left welcome + cards, right main button */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 32 }}>
            {/* Left: welcome + SummaryCard */}
            <div style={{ flex: 2, minWidth: 340 }}>
              <div style={{ fontWeight: 800, fontSize: 48, marginBottom: 18, lineHeight: 1.1 }}>
                Welcome back,<br />{isMember ? "valued member" : "regular user"} !
              </div>
              <div style={{ display: "flex", gap: 18, marginTop: 8, flexWrap: "wrap" }}>
                <SummaryCard title="Total Income :" icon={<span role="img" aria-label="income">🧑‍💼</span>} value="$3,000.00" />
                <SummaryCard title="Total Expenses" icon={<span role="img" aria-label="expenses">🧑‍🚀</span>} value="-$136.24" />
                <SummaryCard title="Current Balance" icon={<span role="img" aria-label="balance">🧑‍🎤</span>} value="$2,863.76" />
              </div>
            </div>
            {/* Right: main button area */}
            <div style={{ flex: 1, minWidth: 260, display: "flex", flexDirection: "column", gap: 24, alignItems: "stretch", marginTop: 12 }}>
              <a href="#" style={{
                background: "#111",
                color: "#fff",
                borderRadius: 8,
                padding: "18px 32px",
                fontWeight: 700,
                fontSize: 20,
                textDecoration: "none",
                display: "block",
                boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                textAlign: "center"
              }}>Sync Gmail receipts</a>
              {isMember ? <ValidDate /> : (
                <div style={{
                  background: "#111",
                  color: "#fff",
                  borderRadius: 8,
                  padding: "18px 32px",
                  fontWeight: 700,
                  fontSize: 20,
                  textAlign: "center",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.08)"
                }}>
                  Regular User
                </div>
              )}
            </div>
          </div>
          {/* Member exclusive content */}
          {isMember && (
            <div style={{ display: "flex", gap: 18, marginTop: 32, flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 320 }}>
                <FinancialAdvice />
                <AbnormalAlert />
              </div>
            </div>
          )}
          {/* Bottom main content area */}
          <div style={{ display: "flex", gap: 48, marginTop: 32, flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 320 }}>
              <div style={{ fontWeight: 700, fontSize: 28, marginBottom: 18 }}>Expense Categories</div>
              <ExpenseChart />
            </div>
            <div style={{ flex: 1, minWidth: 320 }}>
              <RecentTransactions />
            </div>
          </div>
          {/* User info display */}
          <div style={{ marginTop: 48, textAlign: "center", color: "#666", fontSize: 14 }}>
            <div>Current User: {user?.username}</div>
            <div>User Type: {isMember ? "Premium Member" : "Regular User"}</div>
            <div>Email: {user?.email}</div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
