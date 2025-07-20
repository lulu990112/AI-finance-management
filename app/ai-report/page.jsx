"use client";
import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, BarChart, Bar } from "recharts";
import { FaExclamationTriangle, FaCheckCircle } from "react-icons/fa";

// mock数据
const summaryText = "你好，王先生！这是您6月的财务摘要。您的总支出比上月减少了10%，非常棒！不过请留意，“餐饮”类别的预算已经接近上限了哦。";
const actionableItems = [
  {
    id: 1,
    type: "新增固定支出",
    desc: "我们检测到一笔来自‘Spotify’的新的周期性扣费，¥15/月。",
    time: "昨天",
    icon: <FaExclamationTriangle color="#FFA940" size={22} />,
    status: "pending"
  },
  {
    id: 2,
    type: "异常大额支出",
    desc: "本周“购物”类别支出异常，超出平均水平¥800。",
    time: "2天前",
    icon: <FaExclamationTriangle color="#FFA940" size={22} />,
    status: "pending"
  }
];
const donutData = [
  { name: "需求", value: 60, color: "#4ecbff" },
  { name: "欲望", value: 35, color: "#ff7ca3" },
  { name: "储蓄", value: 5, color: "#5adbb5" }
];
const lineData = [
  { month: "1月", spend: 150, invest: 151 },
  { month: "2月", spend: 150, invest: 305 },
  { month: "3月", spend: 150, invest: 470 },
  { month: "4月", spend: 150, invest: 640 },
  { month: "5月", spend: 150, invest: 820 },
  { month: "6月", spend: 150, invest: 1000 }
];
const barData = [
  { day: "周一", value: 200 },
  { day: "周二", value: 180 },
  { day: "周三", value: 220 },
  { day: "周四", value: 210 },
  { day: "周五", value: 420 },
  { day: "周六", value: 150 },
  { day: "周日", value: 120 }
];

// 分类映射
const detailMap = {
  需求: ["药品", "挂号", "公交", "地铁", "打车", "日用品", "正餐"],
  欲望: ["零食", "饮品", "服饰", "电子产品", "餐厅", "化妆品", "电影", "游戏", "KTV"]
};
// 汇总mock数据
const allSubcategories = [
  { name: "零食", value: 500, color: "#ff7ca3" },
  { name: "正餐", value: 400, color: "#4ecbff" },
  { name: "饮品", value: 300, color: "#ffe08f" },
  { name: "服饰", value: 800, color: "#ff7ca3" },
  { name: "电子产品", value: 600, color: "#4ecbff" },
  { name: "日用品", value: 400, color: "#ffe08f" },
  { name: "化妆品", value: 350, color: "#a084e8" },
  { name: "药品", value: 120, color: "#a084e8" },
  { name: "挂号", value: 80, color: "#4ecbff" },
  { name: "公交", value: 200, color: "#4ecbff" },
  { name: "地铁", value: 300, color: "#5adbb5" },
  { name: "打车", value: 300, color: "#a084e8" },
  { name: "餐厅", value: 350, color: "#faad14" },
  { name: "电影", value: 200, color: "#5adbb5" },
  { name: "游戏", value: 100, color: "#ff7ca3" },
  { name: "KTV", value: 100, color: "#a084e8" }
];

