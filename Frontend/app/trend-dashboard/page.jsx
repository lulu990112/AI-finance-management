"use client";
import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from "recharts";
import { getAllTransactions } from "../services/api";

// Default data (when API data is not available)
const mockData = [
  { month: "Jan", expense: 1200 },
  { month: "Feb", expense: 900 },
  { month: "Mar", expense: 1500 },
  { month: "Apr", expense: 1100 },
  { month: "May", expense: 1300 },
  { month: "Jun", expense: 1700 },
];

const weekData = [
  { week: "Week 1", expense: 320 },
  { week: "Week 2", expense: 280 },
  { week: "Week 3", expense: 350 },
  { week: "Week 4", expense: 300 },
  { week: "Week 5", expense: 400 },
  { week: "Week 6", expense: 370 },
];

export default function TrendDashboard() {
  const [monthlyData, setMonthlyData] = useState(mockData);
  const [weeklyData, setWeeklyData] = useState(weekData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Process monthly data
  const processMonthlyData = (transactions) => {
    if (!transactions || transactions.length === 0) {
      return mockData;
    }

    // Get the date range of the past 6 months
    const today = new Date();
    const sixMonthsAgo = new Date(today);
    sixMonthsAgo.setMonth(today.getMonth() - 5);
    sixMonthsAgo.setDate(1);
    sixMonthsAgo.setHours(0, 0, 0, 0);

    console.log('TrendDashboard monthly data range:', sixMonthsAgo.toISOString(), 'to', today.toISOString());

    // Group by month
    const monthlyMap = {};
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Initialize the data of the past 6 months
    for (let i = 0; i < 6; i++) {
      const monthDate = new Date(today);
      monthDate.setMonth(today.getMonth() - (5 - i));
      const monthKey = monthNames[monthDate.getMonth()];
      monthlyMap[monthKey] = 0;
    }

    // Filter the transactions of the past 6 months
    const monthlyTransactions = transactions.filter(tx => {
      const txDate = new Date(tx.transaction_date);
      return txDate >= sixMonthsAgo && txDate <= today;
    });

    console.log('TrendDashboard monthly transaction count:', monthlyTransactions.length);

    // Calculate the spending amount by month
    monthlyTransactions.forEach(tx => {
      const txDate = new Date(tx.transaction_date);
      const monthKey = monthNames[txDate.getMonth()];
      if (monthlyMap.hasOwnProperty(monthKey)) {
        monthlyMap[monthKey] += parseFloat(tx.amount || 0);
      }
    });

    // Convert to array format
    const processedMonthlyData = Object.entries(monthlyMap).map(([month, value]) => ({
      month,
      expense: Math.round(value * 100) / 100
    }));

    console.log('TrendDashboard processed monthly data:', processedMonthlyData);
    return processedMonthlyData;
  };

  // Process weekly data
  const processWeeklyData = (transactions) => {
    if (!transactions || transactions.length === 0) {
      return weekData;
    }

    // Get the date range of the past 6 weeks
    const today = new Date();
    const sixWeeksAgo = new Date(today);
    sixWeeksAgo.setDate(today.getDate() - 42); // 6 weeks = 42 days
    sixWeeksAgo.setHours(0, 0, 0, 0);

    console.log('TrendDashboard weekly data range:', sixWeeksAgo.toISOString(), 'to', today.toISOString());

    // Group by week
    const weeklyMap = {};

    // Initialize the data of the past 6 weeks
    for (let i = 0; i < 6; i++) {
      const weekDate = new Date(today);
      weekDate.setDate(today.getDate() - (35 - i * 7)); // Start from 6 weeks ago, 7 days per week
      const weekKey = `Week ${i + 1}`;
      weeklyMap[weekKey] = 0;
    }

    // Filter the transactions of the past 6 weeks
    const weeklyTransactions = transactions.filter(tx => {
      const txDate = new Date(tx.transaction_date);
      return txDate >= sixWeeksAgo && txDate <= today;
    });

    console.log('TrendDashboard weekly transaction count:', weeklyTransactions.length);

    // Calculate the spending amount by week
    weeklyTransactions.forEach(tx => {
      const txDate = new Date(tx.transaction_date);
      const daysDiff = Math.floor((today.getTime() - txDate.getTime()) / (1000 * 60 * 60 * 24));
      const weekIndex = Math.floor((42 - daysDiff) / 7);
      
      if (weekIndex >= 0 && weekIndex < 6) {
        const weekKey = `Week ${weekIndex + 1}`;
        if (weeklyMap.hasOwnProperty(weekKey)) {
          weeklyMap[weekKey] += parseFloat(tx.amount || 0);
        }
      }
    });

    // Convert to array format
    const processedWeeklyData = Object.entries(weeklyMap).map(([week, value]) => ({
      week,
      expense: Math.round(value * 100) / 100
    }));

    console.log('TrendDashboard processed weekly data:', processedWeeklyData);
    return processedWeeklyData;
  };

  // Get real data
  useEffect(() => {
    const fetchTransactionData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('TrendDashboard start getting transaction data...');
        const transactions = await getAllTransactions();
        
        if (transactions && transactions.length > 0) {
          console.log('TrendDashboard successfully got transaction data:', transactions.length, '条');
          
          // Process monthly data
          const monthlyData = processMonthlyData(transactions);
          setMonthlyData(monthlyData);
          
          // Process weekly data
          const weeklyData = processWeeklyData(transactions);
          setWeeklyData(weeklyData);
        } else {
          console.log('TrendDashboard no transaction data found, using default data');
          setMonthlyData(mockData);
          setWeeklyData(weekData);
        }
      } catch (err) {
        console.error('TrendDashboard failed to get transaction data:', err);
        setError('Failed to load data');
        setMonthlyData(mockData);
        setWeeklyData(weekData);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactionData();
  }, []);

  // Calculate average
  const total = monthlyData.reduce((sum, d) => sum + d.expense, 0);
  const avgMonth = (total / monthlyData.length).toFixed(2);
  const avgWeek = (total / (monthlyData.length * 4)).toFixed(2);

  const weekTotal = weeklyData.reduce((sum, d) => sum + d.expense, 0);
  const avgWeek2 = (weekTotal / weeklyData.length).toFixed(2);

  return (
    <div style={{ background: "#f4faff", minHeight: "100vh" }}>
      <Navbar />
      <section style={{ padding: "32px 0 0 0", borderBottom: "1px solid #f0f0f0" }}>
        <div className="container" style={{ maxWidth: 900, margin: "0 auto" }}>
          <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 8 }}>Spending Trends</h1>
          <div style={{ color: "#888", marginBottom: 24 }}>Monthly spending changes over the past 6 months and average level reference</div>
          
          {/* Error display */}
          {error && (
            <div style={{
              background: "#fff2f0",
              border: "1px solid #ffccc7",
              borderRadius: 8,
              padding: "16px",
              marginBottom: 24,
              color: "#ff4d4f"
            }}>
              {error}
            </div>
          )}
          
          {/* Loading indicator */}
          {loading && (
            <div style={{
              background: "#fff",
              borderRadius: 16,
              padding: "32px",
              marginBottom: 24,
              textAlign: "center",
              color: "#666"
            }}>
              Loading...
            </div>
          )}
          
          <div style={{ fontWeight: 700, fontSize: 22, marginBottom: 18 }}>Monthly Spending Changes (Past 6 Months)</div>
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 32, marginBottom: 40 }}>
            <ResponsiveContainer width="100%" height={380}>
              <LineChart data={monthlyData} margin={{ top: 24, right: 80, left: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => "$" + value} />
                <Legend />
                <Line type="monotone" dataKey="expense" name="Monthly Expenses" stroke="#ff7ca3" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} />
                <ReferenceLine y={avgMonth} label={{ value: `Monthly Avg: $${avgMonth}`, position: "insideRight", fill: "#888", fontSize: 12 }} stroke="#4ecbff" strokeDasharray="6 3" />
                <ReferenceLine y={avgWeek} label={{ value: `Weekly Avg: $${avgWeek}`, position: "insideRight", fill: "#aaa", fontSize: 12 }} stroke="#ffe08f" strokeDasharray="2 2" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          {/* Weekly spending changes line chart */}
          <div style={{ fontWeight: 700, fontSize: 22, marginBottom: 18 }}>Weekly Spending Changes (Past 6 Weeks)</div>
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 32 }}>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={weeklyData} margin={{ top: 24, right: 80, left: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis />
                <Tooltip formatter={(value) => "$" + value} />
                <Legend />
                <Line type="monotone" dataKey="expense" name="Weekly Expenses" stroke="#4ecbff" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} />
                <ReferenceLine y={avgWeek2} label={{ value: `Weekly Avg: $${avgWeek2}`, position: "insideRight", fill: "#888", fontSize: 12 }} stroke="#ff7ca3" strokeDasharray="6 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
} 