"use client";
import React, { useState } from "react";
import { useAuth } from "./AuthContext";
import { useRouter } from "next/navigation";

export default function LoginForm() {
  const [formData, setFormData] = useState({
    username: "",
    password: ""
  });
  const [error, setError] = useState("");
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
  
    try {
      await login(formData.username, formData.password);
      router.push("/");
    } catch (err) {
      setError(err.message || "Login failed, please try again");
    }
  };
  

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div style={{
      background: "#fff",
      borderRadius: 12,
      boxShadow: "0 4px 32px rgba(0,0,0,0.06)",
      padding: "48px 40px",
      width: "100%",
      maxWidth: "450px",
      margin: "0 auto"
    }}>
      <h2 style={{ fontWeight: 700, fontSize: 24, marginBottom: 8 }}>Login From Here</h2>
      <div style={{ color: "#888", marginBottom: 24, fontSize: 15 }}>
        Welcome! Please login to your account!
      </div>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 18 }}>
          <label style={{ fontWeight: 600, fontSize: 15 }}>User Name <span style={{ color: "#ff4d4f" }}>*</span></label>
          <input 
            type="text" 
            name="username"
            placeholder="Your Name" 
            value={formData.username}
            onChange={handleChange}
            style={{
              width: "100%",
              padding: "10px 12px",
              border: "1px solid #e0e0e0",
              borderRadius: 6,
              marginTop: 6,
              fontSize: 15
            }} 
            required 
          />
        </div>
        <div style={{ marginBottom: 18 }}>
          <label style={{ fontWeight: 600, fontSize: 15 }}>Password <span style={{ color: "#ff4d4f" }}>*</span></label>
          <input 
            type="password" 
            name="password"
            placeholder="password" 
            value={formData.password}
            onChange={handleChange}
            style={{
              width: "100%",
              padding: "10px 12px",
              border: "1px solid #e0e0e0",
              borderRadius: 6,
              marginTop: 6,
              fontSize: 15
            }} 
            required 
          />
        </div>
        {error && (
          <div style={{
            color: "#ff4d4f",
            fontSize: 14,
            marginBottom: 16,
            textAlign: "center"
          }}>
            {error}
          </div>
        )}
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
      </form>
    </div>
  );
}