'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getAIReportDetail } from '../../services/api';
import Navbar from '../../components/Navbar';
import LoadingSpinner from '../../components/LoadingSpinner';
import { FaArrowLeft } from 'react-icons/fa';

export default function AIReportDetail({ params }) {
  const router = useRouter();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reportId, setReportId] = useState(null);

  useEffect(() => {
    // 处理params Promise
    const handleParams = async () => {
      try {
        const resolvedParams = await params;
        setReportId(resolvedParams.id);
      } catch (error) {
        console.error('解析params失败:', error);
        setError('页面参数错误');
      }
    };
    
    handleParams();
  }, [params]);

  useEffect(() => {
    if (reportId) {
      fetchReportDetail();
    }
  }, [reportId]);

  const fetchReportDetail = async () => {
    try {
      setLoading(true);
      const data = await getAIReportDetail(reportId);
      if (data) {
        setReport(data);
      } else {
        setError('未找到报告数据');
      }
    } catch (err) {
      setError('获取报告详情失败');
      console.error('获取报告详情失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    router.push('/ai-report-list');
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Navbar />
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
        {/* 返回按钮 */}
        <button
          onClick={handleBack}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            background: 'none',
            border: 'none',
            color: '#666',
            cursor: 'pointer',
            marginBottom: 24,
            padding: 0
          }}
        >
          <FaArrowLeft /> 返回报告列表
        </button>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}>
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div style={{ 
            background: '#fff', 
            padding: 24, 
            borderRadius: 12,
            textAlign: 'center',
            color: '#ff4d4f'
          }}>
            {error}
          </div>
        ) : report ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            {/* 标题 */}
            <div style={{ marginBottom: 16 }}>
              <h1 style={{ fontSize: 28, fontWeight: 600, color: '#111' }}>
                AI Financial Report
              </h1>
              <p style={{ color: '#666', marginTop: 8 }}>
                分析期间: {report.period_name}
              </p>
            </div>

            {/* Financial Advice Summary */}
            <div style={{
              background: '#fff',
              borderRadius: 16,
              padding: 32,
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
            }}>
              <h2 style={{ fontSize: 20, fontWeight: 600, color: '#111', marginBottom: 16 }}>
                Financial Advice Summary
              </h2>
              <p style={{ color: '#333', lineHeight: 1.6 }}>
                {report.financial_advice_summary}
              </p>
            </div>

            {/* Abnormal Alert */}
            <div style={{
              background: '#fff',
              borderRadius: 16,
              padding: 32,
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
            }}>
              <h2 style={{ fontSize: 20, fontWeight: 600, color: '#111', marginBottom: 16 }}>
                Abnormal Alert
              </h2>
              <p style={{ color: '#333', lineHeight: 1.6 }}>
                {report.abnormal_alert}
              </p>
            </div>

            {/* Money Saving Tips */}
            <div style={{
              background: '#fff',
              borderRadius: 16,
              padding: 32,
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
            }}>
              <h2 style={{ fontSize: 20, fontWeight: 600, color: '#111', marginBottom: 16 }}>
                Money Saving Tips
              </h2>
              <p style={{ color: '#333', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                {report.money_saving_tip}
              </p>
            </div>

            {/* 报告元数据 */}
            <div style={{
              background: '#fff',
              borderRadius: 16,
              padding: 24,
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
              marginTop: 8
            }}>
              <div style={{ display: 'flex', gap: 32, color: '#666' }}>
                <div>
                  <strong>总交易笔数:</strong> {report.total_transactions}
                </div>
                <div>
                  <strong>总金额:</strong> ${report.total_amount}
                </div>
                <div>
                  <strong>报告生成时间:</strong> {new Date(report.report_date).toLocaleDateString()}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}