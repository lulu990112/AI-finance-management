import Navbar from "../components/Navbar";
import LoginForm from "../components/login-form";

export default function LoginPage() {
  return (
    <div>
      <Navbar />
      {/* Login title */}
      <section style={{
        background: "#f4faff",
        padding: "48px 0 32px 0",
        borderBottom: "1px solid #f0f0f0"
      }}>
        <div className="container">
          <h1 style={{ fontSize: 36, fontWeight: 700, margin: 0 }}>Login</h1>
          <div style={{ color: "#888", marginTop: 8 }}>LULU, your personal AI financial assistant</div>
          <div style={{ float: "right", color: "#ff4d4f", marginTop: -32 }}>
            Home - <span style={{ color: "#ff4d4f" }}>Login</span>
          </div>
        </div>
      </section>
      {/* Login form */}
      <main style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "60vh",
        background: "transparent"
      }}>
        <LoginForm />
      </main>
    </div>
  );
}
