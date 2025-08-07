'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as loginAPI } from '../services/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 页面加载时检查本地存储的用户信息和token
    const savedUser = localStorage.getItem('user');
    const savedToken = localStorage.getItem('authToken');
    
    if (savedUser && savedToken) {
      setUser(JSON.parse(savedUser));
    } else {
      // 如果没有token，清除用户信息
      localStorage.removeItem('user');
      localStorage.removeItem('authToken');
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const userData = await loginAPI(username, password);
      setUser(userData.user);
      localStorage.setItem('user', JSON.stringify(userData.user));
      
      // 检查Gmail授权状态并处理授权
      const checkAndHandleGmailAuth = async () => {
        try {
          console.log('🔍 检查Gmail授权状态...');
          console.log('🔍 登录后Token状态:', localStorage.getItem('authToken') ? '存在' : '不存在');
          
          // 获取Gmail授权状态
          const response = await fetch('http://localhost:8000/api/gmail/auth_status/', {
            headers: {
              'Authorization': `Bearer ${userData.token}`
            }
          });
          
          if (response.ok) {
            const authStatus = await response.json();
            console.log('🔍 Gmail授权状态:', authStatus);
            
            // 为了测试目的，暂时总是打开授权页面
            // 如果Gmail已授权，也重新授权以确保测试
            console.log('🔍 为了测试，强制获取Gmail授权URL...');
            
            // 获取授权URL
            const authUrlResponse = await fetch('http://localhost:8000/api/gmail/auth_url/', {
              headers: {
                'Authorization': `Bearer ${userData.token}`
              }
            });
            
            const authUrlData = await authUrlResponse.json();
            
            if (authUrlData.auth_url) {
              console.log('🔍 获取到Gmail授权URL，准备打开新窗口...');
              console.log('🔍 打开授权窗口前Token状态:', localStorage.getItem('authToken') ? '存在' : '不存在');
              
              // 开始监控Gmail授权过程
              if (window.monitorGmailAuth) {
                window.monitorGmailAuth();
              }
              
              window.open(authUrlData.auth_url, '_blank', 'width=500,height=700');
            }
          } else {
            console.error('获取Gmail授权状态失败:', response.status);
          }
        } catch (error) {
          console.error('Gmail授权检查失败:', error);
        }
      };
      
      // 执行Gmail授权检查
      checkAndHandleGmailAuth();
      
      return userData;
    } catch (error) {
      console.error('登录失败:', error);
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('authToken');
  };

  const value = {
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 