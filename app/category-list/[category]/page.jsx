"use client";
import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Navbar from "../../components/Navbar";
import LoadingSpinner from "../../components/LoadingSpinner";
import ErrorMessage from "../../components/ErrorMessage";
import { getCategoryDetail } from "../../services/api";

// 回退的mock数据，当API失败时使用
const fallbackData = {
  Dining: {
    total: 1200,
    subcategories: [
      { name: "Snacks", value: 500, color: "#ff7ca3" },
      { name: "Meals", value: 400, color: "#4ecbff" },
      { name: "Drinks", value: 300, color: "#ffe08f" },
    ],
    transactions: [
      { id: 1, date: "2024-06-01", subcategory: "Snacks", amount: 50, note: "Chips" },
      { id: 2, date: "2024-06-02", subcategory: "Drinks", amount: 30, note: "Starbucks" },
      { id: 3, date: "2024-06-03", subcategory: "Meals", amount: 80, note: "Hotpot" },
    ]
  },
  Transport: {
    total: 800,
    subcategories: [
      { name: "Bus", value: 200, color: "#4ecbff" },
      { name: "Subway", value: 300, color: "#5adbb5" },
      { name: "Taxi", value: 300, color: "#a084e8" },
    ],
    transactions: [
      { id: 4, date: "2024-06-01", subcategory: "Bus", amount: 2, note: "To work" },
      { id: 5, date: "2024-06-02", subcategory: "Subway", amount: 5, note: "Travel" },
    ]
  },
  Shopping: {
    total: 1800,
    subcategories: [
      { name: "Clothing", value: 800, color: "#ff7ca3" },
      { name: "Electronics", value: 600, color: "#4ecbff" },
      { name: "Daily", value: 400, color: "#ffe08f" },
      { name: "Cosmetics", value: 350, color: "#a084e8" },
    ],
    transactions: [
      { id: 6, date: "2024-06-01", subcategory: "Clothing", amount: 200, note: "T-shirt" },
      { id: 7, date: "2024-06-02", subcategory: "Electronics", amount: 600, note: "Headphones" },
      { id: 8, date: "2024-06-03", subcategory: "Daily", amount: 100, note: "Laundry detergent" },
      { id: 11, date: "2024-06-04", subcategory: "Cosmetics", amount: 200, note: "Face mask" },
      { id: 12, date: "2024-06-05", subcategory: "Cosmetics", amount: 150, note: "Lipstick" },
    ]
  },
  Entertainment: {
    total: 400,
    subcategories: [
      { name: "Movies", value: 200, color: "#5adbb5" },
      { name: "Games", value: 100, color: "#ff7ca3" },
      { name: "KTV", value: 100, color: "#a084e8" },
    ],
    transactions: [
      { id: 9, date: "2024-06-01", subcategory: "Movies", amount: 50, note: "Cinema" },
    ]
  },
  Healthcare: {
    total: 200,
    subcategories: [
      { name: "Medicine", value: 120, color: "#a084e8" },
      { name: "Medical", value: 80, color: "#4ecbff" },
    ],
    transactions: [
      { id: 10, date: "2024-06-01", subcategory: "Medicine", amount: 60, note: "Cold medicine" },
    ]
  },
};

