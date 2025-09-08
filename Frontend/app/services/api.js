// API basic configuration
const API_BASE_URL = 'http://localhost:8000';

// Get stored token
const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('authToken');
    console.log('Get Token:', token ? `${token.substring(0, 20)}...` : 'null');
    return token;
  }
  return null;
};

// Store token
const setAuthToken = (token) => {
  if (typeof window !== 'undefined') {
    console.log('Store Token:', token ? `${token.substring(0, 20)}...` : 'null');
    localStorage.setItem('authToken', token);
  }
};

// Clear token
const clearAuthToken = () => {
  if (typeof window !== 'undefined') {
    console.log('Clear Token');
    localStorage.removeItem('authToken');
  }
};

// Common API request function
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();
  
  console.log(`API request: ${endpoint}`);
  console.log(`Using Token:`, token ? 'Yes' : 'No');
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    ...options,
  };

  // If there is a body parameter, it needs to be JSON serialized
  if (options.body && typeof options.body === 'object') {
    defaultOptions.body = JSON.stringify(options.body);
  } else if (options.body) {
    defaultOptions.body = options.body;
  }

  try {
    const response = await fetch(url, defaultOptions);
    
    console.log(`Response status: ${response.status} ${response.statusText}`);
    
    if (response.status === 401) {
      // Token expired or invalid, clear token and throw error
      console.log('Authentication failed, clear Token');
      clearAuthToken();
      throw new Error('Authentication failed, please login again');
    }
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

// Login API
export const login = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/api/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  // Priority parse backend returned JSON to extract clear error message
  let data;
  try {
    data = await response.json();
  } catch (e) {
    data = null;
  }

  if (!response.ok) {
    const serverMessage = (data && (data.message || data.detail || data.error)) ||
      (response.status === 401 ? 'Username or password is incorrect.' : undefined);
    throw new Error(serverMessage || `Login failed (${response.status} ${response.statusText})`);
  }

  if (data && data.success && data.data && data.data.token) {
    setAuthToken(data.data.token);
    return data.data;
  } else {
    throw new Error((data && data.message) || 'Login failed');
  }
};

// Sync Gmail receipts
export const syncGmailReceipts = async () => {
  console.log(' Start Gmail sync...');
  console.log(' Token status before sync:', getAuthToken() ? 'Exists' : 'Not exists');
  
  const result = await apiRequest('/api/gpt/batch_sync_and_process/', {
    method: 'POST',
  });
  
  console.log('Gmail sync completed');
  console.log('Token status after sync:', getAuthToken() ? 'Exists' : 'Not exists');
  
  return result;
};

// Get all transactions
export const getAllTransactions = async () => {
  try {
    console.log('Start fetching all transaction data...');
    
    // First get the first page of data to understand the total
    const firstPageResponse = await apiRequest('/api/gpt/transactions/?page=1&page_size=20');
    
    if (!firstPageResponse || !firstPageResponse.transactions) {
      console.error('Failed to get first page data');
      return [];
    }
    
    const total = firstPageResponse.total || 0;
    const pageSize = 20; // Backend default page size
    const totalPages = Math.ceil(total / pageSize);
    
    console.log(`Total data: ${total}, Total pages: ${totalPages}`);
    
    // If there is only one page of data, return directly
    if (totalPages <= 1) {
      console.log('Only one page of data, return directly');
      return firstPageResponse.transactions;
    }
    
    // Get data from all pages
    const allTransactions = [...firstPageResponse.transactions];
    
    // Parallel get remaining pages of data
    const remainingPages = [];
    for (let page = 2; page <= totalPages; page++) {
      remainingPages.push(
        apiRequest(`/api/gpt/transactions/?page=${page}&page_size=${pageSize}`)
      );
    }
    
    console.log(`Start fetching remaining ${totalPages - 1} pages of data...`);
    const remainingResponses = await Promise.all(remainingPages);
    
    // Merge all data
    remainingResponses.forEach((response, index) => {
      if (response && response.transactions) {
        allTransactions.push(...response.transactions);
        console.log(`Page ${index + 2} data: ${response.transactions.length} items`);
      }
    });
    
    console.log(`Successfully fetched all data: ${allTransactions.length} items`);
    
    // Sort by transaction date in descending order to ensure the latest is in front
    allTransactions.sort((a, b) => {
      const dateA = new Date(a.transaction_date);
      const dateB = new Date(b.transaction_date);
      return dateB - dateA;
    });
    
    console.log('Data sorted by date in descending order');
    return allTransactions;
    
  } catch (error) {
    console.error('Failed to get all transaction data:', error);
    return [];
  }
};

