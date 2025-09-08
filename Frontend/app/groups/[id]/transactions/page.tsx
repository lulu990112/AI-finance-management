'use client';
import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useGroup } from '../../../context/GroupContext';
import { useAuth } from '../../../components/AuthContext';
import Navbar from '../../../components/Navbar';
import { toast } from 'react-toastify';

export default function GroupTransactionsPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { currentGroup, getGroupInfo, getGroupTransactions } = useGroup();
  
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [memberFilter, setMemberFilter] = useState('');

  const groupId = parseInt(Array.isArray(params.id) ? params.id[0] || '0' : params.id || '0');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    if (groupId) {
      loadGroupInfo();
      loadTransactions();
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

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const response = await getGroupTransactions(groupId);
      setTransactions(response || []);
    } catch (error) {
      console.error('Failed to load group transactions:', error);
      toast.error('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  // 筛选交易
  const filteredTransactions = transactions.filter(transaction => {
    const matchesSearch = !searchTerm || 
      transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transaction.category?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = !categoryFilter || transaction.category === categoryFilter;
    
    const matchesDate = !dateFilter || 
      new Date(transaction.date).toDateString() === new Date(dateFilter).toDateString();
    
    const matchesMember = !memberFilter || transaction.member_name === memberFilter;
    
    return matchesSearch && matchesCategory && matchesDate && matchesMember;
  });

  // Get all categories
  const categories = [...new Set(transactions.map(t => t.category).filter(Boolean))];
  
  // Get all members
  const members = [...new Set(transactions.map(t => t.member_name).filter(Boolean))];

  // Format amount
  const formatAmount = (amount: any) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'CNY'
    }).format(amount);
  };

  // Format date
  const formatDate = (dateString: any) => {
    return new Date(dateString).toLocaleDateString('en-US');
  };

  // Get category color
  const getCategoryColor = (category: any) => {
    const colors = {
      'Dining': '#ff4d4f',
      'Transport': '#1890ff',
      'Shopping': '#52c41a',
      'Entertainment': '#722ed1',
      'Healthcare': '#fa8c16',
      'Education': '#13c2c2',
      'Housing': '#eb2f96',
      'Others': '#666'
    };
    return colors[category as keyof typeof colors] || '#666';
  };

  if (!user || !currentGroup) {
    return null;
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Navbar />
      
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
        {/* Header */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '24px' 
        }}>
          <div>
            <button
              onClick={() => router.push(`/groups/${groupId}`)}
              style={{
                padding: '8px 16px',
                border: '1px solid #d9d9d9',
                background: '#fff',
                color: '#666',
                borderRadius: '6px',
                cursor: 'pointer',
                marginBottom: '12px'
              }}
            >
              ← Back to Group Details
            </button>
            <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#222', margin: 0 }}>
              {currentGroup.group_name} - Transaction Records
            </h1>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => router.push(`/groups/${groupId}/share`)}
              style={{
                padding: '10px 20px',
                border: 'none',
                background: '#111',
                color: '#fff',
                borderRadius: '6px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Share Transactions
            </button>
            <button
              onClick={() => router.push(`/groups/${groupId}/add-transaction`)}
              style={{
                padding: '10px 20px',
                border: '1px solid #52c41a',
                background: '#fff',
                color: '#52c41a',
                borderRadius: '6px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Add Transaction
            </button>
          </div>
        </div>

        {/* Filters */}
        <div style={{ 
          background: '#fff', 
          borderRadius: '8px', 
          padding: '20px', 
          marginBottom: '24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', fontSize: '14px' }}>
                Search
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search transaction description or category..."
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d9d9d9',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', fontSize: '14px' }}>
                Category
              </label>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d9d9d9',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', fontSize: '14px' }}>
                Date
              </label>
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d9d9d9',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', fontSize: '14px' }}>
                Member
              </label>
              <select
                value={memberFilter}
                onChange={(e) => setMemberFilter(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d9d9d9',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                <option value="">All Members</option>
                {members.map(member => (
                  <option key={member} value={member}>{member}</option>
                ))}
              </select>
            </div>
          </div>
          <div style={{ marginTop: '16px', display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button
              onClick={() => {
                setSearchTerm('');
                setCategoryFilter('');
                setDateFilter('');
                setMemberFilter('');
              }}
              style={{
                padding: '8px 16px',
                border: '1px solid #d9d9d9',
                background: '#fff',
                color: '#666',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Transaction list */}
        <div style={{ 
          background: '#fff', 
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ 
            padding: '20px', 
            borderBottom: '1px solid #f0f0f0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
              Transaction Records ({filteredTransactions.length})
            </h3>
            <div style={{ fontSize: '14px', color: '#666' }}>
              Total Amount: {formatAmount(filteredTransactions.reduce((sum, t) => sum + (t.amount || 0), 0))}
            </div>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ fontSize: '16px', color: '#666' }}>Loading...</div>
            </div>
          ) : filteredTransactions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
              <h3 style={{ fontSize: '20px', color: '#222', marginBottom: '8px' }}>
                No transaction records
              </h3>
              <p style={{ color: '#666', marginBottom: '24px' }}>
                Start sharing transactions or add new transactions to view group financial status
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button
                  onClick={() => router.push(`/groups/${groupId}/share`)}
                  style={{
                    padding: '10px 20px',
                    border: 'none',
                    background: '#111',
                    color: '#fff',
                    borderRadius: '6px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Share Transactions
                </button>
                <button
                  onClick={() => router.push(`/groups/${groupId}/add-transaction`)}
                  style={{
                    padding: '10px 20px',
                    border: '1px solid #52c41a',
                    background: '#fff',
                    color: '#52c41a',
                    borderRadius: '6px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Add Transaction
                </button>
              </div>
            </div>
          ) : (
            <div>
              {filteredTransactions.map((transaction, index) => (
                <div
                  key={transaction.id || index}
                  style={{
                    padding: '16px 20px',
                    borderBottom: index < filteredTransactions.length - 1 ? '1px solid #f0f0f0' : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px'
                  }}
                >
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: getCategoryColor(transaction.category),
                    color: '#fff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: '600',
                    fontSize: '14px'
                  }}>
                    {transaction.category?.[0] || '💰'}
                  </div>
                  
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: '600', color: '#222', marginBottom: '4px' }}>
                      {transaction.description}
                    </div>
                    <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#666' }}>
                      <span>{transaction.category}</span>
                      <span>{formatDate(transaction.date)}</span>
                      <span>by {transaction.member_name || 'Unknown User'}</span>
                    </div>
                  </div>
                  
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ 
                      fontSize: '16px', 
                      fontWeight: '600',
                      color: transaction.amount > 0 ? '#ff4d4f' : '#52c41a'
                    }}>
                      {transaction.amount > 0 ? '+' : ''}{formatAmount(transaction.amount)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
