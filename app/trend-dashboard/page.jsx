"use client";
import React from "react";
import Navbar from "../components/Navbar";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from "recharts";

// mock 数据：近半年每月支出
const months = ["1月", "2月", "3月", "4月", "5月", "6月"];
const mockData = [
  { month: "1月", expense: 1200 },
  { month: "2月", expense: 900 },
  { month: "3月", expense: 1500 },
  { month: "4月", expense: 1100 },
  { month: "5月", expense: 1300 },
  { month: "6月", expense: 1700 },
];
const total = mockData.reduce((sum, d) => sum + d.expense, 0);
const avgMonth = (total / mockData.length).toFixed(2);
const avgWeek = (total / (mockData.length * 4)).toFixed(2); // 简单假设每月4周

const weekData = [
  { week: "第1周", expense: 320 },
  { week: "第2周", expense: 280 },
  { week: "第3周", expense: 350 },
  { week: "第4周", expense: 300 },
  { week: "第5周", expense: 400 },
  { week: "第6周", expense: 370 },
];
const weekTotal = weekData.reduce((sum, d) => sum + d.expense, 0);
const avgWeek2 = (weekTotal / weekData.length).toFixed(2);

export default function TrendDashboard() {
  return (
    <div style={{ background: "#f4faff", minHeight: "100vh" }}>
      <Navbar />
      <section style={{ padding: "32px 0 0 0", borderBottom: "1px solid #f0f0f0" }}>
        <div className="container" style={{ maxWidth: 900, margin: "0 auto" }}>
          <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 8 }}>消费趋势</h1>
          <div style={{ color: "#888", marginBottom: 24 }}>近半年月度支出变化及平均水平参考</div>
          <div style={{ fontWeight: 700, fontSize: 22, marginBottom: 18 }}>近半年月度支出变化</div>
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 32, marginBottom: 40 }}>
            <ResponsiveContainer width="100%" height={380}>
              <LineChart data={mockData} margin={{ top: 24, right: 32, left: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => value + " 元"} />
                <Legend />
                <Line type="monotone" dataKey="expense" name="月度支出" stroke="#ff7ca3" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} />
                <ReferenceLine y={avgMonth} label={{ value: `月均 ${avgMonth} 元`, position: "right", fill: "#888" }} stroke="#4ecbff" strokeDasharray="6 3" />
                <ReferenceLine y={avgWeek} label={{ value: `周均 ${avgWeek} 元`, position: "right", fill: "#aaa" }} stroke="#ffe08f" strokeDasharray="2 2" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          {/* 新增每周支出变化折线图 */}
          <div style={{ fontWeight: 700, fontSize: 22, marginBottom: 18 }}>近6周每周支出变化</div>
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 32 }}>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={weekData} margin={{ top: 24, right: 32, left: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis />
                <Tooltip formatter={(value) => value + " 元"} />
                <Legend />
                <Line type="monotone" dataKey="expense" name="每周支出" stroke="#4ecbff" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} />
                <ReferenceLine y={avgWeek2} label={{ value: `周均 ${avgWeek2} 元`, position: "right", fill: "#888" }} stroke="#ff7ca3" strokeDasharray="6 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
} 