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

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    // 简单的验证逻辑
    if (!formData.username || !formData.password) {
      setError("请填写用户名和密码");
      return;
    }

    // 模拟登录验证（实际项目中应该调用API）
    if (formData.username === "admin" && formData.password === "123456") {
      const userData = {
        id: 1,
        username: formData.username,
        email: "admin@example.com",
        isMember: true
      };
      login(userData);
      router.push("/");
    } else if (formData.username === "user" && formData.password === "123456") {
      const userData = {
        id: 2,
        username: formData.username,
        email: "user@example.com",
        isMember: false
      };
      login(userData);
      router.push("/");
    } else {
      setError("用户名或密码错误");
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
        <div style={{ marginTop: 16, fontSize: 12, color: "#888", textAlign: "center" }}>
          测试账号：<br />
          会员账号：admin / 123456<br />
          普通用户：user / 123456
        </div>
      </form>
    </div>
  );
}