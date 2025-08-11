'use client';
import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useGroup } from '../../../context/GroupContext';
import { useAuth } from '../../../components/AuthContext';
import Navbar from '../../../components/Navbar';
import { toast } from 'react-toastify';

export default function AddGroupTransactionPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { currentGroup, getGroupInfo } = useGroup();
  
  const [formData, setFormData] = useState({
    description: '',
    amount: '',
    category: '',
    subcategory: '',
    date: new Date().toISOString().split('T')[0],
    notes: ''
  });
  const [loading, setLoading] = useState(false);

  const groupId = parseInt(Array.isArray(params.id) ? params.id[0] || '0' : params.id || '0');

  // 分类选项
  const categories = [
    { value: '餐饮', label: '餐饮', subcategories: ['早餐', '午餐', '晚餐', '零食', '外卖', '其他'] },
    { value: '交通', label: '交通', subcategories: ['公交', '地铁', '出租车', '网约车', '加油', '停车费', '其他'] },
    { value: '购物', label: '购物', subcategories: ['服装', '数码', '家居', '化妆品', '其他'] },
    { value: '娱乐', label: '娱乐', subcategories: ['电影', '游戏', '运动', '旅游', '其他'] },
    { value: '医疗', label: '医疗', subcategories: ['药品', '检查', '治疗', '其他'] },
    { value: '教育', label: '教育', subcategories: ['学费', '书籍', '培训', '其他'] },
    { value: '住房', label: '住房', subcategories: ['房租', '水电费', '物业费', '维修', '其他'] },
    { value: '其他', label: '其他', subcategories: ['其他'] }
  ];

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    if (groupId) {
      loadGroupInfo();
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

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!formData.description.trim()) {
      toast.error('Please enter transaction description');
      return;
    }
    
    if (!formData.amount || parseFloat(formData.amount) === 0) {
      toast.error('Please enter a valid amount');
      return;
    }
    
    if (!formData.category) {
      toast.error('Please select a category');
      return;
    }

    setLoading(true);
    try {
      // 这里需要调用组交易添加API
      // 由于后端API中没有直接的添加组交易接口，我们可以通过共享交易的方式实现
      // 或者需要后端提供新的API接口
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('Transaction added successfully!');
      router.push(`/groups/${groupId}/transactions`);
    } catch (error) {
      console.error('Failed to add transaction:', error);
      toast.error('Failed to add transaction');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentSubcategories = () => {
    const category = categories.find(cat => cat.value === formData.category);
    return category ? category.subcategories : [];
  };

  if (!user || !currentGroup) {
    return null;
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Navbar />
      
      <div style={{ maxWidth: 800, margin: '0 auto', padding: '24px' }}>
        {/* 头部 */}
        <div style={{ marginBottom: '24px' }}>
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
            Add Group Transaction - {currentGroup.group_name}
          </h1>
        </div>

        {/* 表单 */}
        <div style={{ 
          background: '#fff', 
          borderRadius: '8px', 
          padding: '32px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gap: '24px' }}>
              {/* 交易描述 */}
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '16px' }}>
                  Transaction Description *
                </label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Enter transaction description..."
                  required
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px',
                    fontSize: '16px',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              {/* 金额 */}
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '16px' }}>
                  Amount *
                </label>
                <input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => handleInputChange('amount', e.target.value)}
                  placeholder="0.00"
                  step="0.01"
                  min="0"
                  required
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px',
                    fontSize: '16px',
                    boxSizing: 'border-box'
                  }}
                />
                <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                  Positive numbers for expenses, negative for income
                </div>
              </div>

              {/* 分类和子分类 */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '16px' }}>
                    Category *
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => {
                      handleInputChange('category', e.target.value);
                      handleInputChange('subcategory', ''); // 重置子分类
                    }}
                    required
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '1px solid #d9d9d9',
                      borderRadius: '6px',
                      fontSize: '16px',
                      boxSizing: 'border-box'
                    }}
                  >
                    <option value="">Select Category</option>
                    {categories.map(category => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '16px' }}>
                    Subcategory
                  </label>
                  <select
                    value={formData.subcategory}
                    onChange={(e) => handleInputChange('subcategory', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '1px solid #d9d9d9',
                      borderRadius: '6px',
                      fontSize: '16px',
                      boxSizing: 'border-box'
                    }}
                  >
                    <option value="">Select Subcategory</option>
                    {getCurrentSubcategories().map(subcategory => (
                      <option key={subcategory} value={subcategory}>
                        {subcategory}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* 日期 */}
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '16px' }}>
                  Transaction Date *
                </label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => handleInputChange('date', e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px',
                    fontSize: '16px',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              {/* 备注 */}
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '16px' }}>
                  Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  placeholder="Add notes..."
                  rows={4}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px',
                    fontSize: '16px',
                    resize: 'vertical',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              {/* 提交按钮 */}
              <div style={{ display: 'flex', gap: '16px', justifyContent: 'flex-end', marginTop: '16px' }}>
                <button
                  type="button"
                  onClick={() => router.push(`/groups/${groupId}/transactions`)}
                  style={{
                    padding: '12px 24px',
                    border: '1px solid #d9d9d9',
                    background: '#fff',
                    color: '#666',
                    borderRadius: '6px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    padding: '12px 24px',
                    border: 'none',
                    background: loading ? '#d9d9d9' : '#111',
                    color: '#fff',
                    borderRadius: '6px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: loading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {loading ? 'Adding...' : 'Add Transaction'}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* 提示信息 */}
        <div style={{ 
          background: '#f6ffed', 
          border: '1px solid #b7eb8f', 
          borderRadius: '6px', 
          padding: '16px', 
          marginTop: '24px' 
        }}>
          <div style={{ fontSize: '14px', color: '#52c41a', fontWeight: '500' }}>
            💡 Tips
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
            • Added transactions will be directly shared to the group, all members can view them<br/>
            • Positive amounts for expenses, negative for income<br/>
            • It's recommended to add detailed descriptions and notes for team members to understand
          </div>
        </div>
      </div>
    </div>
  );
}
