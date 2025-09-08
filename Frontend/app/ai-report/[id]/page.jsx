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
    // Handle params Promise
    const handleParams = async () => {
      try {
        const resolvedParams = await params;
        setReportId(resolvedParams.id);
      } catch (error) {
        console.error('Failed to parse params:', error);
        setError('Page parameter error');
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
        setError('Report data not found');
      }
    } catch (err) {
      setError('Failed to get report details');
      console.error('Failed to get report details:', err);
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
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
        {/* Back button */}
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
            padding: 0,
            fontSize: '14px'
          }}
        >
          <FaArrowLeft /> Back to Report List
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
            {/* Title and basic information */}
            <div style={{ 
              background: '#fff', 
              borderRadius: '8px', 
              padding: '24px', 
              marginBottom: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#222', margin: '0 0 8px 0' }}>
                AI Financial Report
              </h1>
              <p style={{ color: '#666', margin: 0, fontSize: '16px' }}>
                Analysis Period: {report.period_name}
              </p>
            </div>

            {/* Financial Advice Summary */}
            <div style={{
              background: '#fff',
              borderRadius: '8px',
              padding: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              border: '1px solid #e6f7ff',
              borderLeft: '4px solid #1890ff'
            }}>
              <h2 style={{ 
                fontSize: '20px', 
                fontWeight: '600', 
                color: '#222', 
                margin: '0 0 16px 0',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span style={{ 
                  width: '4px', 
                  height: '20px', 
                  background: '#1890ff', 
                  borderRadius: '2px' 
                }}></span>
                Financial Advice Summary
              </h2>
              <div style={{ 
                color: '#333', 
                lineHeight: '1.6',
                fontSize: '15px',
                padding: '16px',
                background: '#f8f9fa',
                borderRadius: '6px',
                border: '1px solid #e6f7ff'
              }}>
                {report.financial_advice_summary}
              </div>
            </div>

            {/* Abnormal Alert */}
            <div style={{
              background: '#fff',
              borderRadius: '8px',
              padding: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              border: '1px solid #fff2f0',
              borderLeft: '4px solid #ff4d4f'
            }}>
              <h2 style={{ 
                fontSize: '20px', 
                fontWeight: '600', 
                color: '#222', 
                margin: '0 0 16px 0',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span style={{ 
                  width: '4px', 
                  height: '20px', 
                  background: '#ff4d4f', 
                  borderRadius: '2px' 
                }}></span>
                Abnormal Alert
              </h2>
              <div style={{ 
                color: '#333', 
                lineHeight: '1.6',
                fontSize: '15px',
                padding: '16px',
                background: '#fff2f0',
                borderRadius: '6px',
                border: '1px solid #ffccc7'
              }}>
                {report.abnormal_alert}
              </div>
            </div>

            {/* Money Saving Tips */}
            <div style={{
              background: '#fff',
              borderRadius: '8px',
              padding: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              border: '1px solid #f6ffed',
              borderLeft: '4px solid #52c41a'
            }}>
              <h2 style={{ 
                fontSize: '20px', 
                fontWeight: '600', 
                color: '#222', 
                margin: '0 0 16px 0',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span style={{ 
                  width: '4px', 
                  height: '20px', 
                  background: '#52c41a', 
                  borderRadius: '2px' 
                }}></span>
                Money Saving Tips
              </h2>
              <div style={{ 
                color: '#333', 
                lineHeight: '1.6',
                fontSize: '15px',
                padding: '16px',
                background: '#f6ffed',
                borderRadius: '6px',
                border: '1px solid #b7eb8f',
                whiteSpace: 'pre-line'
              }}>
                {report.money_saving_tip}
              </div>
            </div>

            {/* Report metadata */}
            <div style={{
              background: '#fff',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              border: '1px solid #f0f0f0'
            }}>
              <div style={{ 
                display: 'flex', 
                gap: '32px', 
                color: '#666',
                fontSize: '14px',
                flexWrap: 'wrap'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ 
                    width: '8px', 
                    height: '8px', 
                    background: '#1890ff', 
                    borderRadius: '50%' 
                  }}></span>
                  <strong>Total Transactions:</strong> {report.total_transactions}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ 
                    width: '8px', 
                    height: '8px', 
                    background: '#52c41a', 
                    borderRadius: '50%' 
                  }}></span>
                  <strong>Total Amount:</strong> ${report.total_amount}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ 
                    width: '8px', 
                    height: '8px', 
                    background: '#722ed1', 
                    borderRadius: '50%' 
                  }}></span>
                  <strong>Report Generated:</strong> {new Date(report.report_date).toLocaleDateString()}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}