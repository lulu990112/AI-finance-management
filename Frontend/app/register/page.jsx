"use client";
import Navbar from "../components/Navbar";
import { useAuth } from "../components/AuthContext";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: ""
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation logic
    if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) {
      setError("Please fill in all required fields");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    // Call backend API
    try {
      const res = await fetch("http://127.0.0.1:8000/api/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          confirmPassword: formData.confirmPassword
        })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        setSuccess(true);
        login(data.data.user, data.data.token); // 存储登录信息和token
        setTimeout(() => {
          router.push("/");
        }, 2000);
      } else {
        // Show backend errors in detail
        let errorMsg = data.message || "Registration failed";
        if (data.errors) {
          errorMsg += ": ";
          errorMsg += Object.entries(data.errors)
            .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
            .join("; ");
        }
        setError(errorMsg);
      }
    } catch (err) {
      setError("Request failed: " + err.message);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div>
      <Navbar />
      {/* Register title */}
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
      {/* Register form */}
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
              <label style={{ fontWeight: 600, fontSize: 15 }}>Email <span style={{ color: "#ff4d4f" }}>*</span></label>
              <input 
                type="email" 
                name="email"
                placeholder="Your Email" 
                value={formData.email}
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
                placeholder="Password" 
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
            <div style={{ marginBottom: 18 }}>
              <label style={{ fontWeight: 600, fontSize: 15 }}>Confirm Password <span style={{ color: "#ff4d4f" }}>*</span></label>
              <input 
                type="password" 
                name="confirmPassword"
                placeholder="Confirm Password" 
                value={formData.confirmPassword}
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
                Registration successful! Redirecting to homepage...
              </div>
            )}
          </form>
        </div>
      </main>
    </div>
  );
}