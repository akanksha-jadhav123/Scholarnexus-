import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogoFull } from "../components/Logo";

export default function Home() {
  const { user } = useAuth();

  const features = [
    {
      icon: "✅",
      title: "Eligibility Checker",
      desc: "Instantly check if you qualify based on percentage, income, course, category, gender, and state — with clear reasons."
    },
    {
      icon: "🤖",
      title: "AI Recommendation",
      desc: "Get personalized scholarship matches ranked by a weighted match score based on your profile."
    },
    {
      icon: "📊",
      title: "Match Score & Ranking",
      desc: "See exactly how well each scholarship matches your profile with a transparent 0–100% score."
    },
    {
      icon: "💡",
      title: "Explainable Results",
      desc: "Know exactly which criteria you meet and which you don't — no black-box recommendations."
    },
    {
      icon: "🔖",
      title: "Bookmark & Compare",
      desc: "Save scholarships for later and compare them side-by-side on amount, deadline, and eligibility."
    },
    {
      icon: "⏰",
      title: "Deadline Tracker",
      desc: "Track upcoming deadlines for your bookmarked scholarships with urgency-based color alerts."
    }
  ];

  return (
    <div>
      {/* HERO */}
      <section className="home-hero">
        <div className="container home-hero-content">
          <div className="row align-items-center">
            <div className="col-lg-7">
              <div style={{ marginBottom: "20px" }}>
  <LogoFull size={48} color="white" />
  <span className="home-badge" style={{ marginLeft: "12px", marginBottom: 0 }}>
    Smart Student Funding Assistant
  </span>
</div>
              <h1 className="home-title">
                Find the <span style={{ textDecoration: "underline", textDecorationColor: "#fbbf24" }}>right scholarship</span> for your profile
              </h1>
              <p className="home-subtitle">
                ScholarNexus analyzes your academic, financial, and demographic profile to recommend scholarships you're actually eligible for — with transparent match scores and clear explanations.
              </p>
              <div className="d-flex gap-3 flex-wrap">
                {user ? (
                  <Link to="/dashboard" className="btn-sn">
                    Go to Dashboard →
                  </Link>
                ) : (
                  <>
                    <Link to="/register" className="btn-sn">
                      Get Started Free →
                    </Link>
                    <Link to="/login" className="btn-sn-outline" style={{ background: "rgba(255,255,255,0.15)", color: "white", borderColor: "white" }}>
                      Login
                    </Link>
                  </>
                )}
              </div>

              <div className="home-stats">
                <div>
                  <span className="home-stat-value">12+</span>
                  <span className="home-stat-label">Verified Scholarships</span>
                </div>
                <div>
                  <span className="home-stat-value">6</span>
                  <span className="home-stat-label">Eligibility Criteria</span>
                </div>
                <div>
                  <span className="home-stat-value">100%</span>
                  <span className="home-stat-label">Explainable Matches</span>
                </div>
              </div>
            </div>
            <div className="col-lg-5 d-none d-lg-block">
              <div style={{
                background: "rgba(255,255,255,0.15)",
                borderRadius: "20px",
                padding: "30px",
                backdropFilter: "blur(20px)",
                border: "1px solid rgba(255,255,255,0.3)"
              }}>
                <div style={{ fontSize: "0.85rem", opacity: 0.9, marginBottom: "12px" }}>TOP MATCH FOR YOU</div>
                <h5 style={{ fontWeight: 700, marginBottom: "8px" }}>National Merit Scholarship</h5>
                <p style={{ fontSize: "0.9rem", opacity: 0.9, marginBottom: "16px" }}>Government of India</p>
                <div style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "16px" }}>
                  <span className="match-badge match-high" style={{ background: "white", color: "#065f46" }}>92% Match</span>
                  <span style={{ fontSize: "0.85rem", opacity: 0.9 }}>₹50,000</span>
                </div>
                <div style={{ fontSize: "0.85rem", lineHeight: 1.7, opacity: 0.95 }}>
                  ✓ Percentage satisfies requirement<br />
                  ✓ Income within limit<br />
                  ✓ Course matches<br />
                  ✓ State eligible
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="container mb-5">
        <div className="text-center mb-5">
          <h2 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "12px" }}>
            Everything you need to win scholarships
          </h2>
          <p style={{ color: "var(--gray)", maxWidth: "600px", margin: "0 auto" }}>
            From eligibility checking to application tracking — ScholarNexus covers the entire journey.
          </p>
        </div>
        <div className="row g-4">
          {features.map((f, i) => (
            <div className="col-md-6 col-lg-4" key={i}>
              <div className="feature-card animate-in" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="feature-icon">{f.icon}</div>
                <h5 className="feature-title">{f.title}</h5>
                <p className="feature-desc">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="container mb-5">
        <div className="text-center mb-5">
          <h2 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "12px" }}>
            How ScholarNexus works
          </h2>
        </div>
        <div className="row g-4">
          {[
            { step: "1", title: "Create your profile", desc: "Add academic, financial, and personal details." },
            { step: "2", title: "Check eligibility", desc: "See which scholarships you qualify for." },
            { step: "3", title: "Get AI matches", desc: "Receive ranked recommendations with match %." },
            { step: "4", title: "Apply & track", desc: "Bookmark, apply, and never miss a deadline." }
          ].map((s, i) => (
            <div className="col-md-6 col-lg-3" key={i}>
              <div className="sn-card text-center h-100">
                <div style={{
                  width: "48px", height: "48px", borderRadius: "50%",
                  background: "linear-gradient(135deg, var(--primary), var(--secondary))",
                  color: "white", display: "flex", alignItems: "center",
                  justifyContent: "center", fontWeight: 800, fontSize: "1.2rem",
                  margin: "0 auto 16px"
                }}>{s.step}</div>
                <h6 style={{ fontWeight: 700, marginBottom: "8px" }}>{s.title}</h6>
                <p style={{ color: "var(--gray)", fontSize: "0.9rem", margin: 0 }}>{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="container mb-5">
        <div style={{
          background: "linear-gradient(135deg, var(--primary), var(--secondary))",
          borderRadius: "24px",
          padding: "60px 40px",
          textAlign: "center",
          color: "white"
        }}>
          <h2 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "16px" }}>
            Ready to find your scholarship?
          </h2>
          <p style={{ fontSize: "1.1rem", opacity: 0.95, marginBottom: "30px", maxWidth: "600px", margin: "0 auto 30px" }}>
            Join ScholarNexus today and get personalized matches in seconds.
          </p>
          <Link to={user ? "/dashboard" : "/register"} className="btn-sn" style={{ background: "white", color: "var(--primary)" }}>
            {user ? "Go to Dashboard →" : "Start Free →"}
          </Link>
        </div>
      </section>
    </div>
  );
}