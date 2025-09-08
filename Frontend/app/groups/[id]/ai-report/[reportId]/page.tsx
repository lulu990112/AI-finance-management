'use client';
import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '../../../../components/AuthContext';
import { useGroup } from '../../../../context/GroupContext';
import Navbar from '../../../../components/Navbar';
import LoadingSpinner from '../../../../components/LoadingSpinner';
import { groupService } from '../../../../services/groupService';
import { FaArrowLeft } from 'react-icons/fa';

// Define AI report type
interface AIReport {
  id?: number;
  group_ai_report_id?: number;
  report_date?: string;
  created_at?: string;
  analysis_period?: string;
  total_transactions?: number;
  total_amount?: string | number;
  generation_status?: string;
  ai_analysis?: string;
  financial_advice?: string;
  financial_advice_summary?: string;
  abnormal_alert?: string;
  money_saving_tip?: string;
  category_breakdown?: Record<string, string | number>;
  transactions?: Array<{
    date?: string;
    transaction_date?: string;
    description?: string;
    item_name?: string;
    category?: string;
    category_name?: string;
    amount: string | number;
    member_name?: string;
    username?: string;
  }>;
}

export default function GroupAIReportDetail() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { currentGroup, getGroupInfo } = useGroup();
  
  const [report, setReport] = useState<AIReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const groupId = parseInt(Array.isArray(params.id) ? params.id[0] || '0' : params.id || '0');
  const reportId = parseInt(Array.isArray(params.reportId) ? params.reportId[0] || '0' : params.reportId || '0');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    if (groupId && reportId && reportId > 0) {
      loadGroupInfo();
      fetchReportDetail();
    } else {
      console.error('Invalid parameters:', { groupId, reportId });
      setError('Invalid report ID or group ID');
      setLoading(false);
    }
  }, [user, groupId, reportId, router]);

  const loadGroupInfo = async () => {
    try {
      await getGroupInfo(groupId);
    } catch (error) {
      console.error('Failed to load group info:', error);
      router.push('/groups');
    }
  };

  const fetchReportDetail = async () => {
    try {
      setLoading(true);
      const data = await groupService.getGroupAIReportDetail(groupId, reportId);
      if (data) {
        setReport(data as AIReport);
      } else {
        setError('Report data not found');
      }
    } catch (err) {
      setError('Failed to get report detail');
      console.error('Failed to get report detail:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    router.push(`/groups/${groupId}/ai-report-list`);
  };

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '';
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!user || !currentGroup) {
    return <LoadingSpinner />;
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Navbar />
      
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
        {/* Header information */}
        <div style={{ 
          background: '#fff', 
          borderRadius: '8px', 
          padding: '24px', 
          marginBottom: '24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
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
                marginRight: '16px',
                padding: 0
              }}
            >
              <FaArrowLeft /> Back to Report List
            </button>
            <h1 style={{ fontSize: '24px', fontWeight: '600', color: '#222', margin: 0 }}>
              {currentGroup.group_name || currentGroup.name} - AI Report Detail
            </h1>
          </div>
          <p style={{ color: '#666', margin: 0 }}>
            View detailed content of AI financial analysis report
          </p>
        </div>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div style={{ 
            background: '#fff', 
            padding: '24px', 
            borderRadius: '12px',
            textAlign: 'center',
            color: '#ff4d4f'
          }}>
            {error}
          </div>
        ) : report ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Report basic information */}
            <div style={{ 
              background: '#fff', 
              borderRadius: '8px', 
              padding: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#222', marginBottom: '16px' }}>
                Report Basic Information
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                <div>
                  <span style={{ color: '#666', fontSize: '14px' }}>Report ID:</span>
                  <div style={{ fontWeight: '600', color: '#222' }}>{report.id || report.group_ai_report_id}</div>
                </div>
                <div>
                  <span style={{ color: '#666', fontSize: '14px' }}>Group ID:</span>
                  <div style={{ fontWeight: '600', color: '#222' }}>{groupId}</div>
                </div>
                <div>
                  <span style={{ color: '#666', fontSize: '14px' }}>Report Date:</span>
                  <div style={{ fontWeight: '600', color: '#222' }}>
                    {formatDate(report.report_date || report.created_at)}
                  </div>
                </div>
                <div>
                  <span style={{ color: '#666', fontSize: '14px' }}>Analysis Period:</span>
                  <div style={{ fontWeight: '600', color: '#222' }}>
                    {report.analysis_period || 'Last 30 days'}
                  </div>
                </div>
                <div>
                  <span style={{ color: '#666', fontSize: '14px' }}>Transaction Count:</span>
                  <div style={{ fontWeight: '600', color: '#222' }}>
                    {report.total_transactions || 0}
                  </div>
                </div>
                <div>
                  <span style={{ color: '#666', fontSize: '14px' }}>Total Amount:</span>
                  <div style={{ fontWeight: '600', color: '#222' }}>
                    ${report.total_amount || '0.00'}
                  </div>
                </div>
                <div>
                  <span style={{ color: '#666', fontSize: '14px' }}>Generation Status:</span>
                  <div style={{ 
                    fontWeight: '600', 
                    color: report.generation_status === 'completed' ? '#52c41a' : 
                           report.generation_status === 'processing' ? '#faad14' : '#ff4d4f'
                  }}>
                    {report.generation_status || 'pending'}
                  </div>
                </div>
              </div>
            </div>

            {/* AI analysis content */}
            {report.ai_analysis && (
              <div style={{ 
                background: '#fff', 
                borderRadius: '8px', 
                padding: '24px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#222', marginBottom: '16px' }}>
                  AI Financial Analysis
                </h2>
                <div style={{ 
                  background: '#f8f9fa', 
                  padding: '20px', 
                  borderRadius: '8px',
                  border: '1px solid #e9ecef'
                }}>
                  <div style={{ 
                    whiteSpace: 'pre-wrap', 
                    lineHeight: '1.6',
                    color: '#333',
                    fontSize: '15px'
                  }}>
                    {report.ai_analysis}
                  </div>
                </div>
              </div>
            )}

            {/* Financial advice summary */}
            {report.financial_advice_summary && (
              <div style={{ 
                background: '#fff', 
                borderRadius: '8px', 
                padding: '24px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#222', marginBottom: '16px' }}>
                  Financial Advice Summary
                </h2>
                <div style={{ 
                  background: '#f0f9ff', 
                  padding: '20px', 
                  borderRadius: '8px',
                  border: '1px solid #bae6fd'
                }}>
                  <div style={{ 
                    whiteSpace: 'pre-wrap', 
                    lineHeight: '1.6',
                    color: '#0c4a6e',
                    fontSize: '15px'
                  }}>
                    {report.financial_advice_summary}
                  </div>
                </div>
              </div>
            )}

            {/* Abnormal alert */}
            {report.abnormal_alert && (
              <div style={{ 
                background: '#fff', 
                borderRadius: '8px', 
                padding: '24px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#222', marginBottom: '16px' }}>
                  Abnormal Alert
                </h2>
                <div style={{ 
                  background: '#fef2f2', 
                  padding: '20px', 
                  borderRadius: '8px',
                  border: '1px solid #fecaca'
                }}>
                  <div style={{ 
                    whiteSpace: 'pre-wrap', 
                    lineHeight: '1.6',
                    color: '#991b1b',
                    fontSize: '15px'
                  }}>
                    {report.abnormal_alert}
                  </div>
                </div>
              </div>
            )}

            {/* Money saving tips */}
            {report.money_saving_tip && (
              <div style={{ 
                background: '#fff', 
                borderRadius: '8px', 
                padding: '24px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#222', marginBottom: '16px' }}>
                  Money Saving Tips
                </h2>
                <div style={{ 
                  background: '#f0fdf4', 
                  padding: '20px', 
                  borderRadius: '8px',
                  border: '1px solid #bbf7d0'
                }}>
                  <div style={{ 
                    whiteSpace: 'pre-wrap', 
                    lineHeight: '1.6',
                    color: '#166534',
                    fontSize: '15px'
                  }}>
                    {report.money_saving_tip}
                  </div>
                </div>
              </div>
            )}

            {/* Financial advice (compatible with old format) */}
            {report.financial_advice && (
              <div style={{ 
                background: '#fff', 
                borderRadius: '8px', 
                padding: '24px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#222', marginBottom: '16px' }}>
                  Financial Advice
                </h2>
                <div style={{ 
                  background: '#f0f9ff', 
                  padding: '20px', 
                  borderRadius: '8px',
                  border: '1px solid #bae6fd'
                }}>
                  <div style={{ 
                    whiteSpace: 'pre-wrap', 
                    lineHeight: '1.6',
                    color: '#0c4a6e',
                    fontSize: '15px'
                  }}>
                    {report.financial_advice}
                  </div>
                </div>
              </div>
            )}

            {/* Spending category statistics */}
            {report.category_breakdown && (
              <div style={{ 
                background: '#fff', 
                borderRadius: '8px', 
                padding: '24px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#222', marginBottom: '16px' }}>
                  Expense Category Statistics
                </h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {Object.entries(report.category_breakdown).map(([category, amount]) => (
                    <div key={category} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      padding: '12px 16px',
                      background: '#f8f9fa',
                      borderRadius: '6px',
                      border: '1px solid #e9ecef'
                    }}>
                      <span style={{ fontWeight: '500', color: '#333' }}>{category}</span>
                      <span style={{ fontWeight: '600', color: '#1890ff' }}>${amount}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Transaction records */}
            {report.transactions && report.transactions.length > 0 && (
              <div style={{ 
                background: '#fff', 
                borderRadius: '8px', 
                padding: '24px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#222', marginBottom: '16px' }}>
                  Transaction Records
                </h2>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ 
                    width: '100%', 
                    borderCollapse: 'collapse',
                    fontSize: '14px'
                  }}>
                    <thead>
                      <tr style={{ background: '#fafafa' }}>
                        <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #f0f0f0' }}>
                          Date
                        </th>
                        <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #f0f0f0' }}>
                          Description
                        </th>
                        <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #f0f0f0' }}>
                          Category
                        </th>
                        <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #f0f0f0' }}>
                          Amount
                        </th>
                        <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #f0f0f0' }}>
                          Member
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.transactions.map((transaction, index) => (
                        <tr key={index} style={{ borderBottom: '1px solid #f0f0f0' }}>
                          <td style={{ padding: '12px' }}>
                            {formatDate(transaction.date || transaction.transaction_date)}
                          </td>
                          <td style={{ padding: '12px' }}>
                            {transaction.description || transaction.item_name}
                          </td>
                          <td style={{ padding: '12px' }}>
                            {transaction.category || transaction.category_name}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right', fontWeight: '600' }}>
                            ${parseFloat(String(transaction.amount)).toFixed(2)}
                          </td>
                          <td style={{ padding: '12px' }}>
                            {transaction.member_name || transaction.username}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ 
            background: '#fff', 
            padding: '24px', 
            borderRadius: '12px',
            textAlign: 'center',
            color: '#666'
          }}>
            Report data not found
          </div>
        )}
      </div>
    </div>
  );
}
