'use client';
import React, { useEffect, useState } from "react";
import { useAuth } from "./components/AuthContext";
import { useData } from "./context/DataContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import SummaryCard from "./components/SummaryCard";
import ExpenseChart from "./components/ExpenseChart";
import RecentTransactions from "./components/RecentTransactions";
import ValidDate from "./components/ValidDate";
import FinancialAdvice from "./components/FinancialAdvice";
import AbnormalAlert from "./components/AbnormalAlert";
import { syncGmailReceipts, getGmailAuthStatus, getAllTransactions } from "./services/api";

export default function Home() {
  const { user } = useAuth();
  const { refreshAllData } = useData();
  const isMember = user?.isMember || false; // 从user对象中获取isMember状态
  const [showGmailSuccess, setShowGmailSuccess] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncError, setSyncError] = useState<string | null>(null);
  const [totalExpenses, setTotalExpenses] = useState("-$136.24");
  const [currentBalance, setCurrentBalance] = useState("$2,863.76");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window !== 'undefined' && localStorage.getItem('gmail_authorized_success')) {
      setShowGmailSuccess(true);
      localStorage.removeItem('gmail_authorized_success');
      setTimeout(() => setShowGmailSuccess(false), 5000);
    }
  }, []);

  // 获取真实消费数据
  useEffect(() => {
    const fetchExpenseData = async () => {
      try {
        setLoading(true);
        console.log('🔍 开始获取消费数据...');
        
        const transactions = await getAllTransactions();
        
        if (transactions && transactions.length > 0) {
          console.log('✅ 成功获取交易数据:', transactions.length, '条');
          
          // 获取最近6个月的日期范围
          const today = new Date();
          const sixMonthsAgo = new Date(today);
          sixMonthsAgo.setMonth(today.getMonth() - 6);
          sixMonthsAgo.setDate(1);
          sixMonthsAgo.setHours(0, 0, 0, 0);

          // 过滤最近6个月的交易
          const recentTransactions = transactions.filter((tx: any) => {
            const txDate = new Date(tx.transaction_date);
            return txDate >= sixMonthsAgo && txDate <= today;
          });

          console.log('📊 最近6个月交易数量:', recentTransactions.length);
          
          // 计算最近6个月的总消费金额
          const totalAmount = recentTransactions.reduce((sum: number, tx: any) => {
            return sum + parseFloat(tx.amount || 0);
          }, 0);
          
          const formattedAmount = `-$${totalAmount.toFixed(2)}`;
          console.log('💰 计算得到最近6个月总消费金额:', formattedAmount);
          setTotalExpenses(formattedAmount);

          // 计算Current Balance: 50 - 半年transaction总金额
          const balance = 50 - totalAmount;
          const formattedBalance = `$${balance.toFixed(2)}`;
          console.log('💰 计算得到Current Balance:', formattedBalance);
          setCurrentBalance(formattedBalance);
        } else {
          console.log('⚠️ 未找到交易数据，使用默认值');
          setTotalExpenses("-$136.24");
          setCurrentBalance("$2,863.76");
        }
        
      } catch (err) {
        console.error('❌ 获取消费数据失败:', err);
        setTotalExpenses("-$136.24");
        setCurrentBalance("$2,863.76");
      } finally {
        setLoading(false);
      }
    };

    fetchExpenseData();
  }, []);

  // 处理Gmail同步
  const handleSyncGmail = async () => {
    try {
      console.log('🚀 开始处理Gmail同步...');
      console.log('🔍 同步前Token:', localStorage.getItem('authToken') ? '存在' : '不存在');
      
      setSyncLoading(true);
      setSyncError(null);
      
      await syncGmailReceipts();
      
      console.log('✅ Gmail同步成功，准备刷新数据...');
      console.log('🔍 数据刷新前Token:', localStorage.getItem('authToken') ? '存在' : '不存在');
      
      // 同步成功后刷新数据
      await refreshAllData();
      
      console.log('✅ 数据刷新完成');
      
      setShowGmailSuccess(true);
      setTimeout(() => setShowGmailSuccess(false), 5000);
    } catch (error) {
      console.error('❌ Gmail同步错误:', error);
      console.log('🔍 错误时Token状态:', localStorage.getItem('authToken') ? '存在' : '不存在');
      
      if (error instanceof Error && error.message && error.message.includes('认证失败')) {
        setSyncError('认证失败，请重新登录');
        // 只有在非登录页面才重定向
        if (!window.location.pathname.includes('/login')) {
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
        }
      } else {
        setSyncError('同步失败，请重试');
      }
    } finally {
      setSyncLoading(false);
    }
  };

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
            同步成功！
          </div>
        )}
        {syncError && (
          <div style={{
            position: 'fixed',
            top: 30,
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#ff4d4f',
            color: '#fff',
            padding: '16px 32px',
            borderRadius: 8,
            fontWeight: 700,
            fontSize: 20,
            zIndex: 9999,
            boxShadow: '0 2px 12px rgba(0,0,0,0.12)'
          }}>
            {syncError}
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
                <SummaryCard title="Total Income :" icon={<span role="img" aria-label="income">🧑‍💼</span>} value="$50.00" />
                <SummaryCard title="Total Expenses" icon={<span role="img" aria-label="expenses">🧑‍🚀</span>} value={totalExpenses} />
                <SummaryCard title="Current Balance" icon={<span role="img" aria-label="balance">🧑‍🎤</span>} value={currentBalance} />
              </div>
            </div>
            {/* Right: main button area */}
            <div style={{ flex: 1, minWidth: 260, display: "flex", flexDirection: "column", gap: 24, alignItems: "stretch", marginTop: 12 }}>
              <button 
                onClick={handleSyncGmail}
                disabled={syncLoading}
                style={{
                  background: syncLoading ? "#666" : "#111",
                  color: "#fff",
                  borderRadius: 8,
                  padding: "18px 32px",
                  fontWeight: 700,
                  fontSize: 20,
                  border: "none",
                  cursor: syncLoading ? "not-allowed" : "pointer",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                  textAlign: "center",
                  transition: "background-color 0.2s"
                }}
              >
                {syncLoading ? "同步中..." : "Sync Gmail receipts"}
              </button>
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
