'use client';
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { groupService } from '../services/groupService';
import { toast } from 'react-toastify';

// Initial state
const initialState = {
  groups: [],
  currentGroup: null,
  loading: false,
  error: null,
  groupTransactions: [],
  groupStatistics: null
};

// Action types
const GROUP_ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_GROUPS: 'SET_GROUPS',
  SET_CURRENT_GROUP: 'SET_CURRENT_GROUP',
  ADD_GROUP: 'ADD_GROUP',
  UPDATE_GROUP: 'UPDATE_GROUP',
  REMOVE_GROUP: 'REMOVE_GROUP',
  SET_GROUP_TRANSACTIONS: 'SET_GROUP_TRANSACTIONS',
  SET_GROUP_STATISTICS: 'SET_GROUP_STATISTICS'
};

// Reducer function
const groupReducer = (state, action) => {
  switch (action.type) {
    case GROUP_ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    case GROUP_ACTIONS.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    case GROUP_ACTIONS.SET_GROUPS:
      return { ...state, groups: Array.isArray(action.payload) ? action.payload : [], loading: false };
    case GROUP_ACTIONS.SET_CURRENT_GROUP:
      return { ...state, currentGroup: action.payload };
    case GROUP_ACTIONS.ADD_GROUP:
      return { ...state, groups: [...state.groups, action.payload] };
    case GROUP_ACTIONS.UPDATE_GROUP:
      return {
        ...state,
        groups: state.groups.map(group => 
          group.id === action.payload.id ? action.payload : group
        ),
        currentGroup: state.currentGroup?.id === action.payload.id ? action.payload : state.currentGroup
      };
    case GROUP_ACTIONS.REMOVE_GROUP:
      return {
        ...state,
        groups: state.groups.filter(group => group.id !== action.payload),
        currentGroup: state.currentGroup?.id === action.payload ? null : state.currentGroup
      };
    case GROUP_ACTIONS.SET_GROUP_TRANSACTIONS:
      return { ...state, groupTransactions: Array.isArray(action.payload) ? action.payload : [] };
    case GROUP_ACTIONS.SET_GROUP_STATISTICS:
      return { ...state, groupStatistics: action.payload };
    default:
      return state;
  }
};

// Create Context
const GroupContext = createContext();

// Provider component
export const GroupProvider = ({ children }) => {
  const [state, dispatch] = useReducer(groupReducer, initialState);

  // Get user group list
  const fetchGroups = async () => {
    dispatch({ type: GROUP_ACTIONS.SET_LOADING, payload: true });
    try {
      const response = await groupService.getUserGroups();
      dispatch({ type: GROUP_ACTIONS.SET_GROUPS, payload: response });
    } catch (error) {
      dispatch({ type: GROUP_ACTIONS.SET_ERROR, payload: error.message });
      toast.error('Failed to get group list');
    }
  };

  // Create group
  const createGroup = async (groupData) => {
    dispatch({ type: GROUP_ACTIONS.SET_LOADING, payload: true });
    try {
      const response = await groupService.createGroup(groupData);
      const newGroup = response.data || response;
      dispatch({ type: GROUP_ACTIONS.ADD_GROUP, payload: newGroup });
      toast.success('Group created successfully!');
      return newGroup;
    } catch (error) {
      dispatch({ type: GROUP_ACTIONS.SET_ERROR, payload: error.message });
      toast.error('Failed to create group');
      throw error;
    }
  };

  // Join group
  const joinGroup = async (groupId) => {
    dispatch({ type: GROUP_ACTIONS.SET_LOADING, payload: true });
    try {
      await groupService.joinGroup(groupId);
      await fetchGroups(); // Refresh group list
      toast.success('Successfully joined the group!');
    } catch (error) {
      dispatch({ type: GROUP_ACTIONS.SET_ERROR, payload: error.message });
      toast.error('Failed to join group');
      throw error;
    }
  };

  // Leave group
  const leaveGroup = async (groupId) => {
    dispatch({ type: GROUP_ACTIONS.SET_LOADING, payload: true });
    try {
      await groupService.leaveGroup(groupId);
      dispatch({ type: GROUP_ACTIONS.REMOVE_GROUP, payload: groupId });
      toast.success('Left the group');
    } catch (error) {
      dispatch({ type: GROUP_ACTIONS.SET_ERROR, payload: error.message });
      toast.error('Failed to leave group');
      throw error;
    }
  };

  // Get group info
  const getGroupInfo = async (groupId) => {
    try {
      const response = await groupService.getGroupInfo(groupId);
      const raw = response.data || response;
      const info = raw.group_info ? { ...raw.group_info } : { ...raw };
      const groupInfo = {
        ...info,
        id: info.group_id || info.id,
        group_name: info.group_name || info.name || info.title || info.groupTitle || 'Unnamed Group',
        member_count: info.member_count ?? (Array.isArray(raw.members) ? raw.members.length : 0),
        max_members: info.max_members || 10,
        created_at: info.created_at || info.create_time || info.date,
        members: raw.members || info.members || [],
        user_role: raw.user_role || info.user_role,
      };
      dispatch({ type: GROUP_ACTIONS.SET_CURRENT_GROUP, payload: groupInfo });
      return groupInfo;
    } catch (error) {
      dispatch({ type: GROUP_ACTIONS.SET_ERROR, payload: error.message });
      toast.error('Failed to get group info');
      throw error;
    }
  };

  // Get group transactions
  const getGroupTransactions = async (groupId) => {
    try {
      const response = await groupService.getGroupTransactions(groupId);
      dispatch({ type: GROUP_ACTIONS.SET_GROUP_TRANSACTIONS, payload: response });
      return response;
    } catch (error) {
      dispatch({ type: GROUP_ACTIONS.SET_ERROR, payload: error.message });
      toast.error('Failed to get group transactions');
      throw error;
    }
  };

  // Share transactions
  const shareTransactions = async (shareData) => {
    try {
      await groupService.shareTransactions(shareData);
      toast.success('Transactions shared successfully!');
    } catch (error) {
      toast.error('Failed to share transactions');
      throw error;
    }
  };

  // Get group statistics
  const getGroupStatistics = async (groupId) => {
    try {
      const response = await groupService.getGroupStatistics(groupId);
      const statistics = response.data || response;
      dispatch({ type: GROUP_ACTIONS.SET_GROUP_STATISTICS, payload: statistics });
      return statistics;
    } catch (error) {
      dispatch({ type: GROUP_ACTIONS.SET_ERROR, payload: error.message });
      toast.error('Failed to get group statistics');
      throw error;
    }
  };

  // Generate group AI report
  const generateGroupAIReport = async (groupId) => {
    try {
      const response = await groupService.generateGroupAIReport(groupId);
      toast.success('AI report generated successfully!');
      return response;
    } catch (error) {
      toast.error('Failed to generate AI report');
      throw error;
    }
  };

  // Export group data
  const exportGroupData = async (groupId) => {
    try {
      const response = await groupService.exportGroupData(groupId);
      return response;
    } catch (error) {
      toast.error('Failed to export data');
      throw error;
    }
  };

  const value = {
    ...state,
    fetchGroups,
    createGroup,
    joinGroup,
    leaveGroup,
    getGroupInfo,
    getGroupTransactions,
    shareTransactions,
    getGroupStatistics,
    generateGroupAIReport,
    exportGroupData
  };

  return (
    <GroupContext.Provider value={value}>
      {children}
    </GroupContext.Provider>
  );
};

// Hook
export const useGroup = () => {
  const context = useContext(GroupContext);
  if (!context) {
    throw new Error('useGroup must be used within a GroupProvider');
  }
  return context;
};
