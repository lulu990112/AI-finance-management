"use client";
import React, { useState } from "react";

export default function LoginForm() {
  const [success, setSuccess] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSuccess(true);
  };

  return (
    <div style={{
      background: "#fff",
      borderRadius: 12,
      boxShadow: "0 4px 32px rgba(0,0,0,0.06)",
      padding: "48px 40px",
      width: 400,
      maxWidth: "90%"
    }}>
      <h2 style={{ fontWeight: 700, fontSize: 24, marginBottom: 8 }}>Login From Here</h2>
      <div style={{ color: "#888", marginBottom: 24, fontSize: 15 }}>
        Welcome! Please confirm that you are visiting
      </div>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 18 }}>
          <label style={{ fontWeight: 600, fontSize: 15 }}>User Name <span style={{ color: "#ff4d4f" }}>*</span></label>
          <input type="text" placeholder="Your Name" style={{
            width: "100%",
            padding: "10px 12px",
            border: "1px solid #e0e0e0",
            borderRadius: 6,
            marginTop: 6,
            fontSize: 15
          }} required />
        </div>
        <div style={{ marginBottom: 18 }}>
          <label style={{ fontWeight: 600, fontSize: 15 }}>Password <span style={{ color: "#ff4d4f" }}>*</span></label>
          <input type="password" placeholder="password" style={{
            width: "100%",
            padding: "10px 12px",
            border: "1px solid #e0e0e0",
            borderRadius: 6,
            marginTop: 6,
            fontSize: 15
          }} required />
        </div>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 24
        }}>
          <label style={{ fontSize: 14 }}>
            <input type="checkbox" style={{ marginRight: 6 }} />
            Remember me!
          </label>
          <a href="#" style={{ fontSize: 14, color: "#ff4d4f" }}>Lost your password?</a>
        </div>
        <button type="submit" style={{
          width: "100%",
          background: "#ff4d4f",
          color: "#fff",
          border: "none",
          borderRadius: 6,
          padding: "12px 0",
          fontWeight: 700,
          fontSize: 16,
          cursor: "pointer",
          marginBottom: 12
        }}>LOGIN NOW</button>
        <div style={{ textAlign: "center", fontSize: 14 }}>
          New User? <a href="/register" style={{ color: "#ff4d4f" }}>Register Now</a>
        </div>
        {success && (
          <div style={{
            marginTop: 16,
            color: "#52c41a",
            fontWeight: 600,
            textAlign: "center"
          }}>
            successful
          </div>
        )}
      </form>
    </div>
  );
}