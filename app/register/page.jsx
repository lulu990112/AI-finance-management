"use client";
import Header2 from "../layout/header2";
import Footer from "../layout/footer";
import React, { useState } from "react";

export default function RegisterPage() {
  const [success, setSuccess] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSuccess(true);
  };

  return (
    <div>
      <Header2 />
      {/* 注册标题 */}
      <section style={{
        background: "#f4faff",
        padding: "48px 0 32px 0",
        borderBottom: "1px solid #f0f0f0"
      }}>
        <div className="container">
          <h1 style={{ fontSize: 36, fontWeight: 700, margin: 0 }}>Register</h1>
          <div style={{ color: "#888", marginTop: 8 }}>Create your account to get started</div>
          <div style={{ float: "right", color: "#ff4d4f", marginTop: -32 }}>
            Home - <span style={{ color: "#ff4d4f" }}>Register</span>
          </div>
        </div>
      </section>
      {/* 注册表单 */}
      <main style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "60vh",
        background: "transparent"
      }}>
        <div style={{
          background: "#fff",
          borderRadius: 12,
          boxShadow: "0 4px 32px rgba(0,0,0,0.06)",
          padding: "48px 40px",
          width: 400,
          maxWidth: "90%"
        }}>
          <h2 style={{ fontWeight: 700, fontSize: 24, marginBottom: 8 }}>Register From Here</h2>
          <div style={{ color: "#888", marginBottom: 24, fontSize: 15 }}>
            Welcome! Please fill in the information below
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
              <label style={{ fontWeight: 600, fontSize: 15 }}>Email <span style={{ color: "#ff4d4f" }}>*</span></label>
              <input type="email" placeholder="Your Email" style={{
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
              <input type="password" placeholder="Password" style={{
                width: "100%",
                padding: "10px 12px",
                border: "1px solid #e0e0e0",
                borderRadius: 6,
                marginTop: 6,
                fontSize: 15
              }} required />
            </div>
            <div style={{ marginBottom: 18 }}>
              <label style={{ fontWeight: 600, fontSize: 15 }}>Confirm Password <span style={{ color: "#ff4d4f" }}>*</span></label>
              <input type="password" placeholder="Confirm Password" style={{
                width: "100%",
                padding: "10px 12px",
                border: "1px solid #e0e0e0",
                borderRadius: 6,
                marginTop: 6,
                fontSize: 15
              }} required />
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
            }}>REGISTER NOW</button>
            <div style={{ textAlign: "center", fontSize: 14 }}>
              Already have an account? <a href="/login" style={{ color: "#ff4d4f" }}>Login</a>
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
      </main>
      <Footer />
    </div>
  );
}