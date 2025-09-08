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

  // Default category data (when API data is not available)
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
        
        console.log('🔍 Start fetching category summary data...');
        
        // Try to get data from API
        const apiData = await getCategorySummary();
        
        if (apiData && apiData.length > 0) {
          console.log('✅ Successfully got API data:', apiData);
          setCategoryData(apiData);
        } else {
          // API returns empty data, use default data
          console.log('⚠️ API returned empty data, using default data');
          setCategoryData(defaultCategories);
        }
      } catch (err) {
        console.error('❌ Failed to get category data:', err);
        
        // Use default data
        console.log('🔄 Using default data');
        setCategoryData(defaultCategories);
      } finally {
        setLoading(false);
      }
    };

    fetchCategoryData();
  }, []);

  // Format category data
  const formatCategoryData = (categories) => {
    return categories.map(cat => ({
      name: cat.name || cat.category,
      color: cat.color || "#666",
      value: parseFloat(cat.total_amount || cat.value || 0).toFixed(2)
    }));
  };

  // Use real data or default data
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