// Get category data
export const getCategoryData = async () => {
  return apiRequest('/api/gpt/categories/');
};

// Get detailed data of specific category (frontend data processing)
export const getCategoryDetail = async (categoryName) => {
  try {
    // Parallel get all transactions and category structure
    const [allTransactions, categoryStructure] = await Promise.all([
      getAllTransactions(),
      getCategoryData()
    ]);

    console.log('Got transaction data:', allTransactions.length, 'items');
    console.log('Got category structure:', categoryStructure);

    // Find target category
    const targetCategory = categoryStructure.categories.find(cat => 
      cat.name === categoryName
    );

    if (!targetCategory) {
      console.error('Category not found:', categoryName);
      return null;
    }

    // Filter transactions of this category
    const categoryTransactions = allTransactions.filter(tx => {
      // Handle cases where category field may be object or string
      const txCategory = typeof tx.category === 'object' ? tx.category.name : tx.category;
      return txCategory === categoryName;
    });

    console.log('Filtered category transactions:', categoryTransactions.length, 'items');

    // Calculate total amount of this category
    const totalAmount = categoryTransactions.reduce((sum, tx) => {
      return sum + parseFloat(tx.amount || 0);
    }, 0);

    // Group and summarize by subcategory
    const subcategoryMap = {};
    categoryTransactions.forEach(tx => {
      // Handle cases where subcategory field may be object or string
      const subcategoryName = typeof tx.subcategory === 'object' ? tx.subcategory.name : tx.subcategory;
      if (!subcategoryMap[subcategoryName]) {
        subcategoryMap[subcategoryName] = {
          amount: 0,
          transactions: [],
          color: null
        };
      }
      subcategoryMap[subcategoryName].amount += parseFloat(tx.amount || 0);
      subcategoryMap[subcategoryName].transactions.push(tx);
    });

    // Convert to subcategory array
    const subcategories = Object.entries(subcategoryMap).map(([name, data]) => ({
      name,
      value: data.amount,
      color: getDefaultSubcategoryColor(name),
      transactions: data.transactions
    }));

    // Format transaction records
    const formattedTransactions = categoryTransactions.map(tx => ({
      id: tx.id,
      date: formatDate(tx.transaction_date),
      subcategory: typeof tx.subcategory === 'object' ? tx.subcategory.name : tx.subcategory,
      amount: parseFloat(tx.amount || 0),
      note: tx.note || tx.item_name || 'No note'
    }));

    // Sort by date (latest first)
    formattedTransactions.sort((a, b) => new Date(b.date) - new Date(a.date));

    return {
      total: totalAmount,  // Use calculated total amount
      subcategories,
      transactions: formattedTransactions
    };

  } catch (error) {
    console.error('Failed to get category details:', error);
    throw error;
  }
};

// Get summary data of all categories (frontend data processing)
export const getCategorySummary = async () => {
  try {
    // Parallel get all transactions and category structure
    const [allTransactions, categoryStructure] = await Promise.all([
      getAllTransactions(),
      getCategoryData()
    ]);
    
    console.log('Got category structure:', categoryStructure);

    // Group by category and calculate total amount
    const categoryTotals = {};
    allTransactions.forEach(tx => {
      const categoryName = typeof tx.category === 'object' ? tx.category.name : tx.category;
      if (!categoryTotals[categoryName]) {
        categoryTotals[categoryName] = 0;
      }
      categoryTotals[categoryName] += parseFloat(tx.amount || 0);
    });

    // Generate category summary data
    const categorySummaries = categoryStructure.categories.map(category => ({
      name: category.name,
      total_amount: categoryTotals[category.name] || 0,  // Use calculated total amount
      color: category.color || getDefaultCategoryColor(category.name),
      transaction_count: 0  // Can be calculated separately if needed
    }));

    console.log('Generated category summary:', categorySummaries);
    return categorySummaries;

  } catch (error) {
    console.error('Failed to get category summary:', error);
    throw error;
  }
};

// Helper function: format date
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown date';
  
  try {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0]; // Return YYYY-MM-DD format
  } catch (error) {
    console.error('Date formatting failed:', dateString);
    return 'Unknown date';
  }
};

