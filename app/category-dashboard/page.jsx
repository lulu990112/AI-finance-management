"use client"
import React, { useState } from "react";
import { PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts";
import { DateRange } from "react-date-range";
import Navbar from "../components/Navbar";
import "react-date-range/dist/styles.css";
import "react-date-range/dist/theme/default.css";

// mock data
const mockCategories = [
  { name: "Dining", value: 1200, color: "#ff7ca3" },
  { name: "Transport", value: 800, color: "#4ecbff" },
  { name: "Shopping", value: 600, color: "#ffe08f" },
  { name: "Entertainment", value: 400, color: "#5adbb5" },
  { name: "Healthcare", value: 200, color: "#a084e8" },
];
const totalAmount = mockCategories.reduce((sum, c) => sum + c.value, 0);
const mockTransactions = 42;
const mockAvg = totalAmount / mockTransactions;

export default function CategoryDashboard() {
  const [dateRange, setDateRange] = useState([
    {
      startDate: new Date(),
      endDate: new Date(),
      key: "selection"
    }
  ]);
  const [activeIndex, setActiveIndex] = useState(null);

  return (
    <div style={{ background: "#f4faff", minHeight: "100vh" }}>
      <Navbar />
      <section style={{ padding: "32px 0 0 0", borderBottom: "1px solid #f0f0f0" }}>
        <div className="container" style={{ maxWidth: 1200, margin: "0 auto" }}>
          <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 8 }}>Category Dashboard</h1>
          <div style={{ color: "#888", marginBottom: 24 }}>Conduct statistics and analysis on spending records for any number of days</div>
          <div style={{ display: "flex", gap: 32 }}>
            {/* Pie chart */}
            <div style={{ flex: 2, background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 32 }}>
              <h3 style={{ marginBottom: 16 }}>Spending Category Distribution</h3>
              <ResponsiveContainer width="100%" height={340}>
                <PieChart>
                  <Pie
                    data={mockCategories}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={80}
                    outerRadius={120}
                    onMouseEnter={(_, idx) => setActiveIndex(idx)}
                    onMouseLeave={() => setActiveIndex(null)}
                  >
                    {mockCategories.map((entry, idx) => (
                      <Cell key={entry.name} fill={entry.color} opacity={activeIndex === idx ? 1 : 0.7} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value, name, props) => {
                      const percent = ((value / totalAmount) * 100).toFixed(1) + "%";
                      return [
                        "$" + value + " (" + percent + ")",
                        props.payload.name
                      ];
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              {activeIndex !== null && (
                <div style={{ marginTop: 16, textAlign: "center", fontWeight: 600, fontSize: 18 }}>
                  {mockCategories[activeIndex].name}: ${mockCategories[activeIndex].value} ({((mockCategories[activeIndex].value / totalAmount) * 100).toFixed(1)}%)
                </div>
              )}
            </div>
            {/* Date picker + metrics cards + bar chart + category list */}
            <div style={{ flex: 3, display: "flex", flexDirection: "column", gap: 24 }}>
              <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 24, marginBottom: 8 }}>
                <h3 style={{ marginBottom: 12 }}>Statistics Period</h3>
                <DateRange
                  editableDateInputs={true}
                  onChange={item => setDateRange([item.selection])}
                  moveRangeOnFirstSelection={false}
                  ranges={dateRange}
                  maxDate={new Date()}
                  locale={undefined}
                />
              </div>
              <div style={{ display: "flex", gap: 16 }}>
                {/* Metrics cards */}
                <div style={{ flex: 1, background: "#f7f7fa", borderRadius: 12, padding: 20, textAlign: "center" }}>
                  <div style={{ fontSize: 15, color: "#888" }}>Total Expenses</div>
                  <div style={{ fontSize: 28, fontWeight: 700, color: "#ff7ca3" }}>${totalAmount}</div>
                </div>
                <div style={{ flex: 1, background: "#f7f7fa", borderRadius: 12, padding: 20, textAlign: "center" }}>
                  <div style={{ fontSize: 15, color: "#888" }}>Transactions</div>
                  <div style={{ fontSize: 28, fontWeight: 700, color: "#4ecbff" }}>{mockTransactions}</div>
                </div>
                <div style={{ flex: 1, background: "#f7f7fa", borderRadius: 12, padding: 20, textAlign: "center" }}>
                  <div style={{ fontSize: 15, color: "#888" }}>Average per Transaction</div>
                  <div style={{ fontSize: 28, fontWeight: 700, color: "#5adbb5" }}>${mockAvg.toFixed(2)}</div>
                </div>
              </div>
              {/* Category ranking bar chart */}
              <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 24 }}>
                <h3 style={{ marginBottom: 12 }}>Category Spending Ranking</h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={mockCategories.slice().sort((a, b) => b.value - a.value)} layout="vertical" margin={{ left: 24, right: 24 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" width={80} />
                    <Bar dataKey="value" fill="#4ecbff">
                      {mockCategories.map((entry, idx) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
} 