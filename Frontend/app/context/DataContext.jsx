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

  // Get recent transactions
  const fetchRecentTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRecentTransactions();
      setRecentTransactions(data);
    } catch (err) {
      if (err.message.includes('Authentication failed')) {
        // Don't show authentication errors on login page, and don't redirect
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          setError('Authentication failed, please login again');
          window.location.href = '/login';
        }
      } else {
        setError('Failed to get recent transactions');
      }
      console.error('Failed to get recent transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get category data
  const fetchCategoryData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCategoryData();
      setCategoryData(data);
    } catch (err) {
      if (err.message.includes('Authentication failed')) {
        // Don't show authentication errors on login page, and don't redirect
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          setError('Authentication failed, please login again');
          window.location.href = '/login';
        }
      } else {
        setError('Failed to get category data');
      }
      console.error('Failed to get category data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get all transactions
  const fetchAllTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAllTransactions();
      setAllTransactions(data);
    } catch (err) {
      if (err.message.includes('Authentication failed')) {
        // Don't show authentication errors on login page, and don't redirect
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          setError('Authentication failed, please login again');
          window.location.href = '/login';
        }
      } else {
        setError('Failed to get all transactions');
      }
      console.error('Failed to get all transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get transactions of specific category
  const fetchTransactionsByCategory = async (category) => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTransactionsByCategory(category);
      return data;
    } catch (err) {
      setError(`Failed to get ${category} category transactions`);
      console.error('Failed to get category transactions:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Refresh all data
  const refreshAllData = async () => {
    await Promise.all([
      fetchRecentTransactions(),
      fetchCategoryData(),
      fetchAllTransactions()
    ]);
  };

  // Initialize data
  useEffect(() => {
    // Check if there is authentication token, don't fetch data if not
    const token = localStorage.getItem('authToken');
    const currentPath = typeof window !== 'undefined' ? window.location.pathname : '';
    
    // Only fetch data when there is token and not on login page
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