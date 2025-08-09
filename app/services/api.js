// API基础配置
const API_BASE_URL = 'http://localhost:8000';

// 获取存储的token
const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('authToken');
    console.log('🔍 获取Token:', token ? `${token.substring(0, 20)}...` : 'null');
    return token;
  }
  return null;
};

// 存储token
const setAuthToken = (token) => {
  if (typeof window !== 'undefined') {
    console.log('💾 存储Token:', token ? `${token.substring(0, 20)}...` : 'null');
    localStorage.setItem('authToken', token);
  }
};

// 清除token
const clearAuthToken = () => {
  if (typeof window !== 'undefined') {
    console.log('🗑️ 清除Token');
    localStorage.removeItem('authToken');
  }
};

// 通用API请求函数
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();
  
  console.log(`🌐 API请求: ${endpoint}`);
  console.log(`🔑 使用Token:`, token ? '是' : '否');
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    ...options,
  };

  // 如果有body参数，需要JSON序列化
  if (options.body && typeof options.body === 'object') {
    defaultOptions.body = JSON.stringify(options.body);
  } else if (options.body) {
    defaultOptions.body = options.body;
  }

  try {
    const response = await fetch(url, defaultOptions);
    
    console.log(`📡 响应状态: ${response.status} ${response.statusText}`);
    
    if (response.status === 401) {
      // Token过期或无效，清除token并抛出错误
      console.log('❌ 认证失败，清除Token');
      clearAuthToken();
      throw new Error('认证失败，请重新登录');
    }
    
    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API请求错误:', error);
    throw error;
  }
};

// 登录API
export const login = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/api/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error('登录失败');
  }

  const data = await response.json();
  
  if (data.success && data.data.token) {
    setAuthToken(data.data.token);
    return data.data;
  } else {
    throw new Error(data.message || '登录失败');
  }
};

// 同步Gmail收据
export const syncGmailReceipts = async () => {
  console.log('📧 开始Gmail同步...');
  console.log('🔍 同步前Token状态:', getAuthToken() ? '存在' : '不存在');
  
  const result = await apiRequest('/api/gpt/batch_sync_and_process/', {
    method: 'POST',
  });
  
  console.log('📧 Gmail同步完成');
  console.log('🔍 同步后Token状态:', getAuthToken() ? '存在' : '不存在');
  
  return result;
};

// 获取所有交易记录
export const getAllTransactions = async () => {
  try {
    console.log('📊 开始获取所有交易数据...');
    
    // 首先获取第一页数据来了解总数
    const firstPageResponse = await apiRequest('/api/gpt/transactions/?page=1&page_size=20');
    
    if (!firstPageResponse || !firstPageResponse.transactions) {
      console.error('❌ 获取第一页数据失败');
      return [];
    }
    
    const total = firstPageResponse.total || 0;
    const pageSize = 20; // 后端默认分页大小
    const totalPages = Math.ceil(total / pageSize);
    
    console.log(`📊 总数据量: ${total}, 总页数: ${totalPages}`);
    
    // 如果只有一页数据，直接返回
    if (totalPages <= 1) {
      console.log('📊 只有一页数据，直接返回');
      return firstPageResponse.transactions;
    }
    
    // 获取所有页面的数据
    const allTransactions = [...firstPageResponse.transactions];
    
    // 并行获取剩余页面的数据
    const remainingPages = [];
    for (let page = 2; page <= totalPages; page++) {
      remainingPages.push(
        apiRequest(`/api/gpt/transactions/?page=${page}&page_size=${pageSize}`)
      );
    }
    
    console.log(`📊 开始获取剩余 ${totalPages - 1} 页数据...`);
    const remainingResponses = await Promise.all(remainingPages);
    
    // 合并所有数据
    remainingResponses.forEach((response, index) => {
      if (response && response.transactions) {
        allTransactions.push(...response.transactions);
        console.log(`📊 第 ${index + 2} 页数据: ${response.transactions.length} 条`);
      }
    });
    
    console.log(`📊 成功获取所有数据: ${allTransactions.length} 条`);
    
    // 按交易日期降序排序，确保最新的在前面
    allTransactions.sort((a, b) => {
      const dateA = new Date(a.transaction_date);
      const dateB = new Date(b.transaction_date);
      return dateB - dateA;
    });
    
    console.log('📊 数据已按日期降序排序');
    return allTransactions;
    
  } catch (error) {
    console.error('❌ 获取所有交易数据失败:', error);
    return [];
  }
};

// 获取分类数据
export const getCategoryData = async () => {
  return apiRequest('/api/gpt/categories/');
};

