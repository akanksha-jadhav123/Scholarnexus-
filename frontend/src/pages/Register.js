import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { registerUser, loginUser } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { LogoFull } from "../components/Logo";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await registerUser(form);
      const res = await loginUser({ email: form.email, password: form.password });
      login(res.data);
      navigate("/profile");
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const passwordStrength = () => {
    const p = form.password;
    if (!p) return { label: "", color: "transparent", width: "0%" };
    if (p.length < 6) return { label: "Weak", color: "#ef4444", width: "33%" };
    if (p.length < 10 || !/\d/.test(p)) return { label: "Medium", color: "#f59e0b", width: "66%" };
    return { label: "Strong", color: "#10b981", width: "100%" };
  };

  const strength = passwordStrength();

  const benefits = [
    { icon: "🎯", title: "Eligibility Checker", desc: "Know instantly which scholarships you qualify for" },
    { icon: "🤖", title: "AI Recommendations", desc: "Get ranked matches with transparent scores" },
    { icon: "💡", title: "Explainable Results", desc: "See exactly why each scholarship matches" },
    { icon: "⏰", title: "Deadline Tracker", desc: "Never miss an application deadline" }
  ];

  return (
    <div className="auth-split">
      {/* LEFT PANEL — Brand + Benefits */}
      <div className="auth-split-left">
        <div className="auth-split-left-content">
          <LogoFull size={52} color="white" />

          <h2 className="auth-split-title">
            Find the right scholarship for your profile
          </h2>

          <p className="auth-split-subtitle">
            Join thousands of students discovering scholarships they're actually eligible for.
          </p>

          <div className="auth-benefits">
            {benefits.map((b, i) => (
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
              <div className="auth-trust-value">12+</div>
              <div className="auth-trust-label">Verified Scholarships</div>
            </div>
            <div className="auth-trust-item">
              <div className="auth-trust-value">100%</div>
              <div className="auth-trust-label">Free Forever</div>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL — Form */}
      <div className="auth-split-right">
        <div className="auth-form-wrapper">
          {/* Logo shown again on mobile (hidden on desktop) */}
          <div className="auth-mobile-logo">
            <LogoFull size={44} color="var(--dark)" />
          </div>

          <h3 className="auth-form-title">Create your account</h3>
          <p className="auth-form-subtitle">It takes less than 30 seconds</p>

          {error && <div className="alert alert-danger">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">Full Name</label>
              <input
                className="form-control"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                placeholder="Your full name"
                autoComplete="name"
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Email</label>
              <input
                type="email"
                className="form-control"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                placeholder="you@example.com"
                autoComplete="email"
              />
            </div>

            <div className="mb-2">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
                minLength={6}
                placeholder="Minimum 6 characters"
                autoComplete="new-password"
              />
              {form.password && (
                <div style={{ marginTop: "8px" }}>
                  <div style={{
                    height: "4px",
                    background: "#e2e8f0",
                    borderRadius: "999px",
                    overflow: "hidden"
                  }}>
                    <div style={{
                      height: "100%",
                      width: strength.width,
                      background: strength.color,
                      transition: "all 0.3s"
                    }} />
                  </div>
                  <div style={{ fontSize: "0.75rem", color: strength.color, marginTop: "4px", fontWeight: 600 }}>
                    {strength.label} password
                  </div>
                </div>
              )}
            </div>

            <button className="btn-sn w-100 mt-3" disabled={loading}>
              {loading ? "Creating account..." : "Create Account →"}
            </button>

            <p style={{
              fontSize: "0.75rem",
              color: "var(--gray)",
              textAlign: "center",
              marginTop: "14px",
              marginBottom: 0,
              lineHeight: 1.5
            }}>
              By signing up, you agree to our <strong>Terms</strong> and <strong>Privacy Policy</strong>.
              ScholarNexus is free for all students.
            </p>
          </form>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <p className="text-center mb-0" style={{ fontSize: "0.9rem", color: "var(--gray)" }}>
            Already have an account?{" "}
            <Link to="/login" style={{ color: "var(--primary)", fontWeight: 700 }}>
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}