// Helper function: get default subcategory color
const getDefaultSubcategoryColor = (subcategoryName) => {
  const colorMap = {
    // Dining category subcategories
    'Snacks': '#ff7ca3',
    'Snack': '#ff7ca3',
    'Meals': '#4ecbff',
    'Drinks': '#ffe08f',
    'Drink': '#ffe08f',
    'Restaurant': '#5adbb5',
    'Daily meal': '#4ecbff',
    'Daily': '#ffe08f',
    
    // Transport category subcategories
    'Bus': '#4ecbff',
    'Subway': '#5adbb5',
    'Taxi': '#a084e8',
    'Train': '#a084e8',
    
    // Shopping category subcategories
    'Clothing': '#ff7ca3',
    'Electronics': '#4ecbff',
    'Cosmetic': '#ff4444',
    'Cosmetics': '#ff4444',
    'Household': '#4ecbff',
    
    // Entertainment category subcategories
    'Movies': '#5adbb5',
    'Movie': '#5adbb5',
    'Games': '#ff7ca3',
    'Game': '#ff7ca3',
    'KTV': '#a084e8',
    
    // Healthcare category subcategories
    'Medicine': '#a084e8',
    'Medical': '#4ecbff'
  };
  
  return colorMap[subcategoryName] || '#666666';
};

// Helper function: get default category color
const getDefaultCategoryColor = (categoryName) => {
  const colorMap = {
    'Dining': '#ff7ca3',
    'Transport': '#4ecbff',
    'Shopping': '#ffe08f',
    'Entertainment': '#5adbb5',
    'Healthcare': '#a084e8'
  };
  
  return colorMap[categoryName] || '#666666';
};

// Get recent transactions (filter the latest 4 from all transactions)
export const getRecentTransactions = async () => {
  const allTransactions = await getAllTransactions();
  
  // Return the latest 4 transactions
  return allTransactions.slice(0, 4);
};

// Get transactions of specific category (filter from all transactions)
export const getTransactionsByCategory = async (category) => {
  const allTransactions = await getAllTransactions();
  
  // Filter transactions by category
  const filteredTransactions = allTransactions.filter(tx => 
    tx.category === category || tx.subcategory === category
  );
  
  // Calculate category statistics
  const totalAmount = filteredTransactions.reduce((sum, tx) => sum + parseFloat(tx.amount || 0), 0);
  
  return {
    total_amount: totalAmount,
    transactions: filteredTransactions,
    subcategories: [] // Return empty array temporarily, can be implemented as needed
  };
};

// Get Gmail authorization status
export const getGmailAuthStatus = async () => {
  return apiRequest('/api/gmail/auth_status/');
};

// Debug function: check token status
export const debugTokenStatus = () => {
  const token = localStorage.getItem('authToken');
  console.log('🔍 === Token Status Check ===');
  console.log('Token exists:', !!token);
  if (token) {
    console.log('Token length:', token.length);
    console.log('Token first 20 chars:', token.substring(0, 20));
    
    // Try to parse JWT token (if possible)
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        console.log('Token expiration time:', new Date(payload.exp * 1000));
        console.log('Current time:', new Date());
        console.log('Is expired:', Date.now() > payload.exp * 1000);
      }
    } catch (e) {
      console.log('Cannot parse JWT token');
    }
  }
  console.log('====================');
  return token;
};