// 获取特定分类的详细数据（前端数据处理）
export const getCategoryDetail = async (categoryName) => {
  try {
    // 并行获取所有交易和分类结构
    const [allTransactions, categoryStructure] = await Promise.all([
      getAllTransactions(),
      getCategoryData()
    ]);

    console.log('📊 获取到交易数据:', allTransactions.length, '条');
    console.log('📊 获取到分类结构:', categoryStructure);

    // 找到目标分类
    const targetCategory = categoryStructure.categories.find(cat => 
      cat.name === categoryName
    );

    if (!targetCategory) {
      console.error('❌ 未找到分类:', categoryName);
      return null;
    }

    // 筛选该分类的交易
    const categoryTransactions = allTransactions.filter(tx => {
      // 处理category字段可能是对象或字符串的情况
      const txCategory = typeof tx.category === 'object' ? tx.category.name : tx.category;
      return txCategory === categoryName;
    });

    console.log('📊 筛选到分类交易:', categoryTransactions.length, '条');

    // 计算该分类的总金额
    const totalAmount = categoryTransactions.reduce((sum, tx) => {
      return sum + parseFloat(tx.amount || 0);
    }, 0);

    // 按子分类分组和汇总
    const subcategoryMap = {};
    categoryTransactions.forEach(tx => {
      // 处理subcategory字段可能是对象或字符串的情况
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

    // 转换为子分类数组
    const subcategories = Object.entries(subcategoryMap).map(([name, data]) => ({
      name,
      value: data.amount,
      color: getDefaultSubcategoryColor(name),
      transactions: data.transactions
    }));

    // 格式化交易记录
    const formattedTransactions = categoryTransactions.map(tx => ({
      id: tx.id,
      date: formatDate(tx.transaction_date),
      subcategory: typeof tx.subcategory === 'object' ? tx.subcategory.name : tx.subcategory,
      amount: parseFloat(tx.amount || 0),
      note: tx.note || tx.item_name || '无备注'
    }));

    // 按日期排序（最新的在前）
    formattedTransactions.sort((a, b) => new Date(b.date) - new Date(a.date));

    return {
      total: totalAmount,  // 使用计算出的总金额
      subcategories,
      transactions: formattedTransactions
    };

  } catch (error) {
    console.error('❌ 获取分类详情失败:', error);
    throw error;
  }
};

// 获取所有分类的汇总数据（前端数据处理）
export const getCategorySummary = async () => {
  try {
    // 并行获取所有交易和分类结构
    const [allTransactions, categoryStructure] = await Promise.all([
      getAllTransactions(),
      getCategoryData()
    ]);
    
    console.log('📊 获取到分类结构:', categoryStructure);

    // 按分类分组计算总金额
    const categoryTotals = {};
    allTransactions.forEach(tx => {
      const categoryName = typeof tx.category === 'object' ? tx.category.name : tx.category;
      if (!categoryTotals[categoryName]) {
        categoryTotals[categoryName] = 0;
      }
      categoryTotals[categoryName] += parseFloat(tx.amount || 0);
    });

    // 生成分类汇总数据
    const categorySummaries = categoryStructure.categories.map(category => ({
      name: category.name,
      total_amount: categoryTotals[category.name] || 0,  // 使用计算出的总金额
      color: category.color || getDefaultCategoryColor(category.name),
      transaction_count: 0  // 如果需要，可以单独计算
    }));

    console.log('📊 生成分类汇总:', categorySummaries);
    return categorySummaries;

  } catch (error) {
    console.error('❌ 获取分类汇总失败:', error);
    throw error;
  }
};

// 辅助函数：格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知日期';
  
  try {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0]; // 返回 YYYY-MM-DD 格式
  } catch (error) {
    console.error('❌ 日期格式化失败:', dateString);
    return '未知日期';
  }
};

// 辅助函数：获取默认子分类颜色
const getDefaultSubcategoryColor = (subcategoryName) => {
  const colorMap = {
    // Dining 分类的子分类
    'Snacks': '#ff7ca3',
    'Snack': '#ff7ca3',
    'Meals': '#4ecbff',
    'Drinks': '#ffe08f',
    'Drink': '#ffe08f',
    'Restaurant': '#5adbb5',
    'Daily meal': '#4ecbff',
    'Daily': '#ffe08f',
    
    // Transport 分类的子分类
    'Bus': '#4ecbff',
    'Subway': '#5adbb5',
    'Taxi': '#a084e8',
    'Train': '#a084e8',
    
    // Shopping 分类的子分类
    'Clothing': '#ff7ca3',
    'Electronics': '#4ecbff',
    'Cosmetic': '#ff4444',
    'Cosmetics': '#ff4444',
    'Household': '#4ecbff',
    
    // Entertainment 分类的子分类
    'Movies': '#5adbb5',
    'Movie': '#5adbb5',
    'Games': '#ff7ca3',
    'Game': '#ff7ca3',
    'KTV': '#a084e8',
    
    // Healthcare 分类的子分类
    'Medicine': '#a084e8',
    'Medical': '#4ecbff'
  };
  
  return colorMap[subcategoryName] || '#666666';
};