export default function CategoryDetailPage() {
  const params = useParams();
  const category = decodeURIComponent(params.category);
  
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategoryData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('🔍 开始获取分类数据:', category);
        
        // 尝试从API获取数据
        const apiData = await getCategoryDetail(category);
        
        if (apiData) {
          console.log('✅ 成功获取API数据:', apiData);
          setData(apiData);
        } else {
          // API返回null，使用回退数据
          console.log('⚠️ API返回null，使用回退数据');
          const fallback = fallbackData[category];
          if (fallback) {
            setData(fallback);
          } else {
            setError('未找到该分类的数据');
          }
        }
      } catch (err) {
        console.error('❌ 获取分类数据失败:', err);
        
        // 使用回退数据
        const fallback = fallbackData[category];
        if (fallback) {
          console.log('🔄 使用回退数据');
          setData(fallback);
        } else {
          setError(err.message || '获取数据失败');
        }
      } finally {
        setLoading(false);
      }
    };

    if (category) {
      fetchCategoryData();
    }
  }, [category]);

  // 如果还在加载中
  if (loading) {
    return (
      <div style={{ background: "#f4faff", minHeight: "100vh" }}>
        <Navbar />
        <div style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
          <div style={{ textAlign: "center", padding: "40px" }}>
            <LoadingSpinner size="large" />
            <div style={{ marginTop: 16, color: "#666" }}>Loading...</div>
          </div>
        </div>
      </div>
    );
  }

  // 如果有错误
  if (error) {
    return (
      <div style={{ background: "#f4faff", minHeight: "100vh" }}>
        <Navbar />
        <div style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
          <div style={{ textAlign: "center", padding: "40px" }}>
            <ErrorMessage 
              message={error} 
              onRetry={() => window.location.reload()} 
            />
          </div>
        </div>
      </div>
    );
  }

  // 如果没有数据
  if (!data) {
    return (
      <div style={{ background: "#f4faff", minHeight: "100vh" }}>
        <Navbar />
        <div style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
          <div style={{ textAlign: "center", padding: "40px" }}>
            <div style={{ color: "#666", fontSize: 18 }}>未找到该分类的数据</div>
          </div>
        </div>
      </div>
    );
  }

  const total = data.total || 1;

  return (
    <div style={{ background: "#f4faff", minHeight: "100vh" }}>
      <Navbar />
      <div style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
        {/* Colored title bar */}
        <div style={{ display: "flex", alignItems: "center", marginBottom: 28 }}>
          <div style={{ width: 8, height: 40, borderRadius: 6, background: "linear-gradient(180deg,#4ecbff,#ff7ca3,#ffe08f,#5adbb5,#a084e8)", marginRight: 16 }} />
          <h1 style={{ fontSize: 36, fontWeight: 800, color: "#222", letterSpacing: 2, margin: 0 }}>{category} <span style={{ fontSize: 22, fontWeight: 600, color: "#4ecbff" }}>Total: ${data.total.toFixed(2)}</span></h1>
        </div>
        {/* Subcategory details */}
        <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28, marginBottom: 32 }}>
          <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 18, color: "#222" }}>Subcategory Details</h2>
          {data.subcategories && data.subcategories.length > 0 ? (
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
                  <span style={{ fontWeight: 700, color: sub.color, fontSize: 18 }}>${sub.value.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div style={{ color: "#666", textAlign: "center", padding: "20px" }}>
              暂无子分类数据
            </div>
          )}
        </div>
        {/* Transaction details */}
        <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #e0e0e0", padding: 28 }}>
          <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 18, color: "#222" }}>Transaction Details</h2>
          {data.transactions && data.transactions.length > 0 ? (
            <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: 0, background: "#fff", borderRadius: 12, overflow: "hidden" }}>
              <thead>
                <tr style={{ background: "#f4faff", color: "#888", fontWeight: 700 }}>
                  <th style={{ padding: "12px 8px", textAlign: "left" }}>Date</th>
                  <th style={{ padding: "12px 8px", textAlign: "left" }}>Subcategory</th>
                  <th style={{ padding: "12px 8px", textAlign: "left" }}>Amount</th>
                  <th style={{ padding: "12px 8px", textAlign: "left" }}>Note</th>
                </tr>
              </thead>
              <tbody>
                {data.transactions.map((tx, idx) => (
                  <tr key={tx.id || idx} style={{ background: idx % 2 === 0 ? "#f7fafd" : "#fff", transition: "background 0.2s" }}>
                    <td style={{ padding: "10px 8px" }}>{tx.date}</td>
                    <td style={{ padding: "10px 8px", color: data.subcategories?.find(s => s.name === tx.subcategory)?.color || "#222", fontWeight: 600 }}>{tx.subcategory}</td>
                    <td style={{ padding: "10px 8px", fontWeight: 700, color: "#4ecbff" }}>${tx.amount.toFixed(2)}</td>
                    <td style={{ padding: "10px 8px" }}>{tx.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ color: "#666", textAlign: "center", padding: "20px" }}>
              暂无交易记录
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 