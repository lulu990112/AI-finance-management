'use client';
import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useGroup } from '../../../context/GroupContext';
import { useAuth } from '../../../components/AuthContext';
import { getAllTransactions } from '../../../services/api';
import Navbar from '../../../components/Navbar';
import { toast } from 'react-toastify';

export default function ShareTransactionsPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { currentGroup, getGroupInfo, shareTransactions } = useGroup();
  
  const [personalTransactions, setPersonalTransactions] = useState<any[]>([]);
  const [selectedTransactions, setSelectedTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');

  const groupId = parseInt(Array.isArray(params.id) ? params.id[0] || '0' : params.id || '0');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    if (groupId) {
      loadGroupInfo();
      loadPersonalTransactions();
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

  const loadPersonalTransactions = async () => {
    setLoading(true);
    try {
      const response = await getAllTransactions();
      setPersonalTransactions(response.data || response || []);
    } catch (error) {
      console.error('Failed to load personal transactions:', error);
      toast.error('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  // 筛选交易
  const filteredTransactions = personalTransactions.filter(transaction => {
    const matchesSearch = !searchTerm || 
      transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transaction.category?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = !categoryFilter || transaction.category === categoryFilter;
    
    // 修复日期筛选逻辑
    const matchesDate = !dateFilter || (() => {
      try {
        // 使用正确的字段名：transaction_date
        const transactionDate = transaction.transaction_date || transaction.date;
        if (!transactionDate) return false;
        
        // 将日期转换为 YYYY-MM-DD 格式进行比较
        const transactionDateStr = new Date(transactionDate).toISOString().split('T')[0];
        const filterDateStr = dateFilter;
        
        return transactionDateStr === filterDateStr;
      } catch (error) {
        console.error('Date filter error:', error);
        return false;
      }
    })();
    
    return matchesSearch && matchesCategory && matchesDate;
  });

  // 获取所有分类
  const categories = [...new Set(personalTransactions.map(t => t.category).filter(Boolean))];

  // 处理交易选择
  const handleTransactionSelect = (transactionId: any) => {
    setSelectedTransactions(prev => {
      if (prev.includes(transactionId)) {
        return prev.filter(id => id !== transactionId);
      } else {
        return [...prev, transactionId];
      }
    });
  };

  // 全选/取消全选
  const handleSelectAll = () => {
    if (selectedTransactions.length === filteredTransactions.length) {
      setSelectedTransactions([]);
    } else {
      setSelectedTransactions(filteredTransactions.map(t => t.id));
    }
  };

  // 共享选中的交易
  const handleShareTransactions = async () => {
    if (selectedTransactions.length === 0) {
      toast.error('Please select transactions to share');
      return;
    }

    try {
      await shareTransactions({
        group_ids: [groupId],
        transaction_ids: selectedTransactions
      });
      
      toast.success(`Successfully shared ${selectedTransactions.length} transactions`);
      setSelectedTransactions([]);
      router.push(`/groups/${groupId}/transactions`);
    } catch (error) {
      console.error('Failed to share transactions:', error);
      toast.error('Failed to share transactions');
    }
  };

  // 格式化金额
  const formatAmount = (amount: any) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'CNY'
    }).format(amount);
  };

  // 格式化日期，模仿RecentTransactions组件
  const formatDate = (dateString: any) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '';
    return date.toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' });
  };

  // 获取分类颜色
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
              onClick={() => router.push(`/groups/${groupId}/transactions`)}
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
              ← Back to Transaction List
            </button>
            <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#222', margin: 0 }}>
              Share Transactions to {currentGroup.group_name}
            </h1>
          </div>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <div style={{ fontSize: '14px', color: '#666' }}>
              {selectedTransactions.length} transactions selected
            </div>
            <button
              onClick={handleShareTransactions}
              disabled={selectedTransactions.length === 0}
              style={{
                padding: '10px 20px',
                border: 'none',
                background: selectedTransactions.length > 0 ? '#111' : '#d9d9d9',
                color: '#fff',
                borderRadius: '6px',
                fontWeight: '600',
                cursor: selectedTransactions.length > 0 ? 'pointer' : 'not-allowed'
              }}
            >
              Share Selected Transactions
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
          </div>
          <div style={{ marginTop: '16px', display: 'flex', gap: '12px', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              onClick={handleSelectAll}
              style={{
                padding: '8px 16px',
                border: '1px solid #1890ff',
                background: '#fff',
                color: '#1890ff',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              {selectedTransactions.length === filteredTransactions.length ? 'Deselect All' : 'Select All'}
            </button>
            <button
              onClick={() => {
                setSearchTerm('');
                setCategoryFilter('');
                setDateFilter('');
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
            borderBottom: '1px solid #f0f0f0'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>
              Personal Transaction Records ({filteredTransactions.length})
            </h3>
            <p style={{ fontSize: '14px', color: '#666', margin: '8px 0 0 0' }}>
              Select transactions to share to the group
            </p>
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
                Add some personal transaction records first, then you can share them to the group
              </p>
                          <button
              onClick={() => router.push('/category-list')}
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
              Add Transaction
            </button>
            </div>
          ) : (
            <div>
              {filteredTransactions.map((transaction, index) => (
                <div
                  key={transaction.id}
                  style={{
                    padding: '16px 20px',
                    borderBottom: index < filteredTransactions.length - 1 ? '1px solid #f0f0f0' : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    background: selectedTransactions.includes(transaction.id) ? '#f0f8ff' : 'transparent'
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedTransactions.includes(transaction.id)}
                    onChange={() => handleTransactionSelect(transaction.id)}
                    style={{
                      width: '18px',
                      height: '18px',
                      cursor: 'pointer'
                    }}
                  />
                  
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
                      <span>{formatDate(transaction.transaction_date || transaction.date || transaction.created_at)}</span>
                      <span>{transaction.subcategory}</span>
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
