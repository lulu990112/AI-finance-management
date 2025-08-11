import { apiRequest } from './api';

// Group management API service
export const groupService = {
  // Create group
  createGroup: async (data) => {
    return await apiRequest('/api/group/create/', {
      method: 'POST',
      body: data
    });
  },

  // Get user group list
  getUserGroups: async () => {
    const res = await apiRequest('/api/group/list/');
    // Compatible with backend returning { groups: [...] } or direct array
    let groupArr = [];
    if (Array.isArray(res)) {
      groupArr = res;
    } else if (Array.isArray(res.groups)) {
      groupArr = res.groups;
    }
    return groupArr.map(g => ({
      ...g,
      id: g.group_id,
    }));
  },

  // Get group details
  getGroupInfo: async (groupId) => {
    return await apiRequest(`/api/group/${groupId}/`);
  },

  // Join group
  joinGroup: async (groupId) => {
    return await apiRequest('/api/group/join/', {
      method: 'POST',
      body: { group_id: groupId }
    });
  },

  // Leave group
  leaveGroup: async (groupId) => {
    return await apiRequest(`/api/group/${groupId}/leave/`, {
      method: 'POST'
    });
  },

  // Share transactions
  shareTransactions: async (data) => {
    return await apiRequest('/api/group/share_transactions/', {
      method: 'POST',
      body: data
    });
  },

  // View group transactions
  getGroupTransactions: async (groupId) => {
    const res = await apiRequest(`/api/group/${groupId}/transactions/`);
    // Backend return format: { success: true, transactions: [...], total_amount: 19.9, total_count: 2 }
    const transactions = res.transactions || res || [];
    return transactions.map(t => ({
      ...t,
      id: t.group_transaction_id,
      category: t.category_name,
      subcategory: t.subcategory_name,
      description: t.item_name,
      date: t.transaction_date,
      amount: parseFloat(t.amount),
      member_name: t.username,
    }));
  },

  // Generate group AI report
  generateGroupAIReport: async (groupId) => {
    return await apiRequest(`/api/group/${groupId}/ai_reports/generate/`, {
      method: 'POST'
    });
  },

  // Get group statistics
  getGroupStatistics: async (groupId) => {
    return await apiRequest(`/api/group/${groupId}/statistics/`);
  },

  // Export group data
  exportGroupData: async (groupId) => {
    return await apiRequest(`/api/group/${groupId}/export/`);
  },

  // Get group AI report list
  getGroupAIReports: async (groupId) => {
    return await apiRequest(`/api/group/${groupId}/ai_reports/`);
  },

  // Get group AI report details
  getGroupAIReportDetail: async (groupId, reportId) => {
    // Since the backend doesn't have a group AI report detail endpoint, we find the corresponding report from the list
    try {
      const reports = await groupService.getGroupAIReports(groupId);
      const reportsData = reports.reports || reports || [];
      const targetReport = reportsData.find(report => 
        report.group_ai_report_id === parseInt(reportId) || report.id === parseInt(reportId)
      );
      
      if (targetReport) {
        return targetReport;
      } else {
        throw new Error('AI report not found');
      }
    } catch (error) {
      console.error('Failed to get group AI report details:', error);
      throw error;
    }
  }
};
