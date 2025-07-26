"use client";
import React from "react";
import Navbar from "../components/Navbar";
import Link from "next/link";

const categories = [
  { name: "Dining", color: "#ff7ca3", value: 1200 },
  { name: "Transport", color: "#4ecbff", value: 800 },
  { name: "Shopping", color: "#ffe08f", value: 600 },
  { name: "Entertainment", color: "#5adbb5", value: 400 },
  { name: "Healthcare", color: "#a084e8", value: 200 },
];

export default function CategoryListPage() {
  return (
    <div style={{ background: "#f4faff", minHeight: "100vh" }}>
      <Navbar />
      <div style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, marginBottom: 24 }}>Category List</h1>
        <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
          {categories.map(cat => (
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
      </div>
    </div>
  );
} 