// 辅助函数：获取默认分类颜色
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

// 获取最新交易（从所有交易中筛选最近4条）
export const getRecentTransactions = async () => {
  const allTransactions = await getAllTransactions();
  
  // 返回最近4条交易
  return allTransactions.slice(0, 4);
};

// 获取特定分类的交易（从所有交易中筛选）
export const getTransactionsByCategory = async (category) => {
  const allTransactions = await getAllTransactions();
  
  // 根据分类筛选交易
  const filteredTransactions = allTransactions.filter(tx => 
    tx.category === category || tx.subcategory === category
  );
  
  // 计算分类统计信息
  const totalAmount = filteredTransactions.reduce((sum, tx) => sum + parseFloat(tx.amount || 0), 0);
  
  return {
    total_amount: totalAmount,
    transactions: filteredTransactions,
    subcategories: [] // 暂时返回空数组，后续可以根据需要实现
  };
};

// 获取Gmail授权状态
export const getGmailAuthStatus = async () => {
  return apiRequest('/api/gmail/auth_status/');
};

// 调试函数：检查token状态
export const debugTokenStatus = () => {
  const token = localStorage.getItem('authToken');
  console.log('🔍 === Token状态检查 ===');
  console.log('Token存在:', !!token);
  if (token) {
    console.log('Token长度:', token.length);
    console.log('Token前20字符:', token.substring(0, 20));
    
    // 尝试解析JWT token（如果可能）
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        console.log('Token过期时间:', new Date(payload.exp * 1000));
        console.log('当前时间:', new Date());
        console.log('是否过期:', Date.now() > payload.exp * 1000);
      }
    } catch (e) {
      console.log('无法解析JWT token');
    }
  }
  console.log('🔍 ====================');
  return token;
};

// 将调试函数暴露到全局作用域
if (typeof window !== 'undefined') {
  window.debugTokenStatus = debugTokenStatus;
  
  // 添加Gmail授权窗口监控
  window.monitorGmailAuth = () => {
    console.log('🔍 === 开始监控Gmail授权过程 ===');
    
    // 检查Gmail授权状态
    const checkGmailAuthStatus = async () => {
      try {
        console.log('🔍 检查Gmail授权状态...');
        console.log('🔍 当前Token状态:', localStorage.getItem('authToken') ? '存在' : '不存在');
        
        const authStatus = await getGmailAuthStatus();
        console.log('🔍 Gmail授权状态:', authStatus);
        
        return authStatus;
      } catch (error) {
        console.error('❌ 获取Gmail授权状态失败:', error);
        return null;
      }
    };
    
    // 每3秒检查一次状态
    const interval = setInterval(async () => {
      const authStatus = await checkGmailAuthStatus();
      
      if (authStatus && authStatus.is_authorized) {
        console.log('✅ 检测到Gmail授权成功！');
        console.log('🔍 授权详情:', authStatus);
        clearInterval(interval);
        
        // 延迟检查Token状态
        setTimeout(() => {
          console.log('🔍 授权成功后Token状态:', localStorage.getItem('authToken') ? '存在' : '不存在');
          debugTokenStatus();
        }, 1000);
      } else if (authStatus) {
        console.log('⏳ Gmail授权状态:', authStatus.status || '未知');
      }
    }, 3000);
    
    // 60秒后自动停止监控
    setTimeout(() => {
      clearInterval(interval);
      console.log('⏰ Gmail授权监控超时');
    }, 60000);
    
    return interval;
  };
  
  // 添加手动监控Gmail同步过程
  window.monitorGmailSync = () => {
    console.log('🔍 === 开始监控Gmail同步过程 ===');
    console.log('🔍 同步前Token状态:', localStorage.getItem('authToken') ? '存在' : '不存在');
    debugTokenStatus();
    
    // 每5秒检查一次Token状态
    const interval = setInterval(() => {
      console.log('🔍 检查Token状态变化...');
      debugTokenStatus();
    }, 5000);
    
    // 60秒后自动停止监控
    setTimeout(() => {
      clearInterval(interval);
      console.log('⏰ Gmail同步监控结束');
    }, 60000);
    
    return interval;
  };
  
  // 添加Gmail授权状态检查函数
  window.checkGmailAuthStatus = async () => {
    console.log('🔍 === 检查Gmail授权状态 ===');
    try {
      const authStatus = await getGmailAuthStatus();
      console.log('🔍 Gmail授权状态详情:', authStatus);
      return authStatus;
    } catch (error) {
      console.error('❌ 获取Gmail授权状态失败:', error);
      return null;
    }
  };
  
  // 添加手动触发Gmail授权函数
  window.triggerGmailAuth = async () => {
    console.log('🔍 === 手动触发Gmail授权 ===');
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        console.error('❌ 没有Token，请先登录');
        return;
      }
      
      console.log('🔍 获取Gmail授权URL...');
      const response = await fetch('http://localhost:8000/api/gmail/auth_url/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.auth_url) {
          console.log('🔍 获取到授权URL，打开授权窗口...');
          
          // 开始监控Gmail授权过程
          if (window.monitorGmailAuth) {
            window.monitorGmailAuth();
          }
          
          window.open(data.auth_url, '_blank', 'width=500,height=700');
        } else {
          console.error('❌ 未获取到授权URL');
        }
      } else {
        console.error('❌ 获取授权URL失败:', response.status);
      }
    } catch (error) {
      console.error('❌ 触发Gmail授权失败:', error);
    }
  };
} 

