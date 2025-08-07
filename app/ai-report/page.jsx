"use client";
import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, BarChart, Bar } from "recharts";
import { FaExclamationTriangle, FaCheckCircle } from "react-icons/fa";
import { getAIReport } from "../services/api";
import { getAllTransactions } from "../services/api";

export default function AIReportPage() {
  const [aiReport, setAiReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actions, setActions] = useState([]);
  const [showDetail, setShowDetail] = useState(false);
  const [realTransactionData, setRealTransactionData] = useState(null);
  const [weeklyData, setWeeklyData] = useState(null);

  // 处理真实交易数据，按subcategory分类
  const processTransactionData = (transactions) => {
    if (!transactions || transactions.length === 0) {
      return null;
    }

    // 按subcategory分组并计算金额
    const subcategoryMap = {};
    transactions.forEach(tx => {
      const subcategoryName = typeof tx.subcategory === 'object' ? tx.subcategory.name : tx.subcategory;
      if (!subcategoryMap[subcategoryName]) {
        subcategoryMap[subcategoryName] = 0;
      }
      subcategoryMap[subcategoryName] += parseFloat(tx.amount || 0);
    });

    // 转换为数组格式
    const subcategories = Object.entries(subcategoryMap).map(([name, value]) => ({
      name,
      value: Math.round(value * 100) / 100, // 保留两位小数
      color: getDefaultSubcategoryColor(name)
    }));

    return subcategories;
  };

  // 处理周消费数据，按周一到周日分组
  const processWeeklyData = (transactions) => {
    if (!transactions || transactions.length === 0) {
      return null;
    }

    // 获取最近一周的日期范围
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay() + 1); // 设置为本周一
    startOfWeek.setHours(0, 0, 0, 0);
    
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6); // 设置为本周日
    endOfWeek.setHours(23, 59, 59, 999);

    console.log('📅 周数据范围:', startOfWeek.toISOString(), '到', endOfWeek.toISOString());

    // 按天分组交易数据
    const dailyMap = {
      'Mon': 0,
      'Tue': 0,
      'Wed': 0,
      'Thu': 0,
      'Fri': 0,
      'Sat': 0,
      'Sun': 0
    };

    // 过滤最近一周的交易
    const weeklyTransactions = transactions.filter(tx => {
      const txDate = new Date(tx.transaction_date);
      return txDate >= startOfWeek && txDate <= endOfWeek;
    });

    console.log('📊 本周交易数量:', weeklyTransactions.length);

    // 按天计算消费金额
    weeklyTransactions.forEach(tx => {
      const txDate = new Date(tx.transaction_date);
      const dayOfWeek = txDate.getDay(); // 0=周日, 1=周一, ..., 6=周六
      
      // 转换为我们的格式 (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
      const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      const dayName = dayNames[dayOfWeek];
      
      if (dailyMap.hasOwnProperty(dayName)) {
        dailyMap[dayName] += parseFloat(tx.amount || 0);
      }
    });

    // 转换为数组格式
    const weeklyData = Object.entries(dailyMap).map(([day, value]) => ({
      day,
      value: Math.round(value * 100) / 100 // 保留两位小数
    }));

    console.log('📊 周消费数据:', weeklyData);
    return weeklyData;
  };

  // 获取默认颜色
  const getDefaultSubcategoryColor = (subcategoryName) => {
    const colorMap = {
      // Needs (黑色subcategory)
      'Daily meal': '#4ecbff',
      'Snack': '#ffe08f',
      'Restaurant': '#faad14',
      'Drink': '#ffe08f',
      'Medicine': '#a084e8',
      'Medical': '#4ecbff',
      'Bus': '#4ecbff',
      'Train': '#5adbb5',
      'Taxi': '#a084e8',
      'Subway': '#5adbb5',
      'Plane': '#4ecbff',
      'User defined': '#666666',
      
      // Wants (红色subcategory)
      'Clothing': '#ff7ca3',
      'Shoes': '#ff7ca3',
      'Electronics': '#4ecbff',
      'Household': '#ffe08f',
      'Cosmetic': '#a084e8',
      'Game': '#ff7ca3',
      'Movie': '#5adbb5',
      'KTV': '#a084e8'
    };
    
    return colorMap[subcategoryName] || '#666666';
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('🤖 开始获取数据...');
        
        // 并行获取AI Report和交易数据
        const [report, transactions] = await Promise.all([
          getAIReport(),
          getAllTransactions()
        ]);
        
        if (report) {
          console.log('✅ 成功获取AI Report:', report);
          setAiReport(report);
          
          // 基于AI Report数据生成actionable items
          const actionableItems = [];
          
          if (report.abnormal_alert) {
            actionableItems.push({
              id: 1,
              type: "Abnormal Spending Alert",
              desc: report.abnormal_alert,
              time: "Today",
              icon: <FaExclamationTriangle color="#FFA940" size={22} />,
              status: "pending"
            });
          }
          
          setActions(actionableItems);
        } else {
          console.log('⚠️ 未找到AI Report数据');
          setAiReport(null);
          setActions([]);
        }

        // 处理真实交易数据
        if (transactions && transactions.length > 0) {
          console.log('✅ 成功获取交易数据:', transactions.length, '条');
          const processedData = processTransactionData(transactions);
          setRealTransactionData(processedData);
          
          // 处理周消费数据
          const weeklyData = processWeeklyData(transactions);
          setWeeklyData(weeklyData);
        } else {
          console.log('⚠️ 未找到交易数据，使用默认数据');
          setRealTransactionData(null);
          setWeeklyData(null);
        }
      } catch (err) {
        console.error('❌ 获取数据失败:', err);
        setError('获取数据失败');
        setAiReport(null);
        setActions([]);
        setRealTransactionData(null);
        setWeeklyData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAction = (id, actionType) => {
    setActions(prev => prev.map(item => item.id === id ? { ...item, status: "done", actionType } : item));
  };

  // 默认数据（当API数据不可用时）
  const defaultSummaryText = "Hello! This is your financial summary. Your total expenses are being analyzed. Please wait for the AI report to be generated.";
  
  const defaultLineData = [
    { month: "Jan", spend: 150, invest: 151 },
    { month: "Feb", spend: 150, invest: 305 },
    { month: "Mar", spend: 150, invest: 470 },
    { month: "Apr", spend: 150, invest: 640 },
    { month: "May", spend: 150, invest: 820 },
    { month: "Jun", spend: 150, invest: 1000 }
  ];
  const defaultBarData = [
    { day: "Mon", value: 200 },
    { day: "Tue", value: 180 },
    { day: "Wed", value: 220 },
    { day: "Thu", value: 210 },
    { day: "Fri", value: 420 },
    { day: "Sat", value: 150 },
    { day: "Sun", value: 120 }
  ];

  // Category mapping - 根据表格重新分类
  const detailMap = {
    Needs: [
      // 黑色subcategory (needs)
      "Daily meal", "Snack", "Restaurant", "Drink", 
      "Medicine", "Medical", 
      "Bus", "Train", "Taxi", "Subway", "Plane",
      "User defined"
    ],
    Wants: [
      // 红色subcategory (wants) 
      "Clothing", "Shoes", "Electronics", "Household", "Cosmetic",
      "Game", "Movie", "KTV"
    ]
  };

  // 使用真实交易数据或默认数据
  const allSubcategories = realTransactionData || [
    // 默认数据（当API数据不可用时）
    // Needs (黑色subcategory)
    { name: "Daily meal", value: 400, color: "#4ecbff" },
    { name: "Snack", value: 300, color: "#ffe08f" },
    { name: "Restaurant", value: 350, color: "#faad14" },
    { name: "Drink", value: 200, color: "#ffe08f" },
    { name: "Medicine", value: 120, color: "#a084e8" },
    { name: "Medical", value: 80, color: "#4ecbff" },
    { name: "Bus", value: 200, color: "#4ecbff" },
    { name: "Train", value: 150, color: "#5adbb5" },
    { name: "Taxi", value: 300, color: "#a084e8" },
    { name: "Subway", value: 300, color: "#5adbb5" },
    { name: "Plane", value: 500, color: "#4ecbff" },
    { name: "User defined", value: 100, color: "#666666" },
    
    // Wants (红色subcategory)
    { name: "Clothing", value: 800, color: "#ff7ca3" },
    { name: "Shoes", value: 400, color: "#ff7ca3" },
    { name: "Electronics", value: 600, color: "#4ecbff" },
    { name: "Household", value: 300, color: "#ffe08f" },
    { name: "Cosmetic", value: 350, color: "#a084e8" },
    { name: "Game", value: 100, color: "#ff7ca3" },
    { name: "Movie", value: 200, color: "#5adbb5" },
    { name: "KTV", value: 100, color: "#a084e8" }
  ];

  // 计算needs和wants的总金额
  const needsTotal = allSubcategories
    .filter(item => detailMap.Needs.includes(item.name))
    .reduce((sum, item) => sum + item.value, 0);
  
  const wantsTotal = allSubcategories
    .filter(item => detailMap.Wants.includes(item.name))
    .reduce((sum, item) => sum + item.value, 0);
  
  const totalAmount = needsTotal + wantsTotal;
  const needsPercentage = totalAmount > 0 ? Math.round((needsTotal / totalAmount) * 100) : 0;
  const wantsPercentage = totalAmount > 0 ? Math.round((wantsTotal / totalAmount) * 100) : 0;
  
  const defaultDonutData = [
    { name: "Needs", value: needsPercentage, color: "#4ecbff" },
    { name: "Wants", value: wantsPercentage, color: "#ff7ca3" }
  ];

  // Category grouping - 使用真实数据或默认数据
  const needList = allSubcategories.filter(s => detailMap["Needs"].includes(s.name));
  const wantList = allSubcategories.filter(s => detailMap["Wants"].includes(s.name));

  return (
    <div style={{ background: "#f7fafd", minHeight: "100vh", fontFamily: 'PingFang SC, Segoe UI, Arial, sans-serif' }}>
      <Navbar />
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 8px 48px 8px" }}>
        {/* Top global summary */}
        <div style={{ background: "linear-gradient(90deg,#e0f7fa,#f7fafd 80%)", borderRadius: 16, padding: "28px 32px", marginBottom: 28, display: "flex", alignItems: "center", boxShadow: "0 2px 12px #e0e0e0" }}>
          <div style={{ display: "flex", alignItems: "center" }}>
            <span style={{ fontSize: 22, fontWeight: 700, color: "#222", marginRight: 18 }}>Financial Health Summary</span>
            <span style={{ fontSize: 18, color: "#4ecbff", fontWeight: 600 }}>
              {loading ? "正在加载..." : error ? "加载失败" : aiReport ? aiReport.financial_advice_summary || defaultSummaryText : defaultSummaryText}
            </span>
          </div>
        </div>

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
                  <Pie data={aiReport?.donut_data || defaultDonutData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={55} outerRadius={80}
                    labelLine={false}
                  >
                    {(aiReport?.donut_data || defaultDonutData).map((entry, idx) => <Cell key={entry.name} fill={entry.color} />)}
                  </Pie>
                  <Tooltip formatter={(value, name) => [`${value}%`, name]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ color: "#888", fontSize: 15, textAlign: "center", marginTop: 6 }}>
              {aiReport?.donut_summary || `${needsPercentage}% of your expenses this month are for necessities, your financial structure is ${needsPercentage >= 60 ? 'quite healthy' : 'needs improvement'}!`}
              {realTransactionData && <span style={{ fontSize: 12, color: "#4ecbff", marginLeft: 8 }}>(实时数据)</span>}
            </div>
            <div style={{ marginTop: 10, color: "#4ecbff", fontSize: 15, cursor: "pointer" }} onClick={()=>setShowDetail(true)}>View Detailed Categories</div>
          </div>
          {/* Card B: AI Financial Guidance */}
          <div style={{ background: "linear-gradient(120deg,#f7fafd 60%,#e6f7ff 100%)", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, display: "flex", flexDirection: "column", alignItems: "center", minHeight: 340 }}>
            <div style={{ fontWeight: 700, fontSize: 20, color: "#222", marginBottom: 10 }}>Money Saving Tip: Cut Coffee Expenses?</div>
            <div style={{ width: 280, height: 140, marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={aiReport?.line_data || defaultLineData} margin={{ left: 0, right: 0, top: 10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" hide />
                  <YAxis hide />
                  <Line type="monotone" dataKey="invest" stroke="#5adbb5" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="spend" stroke="#ff7ca3" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div style={{ color: "#888", fontSize: 15, textAlign: "center", marginTop: 6 }}>
              {aiReport?.money_saving_tip ? (
                <>
                  {aiReport.money_saving_tip.split(' ').slice(0, 30).join(' ')}
                  {aiReport.money_saving_tip.split(' ').length > 30 && '...'}
                </>
              ) : (
                "Your monthly coffee expenses are about $150. If you invest this money instead, it could grow to over $25,000 in 10 years."
              )}
            </div>
            <a 
              href="/money-saving-tip" 
              style={{ 
                marginTop: 10, 
                color: "#5adbb5", 
                fontSize: 15, 
                cursor: "pointer",
                textDecoration: "none",
                fontWeight: 600
              }}
            >
              Learn More
            </a>
          </div>
          {/* Card C: Spending Pattern */}
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, display: "flex", flexDirection: "column", alignItems: "center", minHeight: 340 }}>
            <div style={{ fontWeight: 700, fontSize: 20, color: "#222", marginBottom: 10 }}>Weekly Spending Pattern</div>
            <div style={{ width: 220, height: 120, marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weeklyData || defaultBarData} margin={{ left: 0, right: 0, top: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis hide />
                  <Bar dataKey="value" fill="#4ecbff" radius={[8, 8, 0, 0]}>
                    {(weeklyData || defaultBarData).map((entry, idx) => (
                      <Cell key={entry.day} fill={entry.day === "Fri" ? "#ff7ca3" : "#4ecbff"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ color: "#888", fontSize: 15, textAlign: "center", marginTop: 6 }}>
              {aiReport?.bar_summary || "Data shows that most of your shopping and entertainment expenses are concentrated on Friday evenings."}
              {weeklyData && <span style={{ fontSize: 12, color: "#4ecbff", marginLeft: 8 }}>(实时数据)</span>}
            </div>
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
            <div style={{ background: "#fff", borderRadius: 18, boxShadow: "0 4px 32px #aaa6", padding: 36, minWidth: 400, maxWidth: 600 }}>
              <div style={{ fontWeight: 800, fontSize: 22, marginBottom: 18, color: "#222" }}>Detailed Categories</div>
              <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 18, color: "#4ecbff", marginBottom: 10 }}>
                    Needs
                    <span style={{ fontSize: 14, color: "#666", marginLeft: 8, fontWeight: 400 }}>
                      Total: ${needsTotal}
                    </span>
                  </div>
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {needList.map(sub => (
                      <li key={sub.name} style={{ display: "flex", alignItems: "center", marginBottom: 10 }}>
                        <span style={{ display: "inline-block", minWidth: 80, fontWeight: 600, color: "#4ecbff", background: "#4ecbff22", borderRadius: 8, padding: "4px 14px", marginRight: 14 }}>{sub.name}</span>
                        <span style={{ fontWeight: 700, color: "#4ecbff", fontSize: 16 }}>${sub.value}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 18, color: "#ff7ca3", marginBottom: 10 }}>
                    Wants
                    <span style={{ fontSize: 14, color: "#666", marginLeft: 8, fontWeight: 400 }}>
                      Total: ${wantsTotal}
                    </span>
                  </div>
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {wantList.map(sub => (
                      <li key={sub.name} style={{ display: "flex", alignItems: "center", marginBottom: 10 }}>
                        <span style={{ display: "inline-block", minWidth: 80, fontWeight: 600, color: "#ff7ca3", background: "#ff7ca322", borderRadius: 8, padding: "4px 14px", marginRight: 14 }}>{sub.name}</span>
                        <span style={{ fontWeight: 700, color: "#ff7ca3", fontSize: 16 }}>${sub.value}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <div style={{ 
                marginTop: 20, 
                padding: "16px", 
                background: "#f8f9fa", 
                borderRadius: 12,
                border: "1px solid #e9ecef"
              }}>
                <div style={{ textAlign: "center", fontSize: 16, fontWeight: 600, color: "#222" }}>
                  Total Spending: ${totalAmount}
                </div>
                <div style={{ textAlign: "center", fontSize: 14, color: "#666", marginTop: 4 }}>
                  {needsPercentage}% Needs • {wantsPercentage}% Wants
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