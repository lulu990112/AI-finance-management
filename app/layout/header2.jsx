"use client";
import React from "react";
import { useRouter } from "next/navigation";

export default function Header2() {
  const router = useRouter();
  return (
    <header style={{
      background: "#fff",
      borderBottom: "1px solid #f0f0f0",
      position: "sticky",
      top: 0,
      zIndex: 10
    }}>
      <div className="container" style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: 70
      }}>
        <div style={{ display: "flex", alignItems: "center" }}>
          <img src="/assets/img/logo.png" alt="LULU" style={{ height: 40, marginRight: 12 }} />
          <span style={{ fontWeight: 700, fontSize: 24, color: "#222" }}>LULU</span>
        </div>
        <nav style={{ flex: 1, marginLeft: 40 }}>
          <ul style={{
            display: "flex",
            gap: 32,
            listStyle: "none",
            margin: 0,
            padding: 0,
            fontWeight: 500,
            fontSize: 16
          }}>
            <li><a href="#">HOME</a></li>
            <li><a href="#">PAGES</a></li>
            <li><a href="#">PORTFOLIO</a></li>
            <li><a href="#">ELEMENTS</a></li>
            <li><a href="#">BLOG</a></li>
            <li><a href="#">SHOP</a></li>
          </ul>
        </nav>
        <div>
          <button
            style={{
              border: "1px solid #ff4d4f",
              background: "#fff",
              color: "#ff4d4f",
              borderRadius: 6,
              padding: "8px 24px",
              fontWeight: 600,
              cursor: "pointer"
            }}
            onClick={() => router.push("/register")}
          >
            SIGN UP
          </button>
        </div>
      </div>
    </header>
  );
}
