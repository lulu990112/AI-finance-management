"use client";
import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, BarChart, Bar } from "recharts";
import { FaExclamationTriangle, FaCheckCircle } from "react-icons/fa";

// mock data
const summaryText = "Hello, Mr. Wang! This is your June financial summary. Your total expenses decreased by 10% compared to last month, excellent! However, please note that the 'Dining' category budget is approaching its limit.";
const actionableItems = [
  {
    id: 1,
    type: "New Recurring Expense",
    desc: "We detected a new recurring charge from 'Spotify', $15/month.",
    time: "Yesterday",
    icon: <FaExclamationTriangle color="#FFA940" size={22} />,
    status: "pending"
  },
  {
    id: 2,
    type: "Unusual Large Expense",
    desc: "This week's 'Shopping' category expenses are unusual, exceeding the average by $800.",
    time: "2 days ago",
    icon: <FaExclamationTriangle color="#FFA940" size={22} />,
    status: "pending"
  }
];
const donutData = [
  { name: "Needs", value: 60, color: "#4ecbff" },
  { name: "Wants", value: 35, color: "#ff7ca3" },
  { name: "Savings", value: 5, color: "#5adbb5" }
];
const lineData = [
  { month: "Jan", spend: 150, invest: 151 },
  { month: "Feb", spend: 150, invest: 305 },
  { month: "Mar", spend: 150, invest: 470 },
  { month: "Apr", spend: 150, invest: 640 },
  { month: "May", spend: 150, invest: 820 },
  { month: "Jun", spend: 150, invest: 1000 }
];
const barData = [
  { day: "Mon", value: 200 },
  { day: "Tue", value: 180 },
  { day: "Wed", value: 220 },
  { day: "Thu", value: 210 },
  { day: "Fri", value: 420 },
  { day: "Sat", value: 150 },
  { day: "Sun", value: 120 }
];

// Category mapping
const detailMap = {
  Needs: ["Medicine", "Medical", "Bus", "Subway", "Taxi", "Daily", "Meals"],
  Wants: ["Snacks", "Drinks", "Clothing", "Electronics", "Restaurant", "Cosmetics", "Movies", "Games", "KTV"]
};
// Summary mock data
const allSubcategories = [
  { name: "Snacks", value: 500, color: "#ff7ca3" },
  { name: "Meals", value: 400, color: "#4ecbff" },
  { name: "Drinks", value: 300, color: "#ffe08f" },
  { name: "Clothing", value: 800, color: "#ff7ca3" },
  { name: "Electronics", value: 600, color: "#4ecbff" },
  { name: "Daily", value: 400, color: "#ffe08f" },
  { name: "Cosmetics", value: 350, color: "#a084e8" },
  { name: "Medicine", value: 120, color: "#a084e8" },
  { name: "Medical", value: 80, color: "#4ecbff" },
  { name: "Bus", value: 200, color: "#4ecbff" },
  { name: "Subway", value: 300, color: "#5adbb5" },
  { name: "Taxi", value: 300, color: "#a084e8" },
  { name: "Restaurant", value: 350, color: "#faad14" },
  { name: "Movies", value: 200, color: "#5adbb5" },
  { name: "Games", value: 100, color: "#ff7ca3" },
  { name: "KTV", value: 100, color: "#a084e8" }
];

