'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getAIReportList, generateBiweeklyAIReport } from '../services/api';
import Navbar from '../components/Navbar';
import LoadingSpinner from '../components/LoadingSpinner';
import { toast } from 'react-toastify';

export default function AIReportList() {
  const router = useRouter();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [generating, setGenerating] = useState(false);
  const pageSize = 10;

  useEffect(() => {
    fetchReports();
  }, [currentPage]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await getAIReportList(currentPage, pageSize);
      setReports(response.reports);
      setTotalPages(Math.ceil(response.total / pageSize));
    } catch (err) {
      setError('Failed to get report list');
      console.error('Failed to get report list:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = (reportId) => {
    router.push(`/ai-report/${reportId}`);
  };

  // 生成近半个月的AI报告
  const handleGenerateReport = async () => {
    try {
      setGenerating(true);
      
      // 计算近半个月的日期范围
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - 14); // 14天前
      
      // 格式化日期为 YYYY-MM-DD
      const formatDate = (date) => {
        return date.toISOString().split('T')[0];
      };
      
      const startDateStr = formatDate(startDate);
      const endDateStr = formatDate(endDate);
      
      console.log('📅 生成报告时间范围:', startDateStr, 'to', endDateStr);
      
      // 调用API生成报告
      console.log('🚀 开始调用API生成报告...');
      const result = await generateBiweeklyAIReport(startDateStr, endDateStr);
      console.log('🔍 API调用结果:', result);
      console.log('🔍 结果类型:', typeof result);
      console.log('🔍 结果是否为真值:', !!result);
      
      if (result) {
        console.log('✅ 报告生成成功，显示成功提示');
        toast.success('AI Report generated successfully!');
        // 刷新报告列表
        console.log('🔄 开始刷新报告列表...');
        await fetchReports();
        console.log('✅ 报告列表刷新完成');
      } else {
        console.log('❌ 报告生成失败，显示错误提示');
        toast.error('Failed to generate AI Report');
      }
    } catch (error) {
      console.error('Failed to generate AI Report:', error);
      toast.error('Failed to generate AI Report');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      <Navbar />
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'flex-start',
          marginBottom: 32 
        }}>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 600, color: '#111' }}>AI Financial Reports</h1>
            <p style={{ color: '#666', marginTop: 8 }}>View all your AI financial analysis reports</p>
          </div>
          <button
            onClick={handleGenerateReport}
            disabled={generating}
            style={{
              background: '#111',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '12px 24px',
              fontSize: 14,
              fontWeight: 600,
              cursor: generating ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
              opacity: generating ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}
          >
            {generating ? (
              <>
                <div style={{
                  width: 16,
                  height: 16,
                  border: '2px solid #fff',
                  borderTop: '2px solid transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                Generating...
              </>
            ) : (
              'Generate AI Report'
            )}
          </button>
        </div>

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
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {reports.map((report) => (
              <div
                key={report.id}
                style={{
                  background: '#fff',
                  borderRadius: 16,
                  padding: 24,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  ':hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
                  }
                }}
                onClick={() => handleViewReport(report.id)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h3 style={{ fontSize: 18, fontWeight: 600, color: '#111' }}>
                      {report.period_name}
                    </h3>
                    <div style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
                      Transactions: {report.total_transactions} | Total Amount: ${report.total_amount}
                    </div>
                  </div>
                  <button
                    style={{
                      background: '#111',
                      color: '#fff',
                      border: 'none',
                      borderRadius: 6,
                      padding: '8px 16px',
                      fontSize: 14,
                      cursor: 'pointer',
                      transition: 'background 0.2s'
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewReport(report.id);
                    }}
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}

            {/* Pagination */}
            {totalPages > 1 && (
              <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                gap: 8, 
                marginTop: 24 
              }}>
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  style={{
                    padding: '4px 12px',
                    border: '1px solid #d9d9d9',
                    borderRadius: 4,
                    background: currentPage === 1 ? '#f5f5f5' : '#fff',
                    cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
                  }}
                >
                  Previous
                </button>
                <span style={{ padding: '4px 12px' }}>
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  style={{
                    padding: '4px 12px',
                    border: '1px solid #d9d9d9',
                    borderRadius: 4,
                    background: currentPage === totalPages ? '#f5f5f5' : '#fff',
                    cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
                  }}
                >
                  Next
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}