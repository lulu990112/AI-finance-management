'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as loginAPI } from '../services/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check locally stored user info and token when page loads
  useEffect(() => {
   
    const savedUser = localStorage.getItem('user');
    const savedToken = localStorage.getItem('authToken');
    
    if (savedUser && savedToken) {
      setUser(JSON.parse(savedUser));
    } else {
      // If no token, clear user info
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
      
      // Check Gmail authorization status and handle authorization
      const checkAndHandleGmailAuth = async () => {
        try {
          console.log('Checking Gmail authorization status...');
          console.log('Token status after login:', localStorage.getItem('authToken') ? 'Exists' : 'Not exists');
          
          // Get Gmail authorization status
          const response = await fetch('http://localhost:8000/api/gmail/auth_status/', {
            headers: {
              'Authorization': `Bearer ${userData.token}`
            }
          });
          
          if (response.ok) {
            const authStatus = await response.json();
            console.log('Gmail authorization status:', authStatus);
            
            // For testing purposes, always open authorization page
            // If Gmail is already authorized, re-authorize to ensure testing
            console.log('For testing, forcing Gmail authorization URL...');
            
            // Get authorization URL
            const authUrlResponse = await fetch('http://localhost:8000/api/gmail/auth_url/', {
              headers: {
                'Authorization': `Bearer ${userData.token}`
              }
            });
            
            const authUrlData = await authUrlResponse.json();
            
            if (authUrlData.auth_url) {
              console.log('Got Gmail authorization URL, preparing to open new window...');
              console.log('Token status before opening authorization window:', localStorage.getItem('authToken') ? 'Exists' : 'Not exists');
              
              // Start monitoring Gmail authorization process
              if (window.monitorGmailAuth) {
                window.monitorGmailAuth();
              }
              
              window.open(authUrlData.auth_url, '_blank', 'width=500,height=700');
            }
          } else {
            console.error('Failed to get Gmail authorization status:', response.status);
          }
        } catch (error) {
          console.error('Gmail authorization check failed:', error);
        }
      };
      
      // Execute Gmail authorization check
      checkAndHandleGmailAuth();
      
      return userData;
    } catch (error) {
      console.error('Login failed:', error);
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