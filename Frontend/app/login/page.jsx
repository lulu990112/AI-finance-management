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
        <div style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "0 20px",
          position: "relative"
        }}>
          <div style={{
            textAlign: "center",
            marginBottom: "20px"
          }}>
            <h1 style={{ fontSize: 36, fontWeight: 700, margin: 0 }}>Login</h1>
            <div style={{ color: "#888", marginTop: 8 }}>LULU, your personal AI financial assistant</div>
          </div>
          <div style={{ 
            position: "absolute", 
            top: "20px", 
            right: "20px", 
            color: "#ff4d4f" 
          }}>
            Home - <span style={{ color: "#ff4d4f" }}>Login</span>
          </div>
        </div>
      </section>
      {/* Login form */}
      <main style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "70vh",
        background: "transparent",
        padding: "0 20px"
      }}>
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          width: "100%",
          maxWidth: "500px"
        }}>
          <LoginForm />
        </div>
      </main>
    </div>
  );
}