export default function AIReportPage() {
  const [actions, setActions] = useState(actionableItems);
  const [showDetail, setShowDetail] = useState(false);
  const handleAction = (id, actionType) => {
    setActions(prev => prev.map(item => item.id === id ? { ...item, status: "done", actionType } : item));
  };
  // 分类分组
  const needList = allSubcategories.filter(s => detailMap["需求"].includes(s.name));
  const wantList = allSubcategories.filter(s => detailMap["欲望"].includes(s.name));
  return (
    <div style={{ background: "#f7fafd", minHeight: "100vh", fontFamily: 'PingFang SC, Segoe UI, Arial, sans-serif' }}>
      <Navbar />
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 8px 48px 8px" }}>
        {/* 顶部全局摘要 */}
        <div style={{ background: "linear-gradient(90deg,#e0f7fa,#f7fafd 80%)", borderRadius: 16, padding: "28px 32px", marginBottom: 28, display: "flex", alignItems: "center", boxShadow: "0 2px 12px #e0e0e0" }}>
          <span style={{ fontSize: 22, fontWeight: 700, color: "#222", marginRight: 18 }}>财务健康摘要</span>
          <span style={{ fontSize: 18, color: "#4ecbff", fontWeight: 600 }}>{summaryText}</span>
        </div>
        {/* 待处理区域 */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 16, color: "#222" }}>待处理事项</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 18 }}>
            {actions.length === 0 && <div style={{ color: "#888", fontSize: 16 }}>暂无待处理事项</div>}
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
                      <button onClick={() => handleAction(item.id, "confirm")} style={{ background: "#4ecbff", color: "#fff", border: "none", borderRadius: 6, padding: "4px 14px", fontWeight: 600, cursor: "pointer" }}>确认订阅</button>
                      <button onClick={() => handleAction(item.id, "notme")} style={{ background: "#fff", color: "#faad14", border: "1.5px solid #faad14", borderRadius: 6, padding: "4px 14px", fontWeight: 600, cursor: "pointer" }}>不是我付的</button>
                    </> : <span style={{ color: "#52c41a", fontWeight: 600 }}>已处理</span>}
                  </div>
                  <div style={{ color: "#aaa", fontSize: 13, marginTop: 6 }}>{item.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        {/* 洞察卡片网格 */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
          gap: 28
        }}>
          {/* 卡片A：消费归因 */}
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, display: "flex", flexDirection: "column", alignItems: "center", minHeight: 340 }}>
            <div style={{ fontWeight: 700, fontSize: 20, color: "#222", marginBottom: 10 }}>需求 vs. 欲望</div>
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
            <div style={{ color: "#888", fontSize: 15, textAlign: "center", marginTop: 6 }}>您本月60%的支出用于生活必需，财务结构比较健康！</div>
            <div style={{ marginTop: 10, color: "#4ecbff", fontSize: 15, cursor: "pointer" }} onClick={()=>setShowDetail(true)}>展开详细分类</div>
          </div>
          {/* 卡片B：AI财务指导 */}
          <div style={{ background: "linear-gradient(120deg,#f7fafd 60%,#e6f7ff 100%)", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, display: "flex", flexDirection: "column", alignItems: "center", minHeight: 340 }}>
            <div style={{ fontWeight: 700, fontSize: 20, color: "#222", marginBottom: 10 }}>省钱妙计：削减咖啡开支？</div>
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
            <div style={{ color: "#888", fontSize: 15, textAlign: "center", marginTop: 6 }}>您每月在咖啡上的开销约为 <span style={{ color: "#ff7ca3", fontWeight: 700 }}>¥150</span>。如果将这笔钱用于投资，10年后可能增长到 <span style={{ color: "#5adbb5", fontWeight: 700 }}>¥25,000</span> 以上。</div>
            <div style={{ marginTop: 10, color: "#5adbb5", fontSize: 15, cursor: "pointer" }}>了解详情</div>
          </div>
          {/* 卡片C：消费模式 */}
          <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, display: "flex", flexDirection: "column", alignItems: "center", minHeight: 340 }}>
            <div style={{ fontWeight: 700, fontSize: 20, color: "#222", marginBottom: 10 }}>我的消费习惯</div>
            <div style={{ width: 220, height: 120, marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ left: 0, right: 0, top: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis hide />
                  <Bar dataKey="value" fill="#4ecbff" radius={[8, 8, 0, 0]}>
                    {barData.map((entry, idx) => <Cell key={entry.day} fill={entry.day === "周五" ? "#ff7ca3" : "#4ecbff"} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ color: "#888", fontSize: 15, textAlign: "center", marginTop: 6 }}>数据显示，您的大部分购物和娱乐消费都集中在 <span style={{ color: "#ff7ca3", fontWeight: 700 }}>周五晚上</span>。</div>
          </div>
        </div>
        {/* 刷新与同步提示 */}
        <div style={{ marginTop: 36, textAlign: "center", color: "#aaa", fontSize: 15 }}>
          <button style={{ background: "#4ecbff", color: "#fff", border: "none", borderRadius: 8, padding: "8px 28px", fontWeight: 700, fontSize: 16, cursor: "pointer", marginRight: 18 }}>手动刷新</button>
          数据同步于：5分钟前
        </div>
        {/* 详细分类弹窗 */}
        {showDetail && (
          <div style={{
            position: "fixed", left: 0, top: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.18)", zIndex: 1000,
            display: "flex", alignItems: "center", justifyContent: "center"
          }}>
            <div style={{ background: "#fff", borderRadius: 18, boxShadow: "0 4px 32px #aaa6", padding: 36, minWidth: 340, maxWidth: 520 }}>
              <div style={{ fontWeight: 800, fontSize: 22, marginBottom: 18, color: "#222" }}>详细分类</div>
              <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 18, color: "#4ecbff", marginBottom: 10 }}>需求类</div>
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {needList.map(sub => (
                      <li key={sub.name} style={{ display: "flex", alignItems: "center", marginBottom: 10 }}>
                        <span style={{ display: "inline-block", minWidth: 60, fontWeight: 600, color: "#4ecbff", background: "#4ecbff22", borderRadius: 8, padding: "4px 14px", marginRight: 14 }}>{sub.name}</span>
                        <span style={{ fontWeight: 700, color: "#4ecbff", fontSize: 16 }}>¥{sub.value}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 18, color: "#ff7ca3", marginBottom: 10 }}>欲望类</div>
                  <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                    {wantList.map(sub => (
                      <li key={sub.name} style={{ display: "flex", alignItems: "center", marginBottom: 10 }}>
                        <span style={{ display: "inline-block", minWidth: 60, fontWeight: 600, color: "#ff7ca3", background: "#ff7ca322", borderRadius: 8, padding: "4px 14px", marginRight: 14 }}>{sub.name}</span>
                        <span style={{ fontWeight: 700, color: "#ff7ca3", fontSize: 16 }}>¥{sub.value}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <div style={{ textAlign: "center", marginTop: 24 }}>
                <button onClick={()=>setShowDetail(false)} style={{ background: "#4ecbff", color: "#fff", border: "none", borderRadius: 8, padding: "8px 32px", fontWeight: 700, fontSize: 16, cursor: "pointer" }}>关闭</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 