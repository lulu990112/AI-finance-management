"use client"
import React from "react";
import { useParams } from "next/navigation";
import Navbar from "../../components/Navbar";

// mock 数据
const mockData = {
  餐饮: {
    total: 1200,
    subcategories: [
      { name: "快餐", value: 500 },
      { name: "正餐", value: 400 },
      { name: "饮品", value: 300 },
    ],
    transactions: [
      { id: 1, date: "2024-06-01", subcategory: "快餐", amount: 50, note: "麦当劳" },
      { id: 2, date: "2024-06-02", subcategory: "饮品", amount: 30, note: "星巴克" },
      { id: 3, date: "2024-06-03", subcategory: "正餐", amount: 80, note: "火锅" },
    ]
  },
  交通: {
    total: 800,
    subcategories: [
      { name: "公交", value: 200 },
      { name: "地铁", value: 300 },
      { name: "打车", value: 300 },
    ],
    transactions: [
      { id: 4, date: "2024-06-01", subcategory: "公交", amount: 2, note: "上班" },
      { id: 5, date: "2024-06-02", subcategory: "地铁", amount: 5, note: "出行" },
    ]
  },
  购物: {
    total: 1800,
    subcategories: [
      { name: "服饰", value: 800 },
      { name: "电子产品", value: 600 },
      { name: "日用品", value: 400 },
    ],
    transactions: [
      { id: 6, date: "2024-06-01", subcategory: "服饰", amount: 200, note: "T恤" },
      { id: 7, date: "2024-06-02", subcategory: "电子产品", amount: 600, note: "耳机" },
      { id: 8, date: "2024-06-03", subcategory: "日用品", amount: 100, note: "洗衣液" },
    ]
  },
  娱乐: {
    total: 400,
    subcategories: [
      { name: "电影", value: 200 },
      { name: "游戏", value: 100 },
      { name: "KTV", value: 100 },
    ],
    transactions: [
      { id: 9, date: "2024-06-01", subcategory: "电影", amount: 50, note: "影院" },
    ]
  },
  医疗: {
    total: 200,
    subcategories: [
      { name: "药品", value: 120 },
      { name: "挂号", value: 80 },
    ],
    transactions: [
      { id: 10, date: "2024-06-01", subcategory: "药品", amount: 60, note: "感冒药" },
    ]
  },
};

export default function CategoryDetailPage() {
  const params = useParams();
  // 兼容英文参数
  const categoryMap = { shopping: "购物", food: "餐饮", traffic: "交通", entertainment: "娱乐", medical: "医疗" };
  const categoryKey = categoryMap[params.category] || params.category;
  const data = mockData[categoryKey] || { total: 0, subcategories: [], transactions: [] };

  return (
    <div style={{ background: "#f4faff", minHeight: "100vh" }}>
      <Navbar />
      <div style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, marginBottom: 16 }}>
          {categoryKey} 总支出：¥{data.total}
        </h1>
        <h2 style={{ marginTop: 24, fontSize: 22 }}>子类别明细</h2>
        <ul style={{ background: "#fff", borderRadius: 12, padding: 24, margin: "16px 0", boxShadow: "0 2px 12px #e0e0e0" }}>
          {data.subcategories.map(sub => (
            <li key={sub.name} style={{ fontSize: 18, margin: "8px 0", display: "flex", justifyContent: "space-between" }}>
              <span>{sub.name}</span>
              <span>¥{sub.value}</span>
            </li>
          ))}
        </ul>
        <h2 style={{ marginTop: 24, fontSize: 22 }}>交易明细</h2>
        <table style={{ width: "100%", background: "#fff", borderRadius: 8, padding: 16, boxShadow: "0 2px 12px #e0e0e0" }}>
          <thead>
            <tr style={{ textAlign: "left" }}>
              <th>日期</th>
              <th>子类别</th>
              <th>金额</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            {data.transactions.map(tx => (
              <tr key={tx.id}>
                <td>{tx.date}</td>
                <td>{tx.subcategory}</td>
                <td>¥{tx.amount}</td>
                <td>{tx.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 