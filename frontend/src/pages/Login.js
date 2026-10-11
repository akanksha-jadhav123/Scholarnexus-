import React, { useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { loginUser } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { LogoFull } from "../components/Logo";

export default function Login() {
  const location = useLocation();
  const startAsAdmin = location.state?.isAdmin === true;

  const [isAdmin, setIsAdmin] = useState(startAsAdmin);
  const [form, setForm] = useState(
    startAsAdmin
      ? { email: "admin@scholarnexus.com", password: "admin123" }
      : { email: "", password: "" }
  );
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  // ... rest of the Login component (toggle + form)

  const toggleAdminMode = () => {
    const next = !isAdmin;
    setIsAdmin(next);
    if (next) {
      // Pre-fill demo admin credentials
      setForm({
        email: "admin@scholarnexus.com",
        password: "admin123"
      });
    } else {
      setForm({ email: "", password: "" });
    }
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  setError("");
  setLoading(true);
  try {
    const res = await loginUser(form);
    login(res.data);

    // REDIRECT BASED ON ROLE
    if (res.data.role === "admin") {
      navigate("/admin");
    } else {
      navigate("/dashboard");
    }
  } catch (err) {
    setError(err.response?.data?.error || "Login failed");
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="auth-split">
      {/* LEFT PANEL */}
      <div className="auth-split-left">
        <div className="auth-split-left-content">
          <LogoFull size={52} color="white" />
          <h2 className="auth-split-title">
            Welcome back to ScholarNexus
          </h2>
          <p className="auth-split-subtitle">
            Sign in to continue discovering scholarships that match your profile.
          </p>

          <div className="auth-benefits">
            {[
              { icon: "🎯", title: "Personalized Matches", desc: "Ranked scholarships based on your profile" },
              { icon: "✅", title: "Instant Eligibility", desc: "Know if you qualify in one click" },
              { icon: "📊", title: "Track Progress", desc: "Bookmarks, deadlines, and applications" }
            ].map((b, i) => (
              <div key={i} className="auth-benefit-item">
                <div className="auth-benefit-icon">{b.icon}</div>
                <div>
                  <div className="auth-benefit-title">{b.title}</div>
                  <div className="auth-benefit-desc">{b.desc}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="auth-trust">
            <div className="auth-trust-item">
              <div className="auth-trust-value">93+</div>
              <div className="auth-trust-label">Scholarships</div>
            </div>
            <div className="auth-trust-item">
              <div className="auth-trust-value">6</div>
              <div className="auth-trust-label">Criteria Checked</div>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="auth-split-right">
        <div className="auth-form-wrapper">
          <div className="auth-mobile-logo">
            <LogoFull size={44} color="var(--dark)" />
          </div>

          {/* ADMIN TOGGLE */}
          <div
            style={{
              display: "flex",
              background: "var(--light)",
              borderRadius: "10px",
              padding: "4px",
              marginBottom: "24px"
            }}
          >
            <button
              type="button"
              onClick={() => isAdmin && toggleAdminMode()}
              style={{
                flex: 1,
                padding: "10px",
                border: "none",
                borderRadius: "8px",
                fontWeight: 600,
                fontSize: "0.9rem",
                cursor: "pointer",
                background: !isAdmin ? "white" : "transparent",
                color: !isAdmin ? "var(--primary)" : "var(--gray)",
                boxShadow: !isAdmin ? "0 2px 6px rgba(0,0,0,0.08)" : "none",
                transition: "all 0.2s"
              }}
            >
              👤 Student
            </button>
            <button
              type="button"
              onClick={() => !isAdmin && toggleAdminMode()}
              style={{
                flex: 1,
                padding: "10px",
                border: "none",
                borderRadius: "8px",
                fontWeight: 600,
                fontSize: "0.9rem",
                cursor: "pointer",
                background: isAdmin ? "white" : "transparent",
                color: isAdmin ? "#dc3545" : "var(--gray)",
                boxShadow: isAdmin ? "0 2px 6px rgba(0,0,0,0.08)" : "none",
                transition: "all 0.2s"
              }}
            >
              🛠️ Admin
            </button>
          </div>

          <h3 className="auth-form-title" style={{ color: isAdmin ? "#dc3545" : "var(--dark)" }}>
            {isAdmin ? "🛠️ Admin Login" : "Sign in"}
          </h3>
          <p className="auth-form-subtitle">
            {isAdmin
              ? "Administrative access to manage scholarships and users"
              : "Enter your credentials to continue"}
          </p>

          {error && <div className="alert alert-danger">{error}</div>}

          {isAdmin && (
            <div
              className="alert"
              style={{
                background: "#fef2f2",
                border: "1px solid #fecaca",
                color: "#991b1b",
                fontSize: "0.85rem"
              }}
            >
              <strong>⚠️ Demo Admin Access</strong>
              <br />
              Credentials are pre-filled for demonstration.
              In production, this would require secure authentication.
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">Email</label>
              <input
                type="email"
                className="form-control"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                placeholder={isAdmin ? "admin@scholarnexus.com" : "you@example.com"}
                autoComplete="email"
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
                placeholder="••••••••"
                autoComplete="current-password"
              />
            </div>

            <button
              className="btn-sn w-100 mt-2"
              disabled={loading}
              style={isAdmin ? {
                background: "linear-gradient(135deg, #dc3545, #b91c1c)"
              } : {}}
            >
              {loading
                ? "Signing in..."
                : isAdmin
                ? "Sign In as Admin →"
                : "Sign In →"}
            </button>
          </form>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <p className="text-center mb-0" style={{ fontSize: "0.9rem", color: "var(--gray)" }}>
            New to ScholarNexus?{" "}
            <Link to="/register" style={{ color: "var(--primary)", fontWeight: 700 }}>
              Create free account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}