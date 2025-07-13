import React from "react";

export default function Footer() {
  return (
    <footer style={{
      background: "#fff",
      borderTop: "1px solid #f0f0f0",
      padding: "40px 0 24px 0",
      marginTop: 40
    }}>
      <div className="container" style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        flexWrap: "wrap"
      }}>
        <div style={{ flex: "1 1 180px", marginBottom: 24 }}>
          <img src="/assets/img/logo.png" alt="xisen" style={{ height: 36, marginBottom: 8 }} />
          <div style={{ fontWeight: 700, fontSize: 20, color: "#222" }}>xisen</div>
        </div>
        <div style={{ flex: "1 1 120px", marginBottom: 24 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>About Us</div>
          <div><a href="#">Company</a></div>
          <div><a href="#">Team</a></div>
          <div><a href="#">Careers</a></div>
        </div>
        <div style={{ flex: "1 1 120px", marginBottom: 24 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Quick Links</div>
          <div><a href="#">Home</a></div>
          <div><a href="#">Shop</a></div>
          <div><a href="#">Contact</a></div>
        </div>
        <div style={{ flex: "1 1 120px", marginBottom: 24 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>My Account</div>
          <div><a href="#">Login</a></div>
          <div><a href="#">Register</a></div>
          <div><a href="#">Orders</a></div>
        </div>
        <div style={{ flex: "1 1 120px", marginBottom: 24 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Resources</div>
          <div><a href="#">Blog</a></div>
          <div><a href="#">Help Center</a></div>
          <div><a href="#">Privacy Policy</a></div>
        </div>
      </div>
    </footer>
  );
}
