'use client';
import React from "react";
import { useAuth } from "./AuthContext";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header style={{
      background: "#fff",
      borderBottom: "1px solid #f0f0f0",
      position: "sticky",
      top: 0,
      zIndex: 10,
      width: "100%"
    }}>
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: 70,
        maxWidth: 1200,
        margin: "0 auto",
        padding: "0 24px"
      }}>
        <div style={{ display: "flex", alignItems: "center" }}>
          <img src="/assets/img/logo.png" alt="LULU" style={{ height: 40, marginRight: 12 }} />
          <div>
            <span style={{ fontWeight: 700, fontSize: 22, color: "#222" }}>LULU</span>
            <div style={{ fontSize: 12, color: "#888", fontWeight: 400 }}>Your personal AI financial consultant</div>
          </div>
        </div>
        <nav>
          <ul style={{
            display: "flex",
            gap: 32,
            listStyle: "none",
            margin: 0,
            padding: 0,
            fontWeight: 500,
            fontSize: 16
          }}>
            <li><a href="/">Home</a></li>
            <li><a href="#">Page</a></li>
            <li><a href="#">Page</a></li>
          </ul>
        </nav>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {user ? (
            <>
              <div style={{ fontSize: 14, color: "#666" }}>
                欢迎，{user.username}
              </div>
              <button
                onClick={handleLogout}
                style={{
                  border: "1px solid #ff4d4f",
                  background: "#fff",
                  color: "#ff4d4f",
                  borderRadius: 6,
                  padding: "8px 16px",
                  fontWeight: 600,
                  fontSize: 14,
                  cursor: "pointer",
                  transition: "all 0.2s"
                }}
              >
                登出
              </button>
            </>
          ) : (
            <a href="/login" style={{
              border: "none",
              background: "#111",
              color: "#fff",
              borderRadius: 6,
              padding: "10px 22px",
              fontWeight: 600,
              fontSize: 15,
              textDecoration: "none",
              transition: "background 0.2s",
              boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
              display: "inline-block"
            }}>Login/Register</a>
          )}
        </div>
      </div>
    </header>
  );
} 