// Expose debug function to global scope
if (typeof window !== 'undefined') {
  window.debugTokenStatus = debugTokenStatus;
  
  // Add Gmail authorization window monitoring
  window.monitorGmailAuth = () => {
    console.log(' === Start monitoring Gmail authorization process ===');
    
    // Check Gmail authorization status
    const checkGmailAuthStatus = async () => {
      try {
        console.log('Checking Gmail authorization status...');
        console.log('Current Token status:', localStorage.getItem('authToken') ? 'Exists' : 'Not exists');
        
        const authStatus = await getGmailAuthStatus();
        console.log('Gmail authorization status:', authStatus);
        
        return authStatus;
      } catch (error) {
        console.error('Failed to get Gmail authorization status:', error);
        return null;
      }
    };
    
    // Check status every 3 seconds
    const interval = setInterval(async () => {
      const authStatus = await checkGmailAuthStatus();
      
      if (authStatus && authStatus.is_authorized) {
        console.log('Gmail authorization successful!');
        console.log(' Authorization details:', authStatus);
        clearInterval(interval);
        
        // Delay to check Token status
        setTimeout(() => {
          console.log('Token status after authorization:', localStorage.getItem('authToken') ? 'Exists' : 'Not exists');
          debugTokenStatus();
        }, 1000);
      } else if (authStatus) {
        console.log('Gmail授权状态:', authStatus.status || '未知');
      }
    }, 3000);
    
    // 60秒后自动停止监控
    setTimeout(() => {
      clearInterval(interval);
      console.log('Gmail授权监控超时');
    }, 60000);
    
    return interval;
  };
  
  // 添加手动监控Gmail同步过程
  window.monitorGmailSync = () => {
    console.log('=== 开始监控Gmail同步过程 ===');
    console.log(' 同步前Token状态:', localStorage.getItem('authToken') ? '存在' : '不存在');
    debugTokenStatus();
    
    // 每5秒检查一次Token状态
    const interval = setInterval(() => {
      console.log(' 检查Token状态变化...');
      debugTokenStatus();
    }, 5000);
    
    // 60秒后自动停止监控
    setTimeout(() => {
      clearInterval(interval);
      console.log(' Gmail同步监控结束');
    }, 60000);
    
    return interval;
  };
  
  // 添加Gmail授权状态检查函数
  window.checkGmailAuthStatus = async () => {
    console.log(' === 检查Gmail授权状态 ===');
    try {
      const authStatus = await getGmailAuthStatus();
      console.log(' Gmail授权状态详情:', authStatus);
      return authStatus;
    } catch (error) {
      console.error(' Failed to get Gmail authorization status:', error);
      return null;
    }
  };
  
  // 添加手动触发Gmail授权函数
  window.triggerGmailAuth = async () => {
    console.log(' === 手动触发Gmail授权 ===');
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        console.error(' 没有Token，请先登录');
        return;
      }
      
      console.log(' 获取Gmail授权URL...');
      const response = await fetch('http://localhost:8000/api/gmail/auth_url/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.auth_url) {
          console.log(' 获取到授权URL，打开授权窗口...');
          
          // 开始监控Gmail授权过程
          if (window.monitorGmailAuth) {
            window.monitorGmailAuth();
          }
          
          window.open(data.auth_url, '_blank', 'width=500,height=700');
        } else {
          console.error(' 未获取到授权URL');
        }
      } else {
        console.error(' 获取授权URL失败:', response.status);
      }
    } catch (error) {
      console.error(' 触发Gmail授权失败:', error);
    }
  };
} 

// 获取AI Report数据
export const getAIReport = async () => {
  try {
    console.log(' 开始获取AI Report数据...');
    const response = await apiRequest('/api/ai_report/latest/');
    
    // 添加详细的调试信息
    console.log(' API响应详情:', response);
    console.log(' 响应类型:', typeof response);
    console.log(' 是否为数组:', Array.isArray(response));
    
    // 检查不同的数据格式
    if (response && response.id) {
      // 直接对象格式：{id: 1, financial_advice_summary: "...", ...}
      console.log(' 成功获取AI Report (直接对象格式):', response);
      return response;
    } else if (response && Array.isArray(response) && response.length > 0) {
      // 数组格式：[{id: 1, financial_advice_summary: "...", ...}]
      console.log(' 成功获取AI Report (数组格式):', response[0]);
      return response[0];
    } else if (response && response.report) {
      // 嵌套对象格式：{report: {id: 1, financial_advice_summary: "...", ...}}
      console.log(' 成功获取AI Report (嵌套对象格式):', response.report);
      return response.report;
    } else if (response && response.message === "No AI report found") {
      console.log(' 未找到AI Report数据 (后端明确返回无数据)');
      return null;
    } else if (response && typeof response === 'object' && Object.keys(response).length === 0) {
      console.log(' API返回空对象');
      return null;
    } else {
      console.log(' 未找到AI Report数据 (未知格式):', response);
      return null;
    }
  } catch (error) {
    console.error(' 获取AI Report失败:', error);
    return null;
  }
};

// 获取AI Report列表
export const getAIReportList = async (page = 1, pageSize = 10) => {
  try {
    console.log('🤖 开始获取AI Report列表...');
    const response = await apiRequest(`/api/ai_report/reports/?page=${page}&page_size=${pageSize}`);
    
    if (response && response.reports && Array.isArray(response.reports)) {
      console.log('✅ 成功获取AI Report列表:', response);
      return response;
    } else {
      console.log('⚠️ 未找到AI Report列表数据');
      return { reports: [], total: 0, page: 1, page_size: pageSize };
    }
  } catch (error) {
    console.error('❌ 获取AI Report列表失败:', error);
    return { reports: [], total: 0, page: 1, page_size: pageSize };
  }
};