export default function AIReportPage() {
  const [actions, setActions] = useState(actionableItems);
  const [showDetail, setShowDetail] = useState(false);
  const handleAction = (id, actionType) => {
    setActions(prev => prev.map(item => item.id === id ? { ...item, status: "done", actionType } : item));
  };
  // Category grouping
  const needList = allSubcategories.filter(s => detailMap["Needs"].includes(s.name));
  const wantList = allSubcategories.filter(s => detailMap["Wants"].includes(s.name));
  return (
    <div style={{ background: "#f7fafd", minHeight: "100vh", fontFamily: 'PingFang SC, Segoe UI, Arial, sans-serif' }}>
      <Navbar />
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 8px 48px 8px" }}>
        {/* Top global summary */}
        <div style={{ background: "linear-gradient(90deg,#e0f7fa,#f7fafd 80%)", borderRadius: 16, padding: "28px 32px", marginBottom: 28, display: "flex", alignItems: "center", boxShadow: "0 2px 12px #e0e0e0" }}>
          <span style={{ fontSize: 22, fontWeight: 700, color: "#222", marginRight: 18 }}>Financial Health Summary</span>
          <span style={{ fontSize: 18, color: "#4ecbff", fontWeight: 600 }}>{summaryText}</span>
        </div>
        {/* Pending items area */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 16, color: "#222" }}>Pending Items</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 18 }}>
            {actions.length === 0 && <div style={{ color: "#888", fontSize: 16 }}>No pending items</div>}
            {actions.map(item => (
              <div key={item.id} style={{
                minWidth: 320,
                background: item.status === "done" ? "#f7fafd" : "#fffbe6",
                borderRadius: 12,
                boxShadow: "0 2px 8px #ffe08f55",
                borderLeft: `6px solid ${item.status === "done" ? '#b7eb8f' : '#ffec3d'}`,
                display: "flex",
                alignItems: "flex-start",
                padding: "18px 20px 18px 18px",
                position: "relative"
              }}>
                <div style={{ marginRight: 14, marginTop: 2 }}>{item.status === "done" ? <FaCheckCircle color="#52c41a" size={22} /> : item.icon}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 17, color: item.status === "done" ? "#888" : "#faad14" }}>{item.type}</div>
                  <div style={{ color: "#222", fontSize: 15, margin: "6px 0 10px 0" }}>{item.desc}</div>
                  <div style={{ display: "flex", gap: 10 }}>
                    {item.status === "pending" ? <>
                      <button onClick={() => handleAction(item.id, "confirm")} style={{ background: "#4ecbff", color: "#fff", border: "none", borderRadius: 6, padding: "4px 14px", fontWeight: 600, cursor: "pointer" }}>Confirm Subscription</button>
                      <button onClick={() => handleAction(item.id, "notme")} style={{ background: "#fff", color: "#faad14", border: "1.5px solid #faad14", borderRadius: 6, padding: "4px 14px", fontWeight: 600, cursor: "pointer" }}>Not My Payment</button>
                    </> : <span style={{ color: "#52c41a", fontWeight: 600 }}>Processed</span>}
                  </div>
                  <div style={{ color: "#aaa", fontSize: 13, marginTop: 6 }}>{item.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        {/* Insight cards grid */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
          gap: 28
        }}>
          {/* Card A: Spending Attribution */}
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, display: "flex", flexDirection: "column", alignItems: "center", minHeight: 340 }}>
            <div style={{ fontWeight: 700, fontSize: 20, color: "#222", marginBottom: 10 }}>Needs vs. Wants</div>
            <div style={{ width: 180, height: 180, marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={donutData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={55} outerRadius={80}
                    labelLine={false}
                  >
                    {donutData.map((entry, idx) => <Cell key={entry.name} fill={entry.color} />)}
                  </Pie>
                  <Tooltip formatter={(value, name) => [`${value}%`, name]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ color: "#888", fontSize: 15, textAlign: "center", marginTop: 6 }}>60% of your expenses this month are for necessities, your financial structure is quite healthy!</div>
            <div style={{ marginTop: 10, color: "#4ecbff", fontSize: 15, cursor: "pointer" }} onClick={()=>setShowDetail(true)}>View Detailed Categories</div>
          </div>
          {/* Card B: AI Financial Guidance */}
          <div style={{ background: "linear-gradient(120deg,#f7fafd 60%,#e6f7ff 100%)", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, display: "flex", flexDirection: "column", alignItems: "center", minHeight: 340 }}>
            <div style={{ fontWeight: 700, fontSize: 20, color: "#222", marginBottom: 10 }}>Money Saving Tip: Cut Coffee Expenses?</div>
            <div style={{ width: 220, height: 120, marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={lineData} margin={{ left: 0, right: 0, top: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" hide />
                  <YAxis hide />
                  <Line type="monotone" dataKey="invest" stroke="#5adbb5" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="spend" stroke="#ff7ca3" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div style={{ color: "#888", fontSize: 15, textAlign: "center", marginTop: 6 }}>Your monthly coffee expenses are about <span style={{ color: "#ff7ca3", fontWeight: 700 }}>$150</span>. If you invest this money instead, it could grow to over <span style={{ color: "#5adbb5", fontWeight: 700 }}>$25,000</span> in 10 years.</div>
            <div style={{ marginTop: 10, color: "#5adbb5", fontSize: 15, cursor: "pointer" }}>Learn More</div>
          </div>
          {/* Card C: Spending Pattern */}
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, display: "flex", flexDirection: "column", alignItems: "center", minHeight: 340 }}>
            <div style={{ fontWeight: 700, fontSize: 20, color: "#222", marginBottom: 10 }}>My Spending Habits</div>
            <div style={{ width: 220, height: 120, marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ left: 0, right: 0, top: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis hide />
                  <Bar dataKey="value" fill="#4ecbff" radius={[8, 8, 0, 0]}>
                    {barData.map((entry, idx) => <Cell key={entry.day} fill={entry.day === "Fri" ? "#ff7ca3" : "#4ecbff"} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ color: "#888", fontSize: 15, textAlign: "center", marginTop: 6 }}>Data shows that most of your shopping and entertainment expenses are concentrated on <span style={{ color: "#ff7ca3", fontWeight: 700 }}>Friday evenings</span>.</div>
          </div>
        </div>
        {/* Refresh and sync prompt */}
        <div style={{ marginTop: 36, textAlign: "center", color: "#aaa", fontSize: 15 }}>
          <button style={{ background: "#4ecbff", color: "#fff", border: "none", borderRadius: 8, padding: "8px 28px", fontWeight: 700, fontSize: 16, cursor: "pointer", marginRight: 18 }}>Manual Refresh</button>
          Data synced: 5 minutes ago
        </div>
        {/* Detailed category popup */}
        {showDetail && (
          <div style={{
            position: "fixed", left: 0, top: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.18)", zIndex: 1000,
            display: "flex", alignItems: "center", justifyContent: "center"
          }}>
            <div style={{ background: "#fff", borderRadius: 18, boxShadow: "0 4px 32px #aaa6", padding: 36, minWidth: 340, maxWidth: 520 }}>
              <div style={{ fontWeight: 800, fontSize: 22, marginBottom: 18, color: "#222" }}>Detailed Categories</div>
              <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 18, color: "#4ecbff", marginBottom: 10 }}>Needs</div>
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {needList.map(sub => (
                      <li key={sub.name} style={{ display: "flex", alignItems: "center", marginBottom: 10 }}>
                        <span style={{ display: "inline-block", minWidth: 60, fontWeight: 600, color: "#4ecbff", background: "#4ecbff22", borderRadius: 8, padding: "4px 14px", marginRight: 14 }}>{sub.name}</span>
                        <span style={{ fontWeight: 700, color: "#4ecbff", fontSize: 16 }}>${sub.value}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 18, color: "#ff7ca3", marginBottom: 10 }}>Wants</div>
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {wantList.map(sub => (
                      <li key={sub.name} style={{ display: "flex", alignItems: "center", marginBottom: 10 }}>
                        <span style={{ display: "inline-block", minWidth: 60, fontWeight: 600, color: "#ff7ca3", background: "#ff7ca322", borderRadius: 8, padding: "4px 14px", marginRight: 14 }}>{sub.name}</span>
                        <span style={{ fontWeight: 700, color: "#ff7ca3", fontSize: 16 }}>${sub.value}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <div style={{ textAlign: "center", marginTop: 24 }}>
                <button onClick={()=>setShowDetail(false)} style={{ background: "#4ecbff", color: "#fff", border: "none", borderRadius: 8, padding: "8px 32px", fontWeight: 700, fontSize: 16, cursor: "pointer" }}>Close</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 