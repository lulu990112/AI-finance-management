'use client';
import React, { useState, useEffect } from 'react';
import { useGroup } from '../context/GroupContext';
import { useAuth } from '../components/AuthContext';
import { useRouter } from 'next/navigation';
import Navbar from '../components/Navbar';
import { toast } from 'react-toastify';

export default function GroupsPage() {
  const { groups, loading, fetchGroups, joinGroup } = useGroup();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [joinGroupId, setJoinGroupId] = useState('');
  const [createForm, setCreateForm] = useState({
    group_name: '',
    description: '',
    max_members: 10
  });

  // 通用样式对象
  const styles = {
    button: {
      padding: '10px 20px',
      borderRadius: '6px',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.2s'
    },
    primaryButton: {
      padding: '10px 20px',
      border: 'none',
      background: '#111',
      color: '#fff',
      borderRadius: '6px',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.2s'
    },
    secondaryButton: {
      padding: '10px 20px',
      border: '1px solid #111',
      background: '#fff',
      color: '#111',
      borderRadius: '6px',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.2s'
    },
    modalButton: {
      padding: '10px 20px',
      border: '1px solid #d9d9d9',
      background: '#fff',
      color: '#666',
      borderRadius: '6px',
      cursor: 'pointer'
    },
    input: {
      width: '100%',
      padding: '10px',
      border: '1px solid #d9d9d9',
      borderRadius: '6px',
      fontSize: '14px'
    }
  };

  useEffect(() => {
    if (authLoading) return; // 等待 user 恢复
    if (!user) {
      router.push('/login');
      return;
    }
    fetchGroups();
  }, [user, authLoading]);

  const handleCreateGroup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await createGroup(createForm);
      setShowCreateModal(false);
      setCreateForm({ group_name: '', description: '', max_members: 10 });
      await fetchGroups(); // 创建组成功后刷新组列表
    } catch (error) {
      console.error('Failed to create group:', error);
    }
  };

  const handleJoinGroup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!joinGroupId.trim()) {
      toast.error('Please enter a group ID');
      return;
    }
    try {
      await joinGroup(parseInt(joinGroupId));
      setShowJoinModal(false);
      setJoinGroupId('');
    } catch (error) {
      console.error('Failed to join group:', error);
    }
  };

  const { createGroup } = useGroup();

  if (!user) {
    return null;
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Navbar />
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px'
        }}>
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#222' }}>
            My Groups
          </h1>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => setShowJoinModal(true)}
              style={styles.secondaryButton}
            >
              Join Group
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              style={styles.primaryButton}
            >
              Create Group
            </button>
          </div>
        </div>

        {/* 组列表渲染 */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '16px', color: '#666' }}>Loading...</div>
          </div>
        ) : (Array.isArray(groups) && groups.length > 0) ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: '20px'
          }}>
            {groups.map((group: any) => (
              <div
                key={group.id}
                style={{
                  background: '#fff',
                  borderRadius: '8px',
                  padding: '20px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  border: '1px solid #f0f0f0'
                }}
                onClick={() => router.push(`/groups/${group.id}`)}
                onMouseEnter={(e: React.MouseEvent<HTMLDivElement>) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                }}
                onMouseLeave={(e: React.MouseEvent<HTMLDivElement>) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
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
                    fontSize: '16px',
                    marginRight: '12px'
                  }}>
                    {group.group_name?.[0]?.toUpperCase() || 'G'}
                  </div>
                  <div>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#222', margin: 0 }}>
                      {group.group_name}
                    </h3>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      ID: {group.id}
                    </div>
                  </div>
                </div>
                <p style={{
                  color: '#666',
                  fontSize: '14px',
                  marginBottom: '16px',
                  lineHeight: '1.5'
                }}>
                  {group.description || 'No description'}
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <span style={{
                      padding: '4px 8px',
                      background: group.role === 'admin' ? '#ff4d4f' : '#52c41a',
                      color: '#fff',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}>
                      {group.role === 'admin' ? 'Admin' : 'Member'}
                    </span>
                    <span style={{ fontSize: '12px', color: '#666' }}>
                      {group.member_count || 0}/{group.max_members || 10} members
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: '#999' }}>
                    Click to view details →
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            background: '#fff',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>👥</div>
            <h3 style={{ fontSize: '20px', color: '#222', marginBottom: '8px' }}>
              Haven't joined any groups yet
            </h3>
            <p style={{ color: '#666', marginBottom: '24px' }}>
              Create or join a group to start team financial management
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                onClick={() => setShowJoinModal(true)}
                style={styles.secondaryButton}
              >
                Join Group
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                style={styles.primaryButton}
              >
                Create Group
              </button>
            </div>
          </div>
        )}
      </div>
      {/* 创建组模态框 */}
      {showCreateModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#fff',
            borderRadius: '8px',
            padding: '24px',
            width: '400px',
            maxWidth: '90vw'
          }}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px' }}>
              Create New Group
            </h3>
            <form onSubmit={handleCreateGroup}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Group Name *
                </label>
                <input
                  type="text"
                  value={createForm.group_name}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCreateForm({...createForm, group_name: e.target.value})}
                  required
                  style={styles.input}
                  placeholder="Enter group name"
                />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Description
                </label>
                <textarea
                  value={createForm.description}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCreateForm({...createForm, description: e.target.value})}
                  style={{
                    ...styles.input,
                    minHeight: '80px',
                    resize: 'vertical'
                  }}
                  placeholder="Enter group description"
                />
              </div>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Max Members
                </label>
                <input
                  type="number"
                  value={createForm.max_members}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCreateForm({...createForm, max_members: parseInt(e.target.value)})}
                  min="2"
                  max="50"
                  style={styles.input}
                />
              </div>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  style={styles.modalButton}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={styles.primaryButton}
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 加入组模态框 */}
      {showJoinModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#fff',
            borderRadius: '8px',
            padding: '24px',
            width: '400px',
            maxWidth: '90vw'
          }}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px' }}>
              Join Group
            </h3>
            <form onSubmit={handleJoinGroup}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                  Group ID *
                </label>
                <input
                  type="number"
                  value={joinGroupId}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setJoinGroupId(e.target.value)}
                  required
                  style={styles.input}
                  placeholder="Enter group ID"
                />
              </div>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowJoinModal(false)}
                  style={styles.modalButton}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={styles.primaryButton}
                >
                  Join
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