// 获取单个AI Report详情
export const getAIReportDetail = async (reportId) => {
  try {
    console.log(`🤖 开始获取AI Report详情 (ID: ${reportId})...`);
    const response = await apiRequest(`/api/ai_report/reports/${reportId}/`);
    
    console.log('🔍 后端返回的原始数据:', response);
    console.log('🔍 数据类型:', typeof response);
    
    // 检查嵌套结构
    let reportData = null;
    if (response && response.report && Object.keys(response.report).length > 0) {
      // 数据在 report 字段中
      reportData = response.report;
      console.log('🔍 从report字段获取数据:', reportData);
    } else if (response && response.id) {
      // 数据直接在根级别
      reportData = response;
      console.log(' 从根级别获取数据:', reportData);
    } else {
      console.log(' 未找到有效的报告数据');
      return null;
    }
    
    if (reportData && reportData.id) {
      console.log(' 成功获取AI Report详情:', reportData);
      return reportData;
    } else {
      console.log(' 报告数据缺少id字段:', reportData);
      return null;
    }
  } catch (error) {
    console.error(' 获取AI Report详情失败:', error);
    return null;
  }
};

// 生成新的AI Report
export const generateAIReport = async (analysisPeriodDays = 30) => {
  try {
    console.log(' 开始生成AI Report...');
    const response = await apiRequest('/api/ai_report/generate/', {
      method: 'POST',
      body: { analysis_period_days: analysisPeriodDays }
    });
    
    if (response && response.id) {
      console.log(' 成功生成AI Report:', response);
      return response;
    } else {
      console.log(' AI Report生成失败');
      return null;
    }
  } catch (error) {
    console.error(' 生成AI Report失败:', error);
    return null;
  }
};

// Generate biweekly AI Report
export const generateBiweeklyAIReport = async (startDate, endDate) => {
  try {
    console.log(' Start generating biweekly AI Report...');
    console.log(' Date range:', startDate, 'to', endDate);
    
    const response = await apiRequest('/api/ai_report/biweekly/generate/', {
      method: 'POST',
      body: { 
        start_date: startDate,
        end_date: endDate
      }
    });
    
    console.log(' Backend response details:', response);
    console.log(' Response type:', typeof response);
    console.log(' Response ID field:', response?.id);
    console.log(' Response all fields:', Object.keys(response || {}));
    
    if (response && response.id) {
      console.log(' Successfully generated biweekly AI Report:', response);
      return response;
    } else if (response && response.report && response.report.id) {
      // If data is in report field
      console.log(' Successfully generated biweekly AI Report (nested format):', response.report);
      return response.report;
    } else if (response && response.success) {
      // If backend returns success field
      console.log(' Successfully generated biweekly AI Report (success format):', response);
      return response;
    } else if (response && typeof response === 'object' && Object.keys(response).length > 0) {
      // Temporary solution: accept any non-empty object response
      console.log(' Successfully generated biweekly AI Report (temporary format):', response);
      return response;
    } else {
      console.log(' Biweekly AI Report generation failed - response format mismatch');
      console.log(' Expected id field, but actual response:', response);
      return null;
    }
  } catch (error) {
    console.error(' Failed to generate biweekly AI Report:', error);
    return null;
  }
};

// 删除AI Report
export const deleteAIReport = async (reportId) => {
  try {
    console.log(` Start deleting AI Report (ID: ${reportId})...`);
    const response = await apiRequest(`/api/ai_report/reports/${reportId}/`, {
      method: 'DELETE'
    });
    
    console.log(' Successfully deleted AI Report');
    return true;
  } catch (error) {
    console.error(' Failed to delete AI Report:', error);
    return false;
  }
};

// Get AI Report statistics
export const getAIReportStats = async () => {
  try {
    console.log(' Start getting AI Report statistics...');
    const response = await apiRequest('/api/ai_report/stats/');
    
    if (response && response.stats) {
      console.log(' Successfully got AI Report statistics:', response);
      return response.stats;
    } else {
      console.log(' No AI Report statistics found');
      return null;
    }
  } catch (error) {
    console.error(' Failed to get AI Report statistics:', error);
    return null;
  }
}; 