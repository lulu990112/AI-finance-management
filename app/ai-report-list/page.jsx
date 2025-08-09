'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getAIReportList } from '../services/api';
import Navbar from '../components/Navbar';
import LoadingSpinner from '../components/LoadingSpinner';

export default function AIReportList() {
  const router = useRouter();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
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
      setError('获取报告列表失败');
      console.error('获取报告列表失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = (reportId) => {
    router.push(`/ai-report/${reportId}`);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Navbar />
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 600, color: '#111' }}>AI Financial Reports</h1>
          <p style={{ color: '#666', marginTop: 8 }}>查看您的所有AI财务分析报告</p>
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
                      交易笔数: {report.total_transactions} | 总金额: ${report.total_amount}
                    </div>
                  </div>
                  <button
                    style={{
                      background: '#1677ff',
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
                    查看详情
                  </button>
                </div>
              </div>
            ))}

            {/* 分页控制 */}
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
                  上一页
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
                  下一页
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}