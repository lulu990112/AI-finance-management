"use client";
import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  getRecentTransactions, 
  getCategoryData, 
  getTransactionsByCategory,
  getAllTransactions 
} from '../services/api';

const DataContext = createContext();

export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

export const DataProvider = ({ children }) => {
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [allTransactions, setAllTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取最新交易
  const fetchRecentTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRecentTransactions();
      setRecentTransactions(data);
    } catch (err) {
      if (err.message.includes('认证失败')) {
        // 在登录页面不显示认证错误，也不重定向
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          setError('认证失败，请重新登录');
          window.location.href = '/login';
        }
      } else {
        setError('获取最新交易失败');
      }
      console.error('获取最新交易错误:', err);
    } finally {
      setLoading(false);
    }
  };

  // 获取分类数据
  const fetchCategoryData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCategoryData();
      setCategoryData(data);
    } catch (err) {
      if (err.message.includes('认证失败')) {
        // 在登录页面不显示认证错误，也不重定向
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          setError('认证失败，请重新登录');
          window.location.href = '/login';
        }
      } else {
        setError('获取分类数据失败');
      }
      console.error('获取分类数据错误:', err);
    } finally {
      setLoading(false);
    }
  };

  // 获取所有交易
  const fetchAllTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAllTransactions();
      setAllTransactions(data);
    } catch (err) {
      if (err.message.includes('认证失败')) {
        // 在登录页面不显示认证错误，也不重定向
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          setError('认证失败，请重新登录');
          window.location.href = '/login';
        }
      } else {
        setError('获取所有交易失败');
      }
      console.error('获取所有交易错误:', err);
    } finally {
      setLoading(false);
    }
  };

  // 获取特定分类的交易
  const fetchTransactionsByCategory = async (category) => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTransactionsByCategory(category);
      return data;
    } catch (err) {
      setError(`获取${category}分类交易失败`);
      console.error('获取分类交易错误:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // 刷新所有数据
  const refreshAllData = async () => {
    await Promise.all([
      fetchRecentTransactions(),
      fetchCategoryData(),
      fetchAllTransactions()
    ]);
  };

  // 初始化数据
  useEffect(() => {
    // 检查是否有认证token，如果没有则不获取数据
    const token = localStorage.getItem('authToken');
    const currentPath = typeof window !== 'undefined' ? window.location.pathname : '';
    
    // 只有在有token且不在登录页面时才获取数据
    if (token && !currentPath.includes('/login')) {
      refreshAllData();
    }
  }, []);

  const value = {
    recentTransactions,
    categoryData,
    allTransactions,
    loading,
    error,
    fetchRecentTransactions,
    fetchCategoryData,
    fetchAllTransactions,
    fetchTransactionsByCategory,
    refreshAllData,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
}; 