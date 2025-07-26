"use client";
import React from "react";
import Navbar from "../components/Navbar";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from "recharts";

// mock data: monthly expenses for the past 6 months
const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"];
const mockData = [
  { month: "Jan", expense: 1200 },
  { month: "Feb", expense: 900 },
  { month: "Mar", expense: 1500 },
  { month: "Apr", expense: 1100 },
  { month: "May", expense: 1300 },
  { month: "Jun", expense: 1700 },
];
const total = mockData.reduce((sum, d) => sum + d.expense, 0);
const avgMonth = (total / mockData.length).toFixed(2);
const avgWeek = (total / (mockData.length * 4)).toFixed(2); // simple assumption of 4 weeks per month

const weekData = [
  { week: "Week 1", expense: 320 },
  { week: "Week 2", expense: 280 },
  { week: "Week 3", expense: 350 },
  { week: "Week 4", expense: 300 },
  { week: "Week 5", expense: 400 },
  { week: "Week 6", expense: 370 },
];
const weekTotal = weekData.reduce((sum, d) => sum + d.expense, 0);
const avgWeek2 = (weekTotal / weekData.length).toFixed(2);

export default function TrendDashboard() {
  return (
    <div style={{ background: "#f4faff", minHeight: "100vh" }}>
      <Navbar />
      <section style={{ padding: "32px 0 0 0", borderBottom: "1px solid #f0f0f0" }}>
        <div className="container" style={{ maxWidth: 900, margin: "0 auto" }}>
          <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 8 }}>Spending Trends</h1>
          <div style={{ color: "#888", marginBottom: 24 }}>Monthly spending changes over the past 6 months and average level reference</div>
          <div style={{ fontWeight: 700, fontSize: 22, marginBottom: 18 }}>Monthly Spending Changes (Past 6 Months)</div>
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 32, marginBottom: 40 }}>
            <ResponsiveContainer width="100%" height={380}>
              <LineChart data={mockData} margin={{ top: 24, right: 32, left: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => "$" + value} />
                <Legend />
                <Line type="monotone" dataKey="expense" name="Monthly Expenses" stroke="#ff7ca3" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} />
                <ReferenceLine y={avgMonth} label={{ value: `Monthly Avg: $${avgMonth}`, position: "right", fill: "#888" }} stroke="#4ecbff" strokeDasharray="6 3" />
                <ReferenceLine y={avgWeek} label={{ value: `Weekly Avg: $${avgWeek}`, position: "right", fill: "#aaa" }} stroke="#ffe08f" strokeDasharray="2 2" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          {/* Weekly spending changes line chart */}
          <div style={{ fontWeight: 700, fontSize: 22, marginBottom: 18 }}>Weekly Spending Changes (Past 6 Weeks)</div>
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 32 }}>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={weekData} margin={{ top: 24, right: 32, left: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis />
                <Tooltip formatter={(value) => "$" + value} />
                <Legend />
                <Line type="monotone" dataKey="expense" name="Weekly Expenses" stroke="#4ecbff" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} />
                <ReferenceLine y={avgWeek2} label={{ value: `Weekly Avg: $${avgWeek2}`, position: "right", fill: "#888" }} stroke="#ff7ca3" strokeDasharray="6 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
} 