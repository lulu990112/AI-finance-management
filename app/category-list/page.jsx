"use client";
import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import Link from "next/link";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import { getCategorySummary } from "../services/api";

export default function CategoryListPage() {
  const [categoryData, setCategoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 默认分类数据（当API数据不可用时）
  const defaultCategories = [
    { name: "Dining", color: "#ff7ca3", value: 1200 },
    { name: "Transport", color: "#4ecbff", value: 800 },
    { name: "Shopping", color: "#ffe08f", value: 600 },
    { name: "Entertainment", color: "#5adbb5", value: 400 },
    { name: "Healthcare", color: "#a084e8", value: 200 },
  ];

  useEffect(() => {
    const fetchCategoryData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('🔍 开始获取分类汇总数据...');
        
        // 尝试从API获取数据
        const apiData = await getCategorySummary();
        
        if (apiData && apiData.length > 0) {
          console.log('✅ 成功获取API数据:', apiData);
          setCategoryData(apiData);
        } else {
          // API返回空数据，使用默认数据
          console.log('⚠️ API返回空数据，使用默认数据');
          setCategoryData(defaultCategories);
        }
      } catch (err) {
        console.error('❌ 获取分类数据失败:', err);
        
        // 使用默认数据
        console.log('🔄 使用默认数据');
        setCategoryData(defaultCategories);
      } finally {
        setLoading(false);
      }
    };

    fetchCategoryData();
  }, []);

  // 格式化分类数据
  const formatCategoryData = (categories) => {
    return categories.map(cat => ({
      name: cat.name || cat.category,
      color: cat.color || "#666",
      value: parseFloat(cat.total_amount || cat.value || 0).toFixed(2)
    }));
  };

  // 使用真实数据或默认数据
  const displayCategories = formatCategoryData(categoryData);

  return (
    <div style={{ background: "#f4faff", minHeight: "100vh" }}>
      <Navbar />
      <div style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, marginBottom: 24 }}>Category List</h1>
        
        {loading && (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <LoadingSpinner size="large" />
            <div style={{ marginTop: 16, color: "#666" }}>Loading...</div>
          </div>
        )}
        
        {error && (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <ErrorMessage message={error} onRetry={() => window.location.reload()} />
          </div>
        )}
        
        {!loading && !error && (
          <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
            {displayCategories.map(cat => (
              <Link
                key={cat.name}
                href={`/category-list/${cat.name}`}
                style={{
                  flex: "1 1 220px",
                  minWidth: 220,
                  background: "#fff",
                  borderRadius: 16,
                  boxShadow: "0 2px 12px #e0e0e0",
                  padding: 32,
                  textAlign: "center",
                  textDecoration: "none",
                  color: "#222",
                  fontWeight: 600,
                  fontSize: 22,
                  marginBottom: 24,
                  transition: "box-shadow 0.2s, transform 0.2s",
                  cursor: "pointer"
                }}
              >
                <div style={{ marginBottom: 12 }}>{cat.name}</div>
                <div style={{ color: cat.color, fontSize: 28 }}>${cat.value}</div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 