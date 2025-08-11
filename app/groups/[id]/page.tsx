'use client';
import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useGroup } from '../../context/GroupContext';
import { useAuth } from '../../components/AuthContext';
import Navbar from '../../components/Navbar';
import { toast } from 'react-toastify';

export default function GroupDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { 
    currentGroup, 
    loading, 
    getGroupInfo, 
    leaveGroup,
    getGroupStatistics,
    generateGroupAIReport
  } = useGroup();
  
  const [activeTab, setActiveTab] = useState('overview');
  const [statistics, setStatistics] = useState<any>(null);
  const [loadingStats, setLoadingStats] = useState(false);

  const groupId = parseInt(Array.isArray(params.id) ? params.id[0] || '0' : params.id || '0');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    if (groupId) {
      loadGroupInfo();
    }
  }, [user, groupId, router]);

  // 当切换到统计标签页时自动加载统计数据
  useEffect(() => {
    if (activeTab === 'statistics' && groupId && !statistics && !loadingStats) {
      loadStatistics();
    }
  }, [activeTab, groupId, statistics, loadingStats]);

  const loadGroupInfo = async () => {
    try {
      await getGroupInfo(groupId);
    } catch (error) {
      console.error('Failed to load group info:', error);
      router.push('/groups');
    }
  };

  const loadStatistics = async () => {
    setLoadingStats(true);
    try {
      const response = await getGroupStatistics(groupId);
      // 处理后端返回的数据结构
      if (response && response.success && response.data) {
        setStatistics(response.data);
      } else if (response && response.data) {
        // 兼容没有success字段的情况
        setStatistics(response.data);
      } else {
        // 兼容直接返回数据的情况
        setStatistics(response);
      }
    } catch (error) {
      console.error('Failed to load statistics:', error);
    } finally {
      setLoadingStats(false);
    }
  };

  const handleLeaveGroup = async () => {
    if (window.confirm('Are you sure you want to leave this group?')) {
      try {
        await leaveGroup(groupId);
        router.push('/groups');
      } catch (error) {
        console.error('Failed to leave group:', error);
      }
    }
  };

  const handleGenerateAIReport = async () => {
    try {
      await generateGroupAIReport(groupId);
    } catch (error) {
      console.error('Failed to generate AI report:', error);
    }
  };

  if (!user || !currentGroup) {
    return null;
  }

  const isAdmin = currentGroup.role === 'admin';

  // 字段兼容处理
  const group = currentGroup || {};
  const groupIdShow = group.group_id || group.id;
  const groupNameShow = group.group_name || group.name;
  const memberCountShow = group.member_count ?? (Array.isArray(group.members) ? group.members.length : 0);
  const maxMembersShow = group.max_members || 10;
  const createdAtShow = group.created_at || group.create_time || group.date;
  const formatDate = (dateString: any) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '';
    return date.toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' });
  };

  // 通用样式对象
  const styles = {
    primaryButton: {
      padding: '12px 20px',
      border: 'none',
      background: '#111',
      color: '#fff',
      borderRadius: '6px',
      cursor: 'pointer',
      fontWeight: '600'
    },
    secondaryButton: {
      padding: '12px 20px',
      border: '1px solid #111',
      background: '#fff',
      color: '#111',
      borderRadius: '6px',
      cursor: 'pointer',
      fontWeight: '600'
    },
    coloredButton: (color: string) => ({
      padding: '12px 20px',
      border: `1px solid ${color}`,
      background: '#fff',
      color: color,
      borderRadius: '6px',
      cursor: 'pointer',
      fontWeight: '600'
    }),
    tabButton: (isActive: boolean) => ({
      padding: '16px 24px',
      border: 'none',
      background: isActive ? '#111' : 'transparent',
      color: isActive ? '#fff' : '#666',
      cursor: 'pointer',
      fontWeight: '600',
      borderBottom: isActive ? '2px solid #111' : 'none'
    }),
    statCard: {
      padding: '16px',
      background: '#f8f9fa',
      borderRadius: '6px',
      textAlign: 'center' as const
    },
    statValue: {
      fontSize: '24px',
      fontWeight: '700'
    },
    statLabel: {
      fontSize: '14px',
      color: '#666'
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Navbar />
      
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
        {/* 头部信息 */}
        <div style={{ 
          background: '#fff', 
          borderRadius: '8px', 
          padding: '24px', 
          marginBottom: '24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
            <div style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              background: '#111',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: '600',
              fontSize: '24px',
              marginRight: '16px'
            }}>
              {groupNameShow?.[0]?.toUpperCase() || 'G'}
            </div>
            <div style={{ flex: 1 }}>
              <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#222', margin: '0 0 8px 0' }}>
                {groupNameShow || 'Unnamed Group'}
              </h1>
              <p style={{ color: '#666', margin: 0, fontSize: '16px' }}>
                {group.description || 'No description'}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <span style={{
                padding: '6px 12px',
                background: isAdmin ? '#ff4d4f' : '#52c41a',
                color: '#fff',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500'
              }}>
                {isAdmin ? 'Admin' : 'Member'}
              </span>
              <button
                onClick={handleLeaveGroup}
                style={{
                  padding: '8px 16px',
                  border: '1px solid #ff4d4f',
                  background: '#fff',
                  color: '#ff4d4f',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Leave Group
              </button>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '24px', fontSize: '14px', color: '#666' }}>
            <div>
              <span style={{ fontWeight: '600' }}>Group ID:</span> {groupIdShow}
            </div>
            <div>
              <span style={{ fontWeight: '600' }}>Members:</span> {memberCountShow}/{maxMembersShow}
            </div>
            <div>
              <span style={{ fontWeight: '600' }}>Created:</span> {formatDate(createdAtShow)}
            </div>
          </div>
        </div>

        {/* 功能按钮 */}
        <div style={{ 
          display: 'flex', 
          gap: '12px', 
          marginBottom: '24px',
          flexWrap: 'wrap'
        }}>
          <button
            onClick={() => router.push(`/groups/${groupId}/transactions`)}
            style={styles.primaryButton}
          >
            View Transactions
          </button>
          <button
            onClick={() => router.push(`/groups/${groupId}/share`)}
            style={styles.secondaryButton}
          >
            Share Transactions
          </button>
          <button
            onClick={handleGenerateAIReport}
            style={styles.coloredButton('#722ed1')}
          >
            Generate AI Report
          </button>
          <button
            onClick={() => router.push(`/groups/${groupId}/ai-report-list`)}
            style={styles.coloredButton('#13c2c2')}
          >
            View AI Reports
          </button>
        </div>

        {/* 标签页 */}
        <div style={{ 
          background: '#fff', 
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ 
            display: 'flex', 
            borderBottom: '1px solid #f0f0f0'
          }}>
            <button
              onClick={() => setActiveTab('overview')}
              style={styles.tabButton(activeTab === 'overview')}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('members')}
              style={styles.tabButton(activeTab === 'members')}
            >
              Members ({currentGroup.members?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('statistics')}
              style={styles.tabButton(activeTab === 'statistics')}
            >
              Statistics
            </button>
          </div>

          <div style={{ padding: '24px' }}>
            {activeTab === 'overview' && (
              <div>
                <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>
                  Group Overview
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  <div style={styles.statCard}>
                    <div style={{ ...styles.statValue, color: '#111' }}>
                      {memberCountShow}
                    </div>
                    <div style={styles.statLabel}>Current Members</div>
                  </div>
                  <div style={styles.statCard}>
                    <div style={{ ...styles.statValue, color: '#52c41a' }}>
                      {maxMembersShow}
                    </div>
                    <div style={styles.statLabel}>Max Members</div>
                  </div>
                  <div style={styles.statCard}>
                    <div style={{ ...styles.statValue, color: '#722ed1' }}>
                      {currentGroup.transaction_count || 0}
                    </div>
                    <div style={styles.statLabel}>Shared Transactions</div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'members' && (
              <div>
                <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>
                  Member List
                </h3>
                {currentGroup.members && currentGroup.members.length > 0 ? (
                  <div style={{ display: 'grid', gap: '12px' }}>
                    {currentGroup.members.map((member: any, index: number) => (
                      <div
                        key={member.id || index}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          padding: '12px',
                          background: '#f8f9fa',
                          borderRadius: '6px'
                        }}
                      >
                        <div style={{
                          width: '40px',
                          height: '40px',
                          borderRadius: '50%',
                          background: '#111',
                          color: '#fff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: '600',
                          marginRight: '12px'
                        }}>
                          {member.username?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: '600', color: '#222' }}>
                            {member.username}
                          </div>
                          <div style={{ fontSize: '12px', color: '#666' }}>
                            {member.email}
                          </div>
                        </div>
                        <span style={{
                          padding: '4px 8px',
                          background: member.role === 'admin' ? '#ff4d4f' : '#52c41a',
                          color: '#fff',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '500'
                        }}>
                          {member.role === 'admin' ? 'Admin' : 'Member'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                    No member information available
                  </div>
                )}
              </div>
            )}

            {activeTab === 'statistics' && (
              <div>
                <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>
                  Statistics {statistics?.period && `(${statistics.period})`}
                </h3>
                
                {loadingStats ? (
                  <div style={{ textAlign: 'center', padding: '40px' }}>
                    <div style={{ fontSize: '16px', color: '#666' }}>Loading statistics...</div>
                  </div>
                ) : statistics && Object.keys(statistics).length > 0 ? (
                  <div>
                    {/* 基础统计卡片 */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                      <div style={styles.statCard}>
                        <div style={{ ...styles.statValue, color: '#111' }}>
                          ¥{statistics.total_amount || 0}
                        </div>
                        <div style={styles.statLabel}>Total Amount</div>
                      </div>
                      <div style={styles.statCard}>
                        <div style={{ ...styles.statValue, color: '#52c41a' }}>
                          {statistics.total_transactions || 0}
                        </div>
                        <div style={styles.statLabel}>Transaction Count</div>
                      </div>
                      <div style={styles.statCard}>
                        <div style={{ ...styles.statValue, color: '#722ed1' }}>
                          ¥{statistics.average_amount || 0}
                        </div>
                        <div style={styles.statLabel}>Average Amount</div>
                      </div>
                      <div style={styles.statCard}>
                        <div style={{ ...styles.statValue, color: '#fa8c16' }}>
                          {statistics.member_count || 0}
                        </div>
                        <div style={styles.statLabel}>Participating Members</div>
                      </div>
                    </div>

                    {/* 详细统计信息 */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
                      {/* 消费最多的成员 */}
                      {statistics.top_members && statistics.top_members.length > 0 && (
                        <div style={{ 
                          background: '#f8f9fa', 
                          borderRadius: '8px',
                          padding: '20px'
                        }}>
                          <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#222' }}>
                            Top Spending Members
                          </h4>
                          <div style={{ display: 'grid', gap: '12px' }}>
                            {statistics.top_members.map((member: any, index: number) => (
                              <div key={index} style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                padding: '12px',
                                background: '#fff',
                                borderRadius: '6px'
                              }}>
                                <div>
                                  <div style={{ fontWeight: '600', color: '#222' }}>
                                    {member.user__username}
                                  </div>
                                  <div style={{ fontSize: '12px', color: '#666' }}>
                                    {member.transaction_count} transactions
                                  </div>
                                </div>
                                <div style={{ fontWeight: '600', color: '#111' }}>
                                  ¥{member.total_amount}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 消费最多的分类 */}
                      {statistics.top_categories && statistics.top_categories.length > 0 && (
                        <div style={{ 
                          background: '#f8f9fa', 
                          borderRadius: '8px',
                          padding: '20px'
                        }}>
                          <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#222' }}>
                            Top Spending Categories
                          </h4>
                          <div style={{ display: 'grid', gap: '12px' }}>
                            {statistics.top_categories.map((category: any, index: number) => (
                              <div key={index} style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                padding: '12px',
                                background: '#fff',
                                borderRadius: '6px'
                              }}>
                                <div>
                                  <div style={{ fontWeight: '600', color: '#222' }}>
                                    {category.category__name}
                                  </div>
                                  <div style={{ fontSize: '12px', color: '#666' }}>
                                    {category.transaction_count} transactions
                                  </div>
                                </div>
                                <div style={{ fontWeight: '600', color: '#52c41a' }}>
                                  ¥{category.total_amount}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 消费最多的商家 */}
                      {statistics.top_vendors && statistics.top_vendors.length > 0 && (
                        <div style={{ 
                          background: '#f8f9fa', 
                          borderRadius: '8px',
                          padding: '20px'
                        }}>
                          <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#222' }}>
                            Top Spending Vendors
                          </h4>
                          <div style={{ display: 'grid', gap: '12px' }}>
                            {statistics.top_vendors.map((vendor: any, index: number) => (
                              <div key={index} style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                padding: '12px',
                                background: '#fff',
                                borderRadius: '6px'
                              }}>
                                <div>
                                  <div style={{ fontWeight: '600', color: '#222' }}>
                                    {vendor.vendor}
                                  </div>
                                  <div style={{ fontSize: '12px', color: '#666' }}>
                                    {vendor.transaction_count} transactions
                                  </div>
                                </div>
                                <div style={{ fontWeight: '600', color: '#722ed1' }}>
                                  ¥{vendor.total_amount}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                    <div style={{ marginBottom: '16px' }}>No statistics available</div>
                    <button
                      onClick={loadStatistics}
                      style={{
                        padding: '8px 16px',
                        background: '#111',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      Click to load statistics
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