// 获取AI Report数据
export const getAIReport = async () => {
  try {
    console.log('🤖 开始获取AI Report数据...');
    const response = await apiRequest('/api/ai_report/latest/');
    
    // 添加详细的调试信息
    console.log('🔍 API响应详情:', response);
    console.log('🔍 响应类型:', typeof response);
    console.log('🔍 是否为数组:', Array.isArray(response));
    
    // 检查不同的数据格式
    if (response && response.id) {
      // 直接对象格式：{id: 1, financial_advice_summary: "...", ...}
      console.log('✅ 成功获取AI Report (直接对象格式):', response);
      return response;
    } else if (response && Array.isArray(response) && response.length > 0) {
      // 数组格式：[{id: 1, financial_advice_summary: "...", ...}]
      console.log('✅ 成功获取AI Report (数组格式):', response[0]);
      return response[0];
    } else if (response && response.report) {
      // 嵌套对象格式：{report: {id: 1, financial_advice_summary: "...", ...}}
      console.log('✅ 成功获取AI Report (嵌套对象格式):', response.report);
      return response.report;
    } else if (response && response.message === "No AI report found") {
      console.log('⚠️ 未找到AI Report数据 (后端明确返回无数据)');
      return null;
    } else if (response && typeof response === 'object' && Object.keys(response).length === 0) {
      console.log('⚠️ API返回空对象');
      return null;
    } else {
      console.log('⚠️ 未找到AI Report数据 (未知格式):', response);
      return null;
    }
  } catch (error) {
    console.error('❌ 获取AI Report失败:', error);
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
      console.log('🔍 从根级别获取数据:', reportData);
    } else {
      console.log('⚠️ 未找到有效的报告数据');
      return null;
    }
    
    if (reportData && reportData.id) {
      console.log('✅ 成功获取AI Report详情:', reportData);
      return reportData;
    } else {
      console.log('⚠️ 报告数据缺少id字段:', reportData);
      return null;
    }
  } catch (error) {
    console.error('❌ 获取AI Report详情失败:', error);
    return null;
  }
};

// 生成新的AI Report
export const generateAIReport = async (analysisPeriodDays = 30) => {
  try {
    console.log('🤖 开始生成AI Report...');
    const response = await apiRequest('/api/ai_report/generate/', {
      method: 'POST',
      body: { analysis_period_days: analysisPeriodDays }
    });
    
    if (response && response.id) {
      console.log('✅ 成功生成AI Report:', response);
      return response;
    } else {
      console.log('⚠️ AI Report生成失败');
      return null;
    }
  } catch (error) {
    console.error('❌ 生成AI Report失败:', error);
    return null;
  }
};

// 删除AI Report
export const deleteAIReport = async (reportId) => {
  try {
    console.log(`🤖 开始删除AI Report (ID: ${reportId})...`);
    const response = await apiRequest(`/api/ai_report/reports/${reportId}/`, {
      method: 'DELETE'
    });
    
    console.log('✅ 成功删除AI Report');
    return true;
  } catch (error) {
    console.error('❌ 删除AI Report失败:', error);
    return false;
  }
};

// 获取AI Report统计信息
export const getAIReportStats = async () => {
  try {
    console.log('🤖 开始获取AI Report统计信息...');
    const response = await apiRequest('/api/ai_report/stats/');
    
    if (response && response.stats) {
      console.log('✅ 成功获取AI Report统计信息:', response);
      return response.stats;
    } else {
      console.log('⚠️ 未找到AI Report统计信息');
      return null;
    }
  } catch (error) {
    console.error('❌ 获取AI Report统计信息失败:', error);
    return null;
  }
}; 