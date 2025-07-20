"use client";
import React from "react";
import { useParams } from "next/navigation";
import Navbar from "../../components/Navbar";

// mock 数据，与 category-dashboard/[category]/page.jsx 保持一致
const mockData = {
  餐饮: {
    total: 1200,
    subcategories: [
      { name: "零食", value: 500, color: "#ff7ca3" },
      { name: "正餐", value: 400, color: "#4ecbff" },
      { name: "饮品", value: 300, color: "#ffe08f" },
    ],
    transactions: [
      { id: 1, date: "2024-06-01", subcategory: "零食", amount: 50, note: "薯片" },
      { id: 2, date: "2024-06-02", subcategory: "饮品", amount: 30, note: "星巴克" },
      { id: 3, date: "2024-06-03", subcategory: "正餐", amount: 80, note: "火锅" },
    ]
  },
  交通: {
    total: 800,
    subcategories: [
      { name: "公交", value: 200, color: "#4ecbff" },
      { name: "地铁", value: 300, color: "#5adbb5" },
      { name: "打车", value: 300, color: "#a084e8" },
    ],
    transactions: [
      { id: 4, date: "2024-06-01", subcategory: "公交", amount: 2, note: "上班" },
      { id: 5, date: "2024-06-02", subcategory: "地铁", amount: 5, note: "出行" },
    ]
  },
  购物: {
    total: 1800,
    subcategories: [
      { name: "服饰", value: 800, color: "#ff7ca3" },
      { name: "电子产品", value: 600, color: "#4ecbff" },
      { name: "日用品", value: 400, color: "#ffe08f" },
      { name: "化妆品", value: 350, color: "#a084e8" },
    ],
    transactions: [
      { id: 6, date: "2024-06-01", subcategory: "服饰", amount: 200, note: "T恤" },
      { id: 7, date: "2024-06-02", subcategory: "电子产品", amount: 600, note: "耳机" },
      { id: 8, date: "2024-06-03", subcategory: "日用品", amount: 100, note: "洗衣液" },
      { id: 11, date: "2024-06-04", subcategory: "化妆品", amount: 200, note: "面膜" },
      { id: 12, date: "2024-06-05", subcategory: "化妆品", amount: 150, note: "口红" },
    ]
  },
  娱乐: {
    total: 400,
    subcategories: [
      { name: "电影", value: 200, color: "#5adbb5" },
      { name: "游戏", value: 100, color: "#ff7ca3" },
      { name: "KTV", value: 100, color: "#a084e8" },
    ],
    transactions: [
      { id: 9, date: "2024-06-01", subcategory: "电影", amount: 50, note: "影院" },
    ]
  },
  医疗: {
    total: 200,
    subcategories: [
      { name: "药品", value: 120, color: "#a084e8" },
      { name: "挂号", value: 80, color: "#4ecbff" },
    ],
    transactions: [
      { id: 10, date: "2024-06-01", subcategory: "药品", amount: 60, note: "感冒药" },
    ]
  },
};

export default function CategoryDetailPage() {
  const params = useParams();
  const category = decodeURIComponent(params.category);
  const data = mockData[category] || { total: 0, subcategories: [], transactions: [] };
  const total = data.total || 1;

  return (
    <div style={{ background: "#f4faff", minHeight: "100vh" }}>
      <Navbar />
      <div style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
        {/* 彩色标题条 */}
        <div style={{ display: "flex", alignItems: "center", marginBottom: 28 }}>
          <div style={{ width: 8, height: 40, borderRadius: 6, background: "linear-gradient(180deg,#4ecbff,#ff7ca3,#ffe08f,#5adbb5,#a084e8)", marginRight: 16 }} />
          <h1 style={{ fontSize: 36, fontWeight: 800, color: "#222", letterSpacing: 2, margin: 0 }}>{category} <span style={{ fontSize: 22, fontWeight: 600, color: "#4ecbff" }}>总支出：¥{data.total}</span></h1>
        </div>
        {/* 子类别明细 */}
        <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, marginBottom: 32 }}>
          <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 18, color: "#222" }}>子类别明细</h2>
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {data.subcategories.map(sub => (
              <li key={sub.name} style={{ display: "flex", alignItems: "center", marginBottom: 18 }}>
                <span style={{
                  display: "inline-block",
                  minWidth: 60,
                  fontWeight: 600,
                  fontSize: 18,
                  color: sub.color,
                  background: sub.color + "22",
                  borderRadius: 8,
                  padding: "4px 16px",
                  marginRight: 18
                }}>{sub.name}</span>
                <div style={{ flex: 1, marginRight: 18, background: "#f4faff", borderRadius: 8, height: 12, position: "relative" }}>
                  <div style={{
                    width: `${Math.round((sub.value / total) * 100)}%`,
                    background: sub.color,
                    height: 12,
                    borderRadius: 8,
                    transition: "width 0.4s"
                  }} />
                </div>
                <span style={{ fontWeight: 700, color: sub.color, fontSize: 18 }}>¥{sub.value}</span>
              </li>
            ))}
          </ul>
        </div>
        {/* 交易明细 */}
        <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28 }}>
          <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 18, color: "#222" }}>交易明细</h2>
          <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: 0, background: "#fff", borderRadius: 12, overflow: "hidden" }}>
            <thead>
              <tr style={{ background: "#f4faff", color: "#888", fontWeight: 700 }}>
                <th style={{ padding: "12px 8px", textAlign: "left" }}>日期</th>
                <th style={{ padding: "12px 8px", textAlign: "left" }}>子类别</th>
                <th style={{ padding: "12px 8px", textAlign: "left" }}>金额</th>
                <th style={{ padding: "12px 8px", textAlign: "left" }}>备注</th>
              </tr>
            </thead>
            <tbody>
              {data.transactions.map((tx, idx) => (
                <tr key={tx.id} style={{ background: idx % 2 === 0 ? "#f7fafd" : "#fff", transition: "background 0.2s" }}>
                  <td style={{ padding: "10px 8px" }}>{tx.date}</td>
                  <td style={{ padding: "10px 8px", color: data.subcategories.find(s => s.name === tx.subcategory)?.color || "#222", fontWeight: 600 }}>{tx.subcategory}</td>
                  <td style={{ padding: "10px 8px", fontWeight: 700, color: "#4ecbff" }}>¥{tx.amount}</td>
                  <td style={{ padding: "10px 8px" }}>{tx.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
} 