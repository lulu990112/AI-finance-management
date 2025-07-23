'use client';
import React from "react";
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

  return (
    <ProtectedRoute>
      <div style={{ background: "#fafbfc", minHeight: "100vh" }}>
        <Navbar />
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "32px 16px 0 16px" }}>
          {/* 顶部主区块：左欢迎语+卡片，右主按钮 */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 32 }}>
            {/* 左侧：欢迎语+SummaryCard */}
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
            {/* 右侧：主按钮区 */}
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
                  普通用户
                </div>
              )}
            </div>
          </div>
          {/* 会员专属内容 */}
          {isMember && (
            <div style={{ display: "flex", gap: 18, marginTop: 32, flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 320 }}>
                <FinancialAdvice />
                <AbnormalAlert />
              </div>
            </div>
          )}
          {/* 下方主内容区 */}
          <div style={{ display: "flex", gap: 48, marginTop: 32, flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 320 }}>
              <div style={{ fontWeight: 700, fontSize: 28, marginBottom: 18 }}>Expense Categories</div>
              <ExpenseChart />
            </div>
            <div style={{ flex: 1, minWidth: 320 }}>
              <RecentTransactions />
            </div>
          </div>
          {/* 用户信息显示 */}
          <div style={{ marginTop: 48, textAlign: "center", color: "#666", fontSize: 14 }}>
            <div>当前用户：{user?.username}</div>
            <div>用户类型：{isMember ? "会员用户" : "普通用户"}</div>
            <div>邮箱：{user?.email}</div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
