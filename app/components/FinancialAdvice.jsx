import React, { useState, useEffect } from "react";
import { getAIReportList } from "../services/api";

export default function FinancialAdvice() {
  const [adviceData, setAdviceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAdviceData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('🤖 开始获取财务建议数据...');
        // 使用报告列表接口，获取第一页数据，取第一个（最新的）报告
        const response = await getAIReportList(1, 1);
        
        if (response && response.reports && response.reports.length > 0) {
          const latestReport = response.reports[0];
          console.log('✅ 成功获取最新报告:', latestReport);
          
          if (latestReport.financial_advice_summary) {
            setAdviceData(latestReport.financial_advice_summary);
          } else {
            console.log('⚠️ 最新报告中没有财务建议数据');
            setAdviceData(null);
          }
        } else {
          console.log('⚠️ 未找到报告数据，使用默认内容');
          setAdviceData(null);
        }
      } catch (err) {
        console.error('❌ 获取财务建议失败:', err);
        if (err.message && err.message.includes('认证失败')) {
          setError('认证失败，请重新登录');
        } else {
          setError('获取财务建议失败');
        }
        setAdviceData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchAdviceData();
  }, []);

  // 默认内容
  const defaultAdvice = "We noticed your dining out expenses are up 15% from last week. Try cooking at home 1~2 more times a week to save money. Most of your shopping is on electronics—keep an eye out for deals.";

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
        {loading && <span style={{ fontSize: 12, color: "#666", marginLeft: 8 }}>(Loading...)</span>}
      </div>
      <div style={{ color: "#444" }}>
        {loading ? (
                      <div style={{ color: "#666", fontStyle: "italic" }}>Loading...</div>
        ) : error ? (
          <div style={{ color: "#ff4d4f" }}>{error}</div>
        ) : adviceData ? (
          adviceData
        ) : (
          defaultAdvice
        )}
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