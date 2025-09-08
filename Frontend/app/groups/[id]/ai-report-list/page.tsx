'use client';
import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '../../../components/AuthContext';
import { useGroup } from '../../../context/GroupContext';
import Navbar from '../../../components/Navbar';
import LoadingSpinner from '../../../components/LoadingSpinner';
import { groupService } from '../../../services/groupService';
import { toast } from 'react-toastify';

// Define AI report list item type
interface AIReportItem {
  id?: number;
  group_ai_report_id?: number;
  report_date?: string;
  created_at?: string;
  analysis_period?: string;
  total_transactions?: number;
  total_amount?: string | number;
  is_generated?: boolean;
  generation_status?: string;
}

export default function GroupAIReportList() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { currentGroup, getGroupInfo } = useGroup();
  
  const [reports, setReports] = useState<AIReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReports, setSelectedReports] = useState<number[]>([]);
  const [action, setAction] = useState('------');

  const groupId = parseInt(Array.isArray(params.id) ? params.id[0] || '0' : params.id || '0');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    if (groupId) {
      loadGroupInfo();
      fetchReports();
    }
  }, [user, groupId, router]);

  const loadGroupInfo = async () => {
    try {
      await getGroupInfo(groupId);
    } catch (error) {
      console.error('Failed to load group info:', error);
      router.push('/groups');
    }
  };

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await groupService.getGroupAIReports(groupId);
      const reportsData = response.reports || response || [];
      setReports(reportsData);
    } catch (err) {
      setError('Failed to get AI report list');
      console.error('Failed to get AI report list:', err);
      toast.error('Failed to get AI report list');
    } finally {
      setLoading(false);
    }
  };

  const getReportId = (report: AIReportItem): number | null => {
    const id = report.id || report.group_ai_report_id;
    return id && !isNaN(id) ? id : null;
  };

  const handleViewReport = (report: AIReportItem) => {
    const reportId = getReportId(report);
    
    if (reportId) {
      router.push(`/groups/${groupId}/ai-report/${reportId}`);
    } else {
      console.error('Invalid report ID:', reportId);
      toast.error('Invalid report ID');
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const validIds = reports.map(report => getReportId(report)).filter(id => id !== null) as number[];
      setSelectedReports(validIds);
    } else {
      setSelectedReports([]);
    }
  };

  const handleSelectReport = (reportId: number | null, checked: boolean) => {
    if (reportId === null) return;
    
    if (checked) {
      setSelectedReports([...selectedReports, reportId]);
    } else {
      setSelectedReports(selectedReports.filter(id => id !== reportId));
    }
  };

  const handleAction = () => {
    if (action === '------' || selectedReports.length === 0) {
      toast.warning('Please select action and reports');
      return;
    }
    
    // Batch operation logic can be added here
    toast.info(`Execute action: ${action}, selected reports: ${selectedReports.length}`);
  };

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '';
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (isGenerated: boolean | undefined) => {
    if (isGenerated) {
      return (
        <span style={{ color: '#52c41a', fontSize: '16px' }}>✓</span>
      );
    }
    return (
      <span style={{ color: '#faad14', fontSize: '16px' }}>⏳</span>
    );
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
              onClick={() => router.push(`/groups/${groupId}`)}
              style={{
                padding: '8px 16px',
                border: '1px solid #d9d9d9',
                background: '#fff',
                color: '#666',
                borderRadius: '6px',
                cursor: 'pointer',
                marginRight: '16px'
              }}
            >
              ← Back to Group
            </button>
            <h1 style={{ fontSize: '24px', fontWeight: '600', color: '#222', margin: 0 }}>
              {currentGroup.group_name || currentGroup.name} - AI Report List
            </h1>
          </div>
          <p style={{ color: '#666', margin: 0 }}>
            View all AI financial analysis reports for this group
          </p>
        </div>

        {/* Action bar */}
        <div style={{ 
          background: '#fff', 
          borderRadius: '8px', 
          padding: '16px 24px', 
          marginBottom: '24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          gap: '16px'
        }}>
          <span style={{ fontWeight: '600', color: '#222' }}>Action:</span>
          <select
            value={action}
            onChange={(e) => setAction(e.target.value)}
            style={{
              padding: '8px 12px',
              border: '1px solid #d9d9d9',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          >
            <option value="------">------</option>
            <option value="delete">Delete</option>
            <option value="export">Export</option>
          </select>
          <button
            onClick={handleAction}
            style={{
              padding: '8px 16px',
              border: 'none',
              background: '#111',
              color: '#fff',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            Go
          </button>
          <span style={{ color: '#666', fontSize: '14px' }}>
            {selectedReports.length} of {reports.length} selected
          </span>

        </div>

        {/* Report list */}
        <div style={{ 
          background: '#fff', 
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
              <LoadingSpinner />
            </div>
          ) : error ? (
            <div style={{ 
              padding: '24px', 
              textAlign: 'center',
              color: '#ff4d4f'
            }}>
              {error}
            </div>
          ) : reports.length === 0 ? (
            <div style={{ 
              padding: '40px', 
              textAlign: 'center',
              color: '#666'
            }}>
              No AI reports available, please generate AI reports first
            </div>
          ) : (
            <>
              {/* Table header */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '50px 1fr 1fr 1fr 1fr 1fr 1fr 1fr',
                padding: '16px 24px',
                background: '#fafafa',
                borderBottom: '1px solid #f0f0f0',
                fontWeight: '600',
                fontSize: '14px',
                color: '#222'
              }}>
                <div>
                  <input
                    type="checkbox"
                    checked={selectedReports.length === reports.length && reports.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    style={{ marginRight: '8px' }}
                  />
                  GROUP AI REPORT ID
                </div>
                <div>GROUP ID</div>
                <div>REPORT DATE</div>
                <div>ANALYSIS PERIOD</div>
                <div>TOTAL TRANSACTIONS</div>
                <div>TOTAL AMOUNT</div>
                <div>IS GENERATED</div>
                <div>GENERATION STATUS</div>
              </div>

              {/* Table content */}
              {reports.map((report, index) => (
                <div
                  key={report.id || report.group_ai_report_id || `report-${index}`}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '50px 1fr 1fr 1fr 1fr 1fr 1fr 1fr',
                    padding: '16px 24px',
                    borderBottom: '1px solid #f0f0f0',
                    fontSize: '14px',
                    color: '#333',
                    cursor: 'pointer',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#f5f5f5';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent';
                  }}
                  onClick={() => handleViewReport(report)}
                >
                  <div>
                    <input
                      type="checkbox"
                      checked={selectedReports.includes(getReportId(report) || 0)}
                      onChange={(e) => {
                        e.stopPropagation();
                        handleSelectReport(getReportId(report), e.target.checked);
                      }}
                      style={{ marginRight: '8px' }}
                    />
                    {getReportId(report) || 'N/A'}
                  </div>
                  <div>{groupId}</div>
                  <div>{formatDate(report.report_date || report.created_at)}</div>
                  <div>{report.analysis_period || 'Last 30 days'}</div>
                  <div>{report.total_transactions || 0}</div>
                  <div>${report.total_amount || '0.00'}</div>
                  <div>{getStatusIcon(report.is_generated)}</div>
                  <div style={{ 
                    color: report.generation_status === 'completed' ? '#52c41a' : 
                           report.generation_status === 'processing' ? '#faad14' : '#ff4d4f'
                  }}>
                    {report.generation_status || 'pending'}
                  </div>
                </div>
              ))}
            </>
          )}
        </div>

        {/* Bottom information */}
        <div style={{ 
          marginTop: '16px', 
          textAlign: 'center',
          color: '#666',
          fontSize: '14px'
        }}>
          {reports.length} group ai report{reports.length !== 1 ? 's' : ''}
        </div>
      </div>
    </div>
  );
}
