import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getRecommendations, getBookmarks, getUpcomingDeadlines,
  getProfileCompletion, getProfile
} from "../services/api";
import { useAuth } from "../context/AuthContext";
import { LogoIcon } from "../components/Logo";

export default function Dashboard() {
  const { user } = useAuth();
  const [recs, setRecs] = useState([]);
  const [bookmarks, setBookmarks] = useState([]);
  const [deadlines, setDeadlines] = useState([]);
  const [completion, setCompletion] = useState(0);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [r, b, d, c, p] = await Promise.all([
        getRecommendations().catch(() => ({ data: { recommendations: [] } })),
        getBookmarks().catch(() => ({ data: [] })),
        getUpcomingDeadlines().catch(() => ({ data: [] })),
        getProfileCompletion().catch(() => ({ data: { completion: 0 } })),
        getProfile().catch(() => ({ data: null }))
      ]);
      setRecs(r.data.recommendations || []);
      setBookmarks(b.data || []);
      setDeadlines(d.data || []);
      setCompletion(c.data.completion || 0);
      setProfile(p.data);
    } finally {
      setLoading(false);
    }
  };

  const topMatch = recs[0];
  const urgentDeadlines = deadlines.filter((d) => d.days_left <= 7);

  if (loading) {
    return <div className="text-center py-5">Loading dashboard...</div>;
  }

  return (
    <div className="animate-in">
      {/* WELCOME HEADER */}
      <div className="sn-card mb-4" style={{
        background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
        color: "white",
        border: "none"
      }}>
        <div className="row align-items-center">
          <div className="col-md-8">
            <h2 style={{ fontWeight: 800, marginBottom: "8px" }}>
              Welcome back, {user?.name} 👋
            </h2>
            <p style={{ opacity: 0.9, marginBottom: "20px" }}>
              Here's your personalized scholarship overview
            </p>
            {completion < 100 && (
              <div style={{ marginBottom: "16px" }}>
                <div className="d-flex justify-content-between mb-2" style={{ fontSize: "0.85rem" }}>
                  <span>Profile completion</span>
                  <strong>{completion}%</strong>
                </div>
                <div className="progress-sn" style={{ background: "rgba(255,255,255,0.25)" }}>
                  <div className="progress-sn-bar" style={{ width: `${completion}%`, background: "white" }}></div>
                </div>
              </div>
            )}
            <Link to="/recommendations" className="btn-sn" style={{ background: "white", color: "var(--primary)" }}>
              View All Recommendations →
            </Link>
          </div>
          <div className="col-md-4 d-none d-md-block text-center">
  <LogoIcon size={100} />
</div>
        </div>
      </div>

      {/* STAT CARDS */}
      <div className="row g-3 mb-4">
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon primary">🎯</div>
            <div>
              <div className="stat-value">{recs.length}</div>
              <div className="stat-label">Recommended</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon warning">🔖</div>
            <div>
              <div className="stat-value">{bookmarks.length}</div>
              <div className="stat-label">Bookmarked</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon danger">⏰</div>
            <div>
              <div className="stat-value">{deadlines.length}</div>
              <div className="stat-label">Upcoming Deadlines</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <div className="stat-icon success">📊</div>
            <div>
              <div className="stat-value">{completion}%</div>
              <div className="stat-label">Profile Complete</div>
            </div>
          </div>
        </div>
      </div>

      {/* ALERT: URGENT DEADLINES */}
      {urgentDeadlines.length > 0 && (
        <div className="sn-card mb-4" style={{ borderLeft: "4px solid var(--danger)", background: "#fef2f2" }}>
          <div className="d-flex align-items-center gap-3">
            <span style={{ fontSize: "1.5rem" }}>⚠️</span>
            <div>
              <strong style={{ color: "var(--danger)" }}>
                {urgentDeadlines.length} deadline{urgentDeadlines.length > 1 ? "s" : ""} within 7 days!
              </strong>
              <p style={{ margin: 0, fontSize: "0.9rem", color: "var(--gray)" }}>
                <Link to="/deadlines">View deadlines →</Link>
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="row g-4">
        {/* TOP MATCH */}
        <div className="col-lg-6">
          <div className="sn-card h-100">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 style={{ fontWeight: 700, margin: 0 }}>🏆 Your Top Match</h5>
              <Link to="/recommendations" className="btn-sn-ghost" style={{ fontSize: "0.85rem" }}>
                See all →
              </Link>
            </div>

            {!topMatch ? (
              <div className="text-center py-4">
                <div style={{ fontSize: "3rem", marginBottom: "12px" }}>🔍</div>
                <p style={{ color: "var(--gray)", marginBottom: "16px" }}>
                  Complete your profile to see matches
                </p>
                <Link to="/profile" className="btn-sn">Complete Profile</Link>
              </div>
            ) : (
              <div>
                <div className="d-flex justify-content-between align-items-start mb-3">
                  <div>
                    <h6 style={{ fontWeight: 700, marginBottom: "4px" }}>
                      {topMatch.scholarship_name}
                    </h6>
                    <p style={{ color: "var(--gray)", fontSize: "0.85rem", margin: 0 }}>
                      {topMatch.provider}
                    </p>
                  </div>
                  <span className={`match-badge ${
                    topMatch.match_percentage >= 70 ? "match-high" :
                    topMatch.match_percentage >= 40 ? "match-mid" : "match-low"
                  }`}>
                    {topMatch.match_percentage}%
                  </span>
                </div>

                <div className="row g-2 mb-3" style={{ fontSize: "0.85rem" }}>
                  <div className="col-6">💰 ₹{topMatch.scholarship_amount}</div>
                  <div className="col-6">📅 {topMatch.application_deadline}</div>
                </div>

                <div style={{ background: "var(--light)", borderRadius: "10px", padding: "14px" }}>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--gray)", marginBottom: "8px" }}>
                    WHY IT MATCHES
                  </div>
                  {(topMatch.breakdown || []).slice(0, 4).map((b, i) => (
                    <div key={i} style={{ fontSize: "0.85rem", marginBottom: "4px" }}>
                      <span style={{ color: "var(--success)", marginRight: "6px" }}>✓</span>
                      {b.field} (+{b.points}%)
                    </div>
                  ))}
                </div>

                <Link
                  to={`/scholarships/${topMatch.scholarship_id}`}
                  className="btn-sn w-100 mt-3"
                  style={{ textAlign: "center", display: "block" }}
                >
                  View Details
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* UPCOMING DEADLINES */}
        <div className="col-lg-6">
          <div className="sn-card h-100">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 style={{ fontWeight: 700, margin: 0 }}>⏰ Upcoming Deadlines</h5>
              <Link to="/deadlines" className="btn-sn-ghost" style={{ fontSize: "0.85rem" }}>
                See all →
              </Link>
            </div>

            {deadlines.length === 0 ? (
              <div className="text-center py-4">
                <div style={{ fontSize: "3rem", marginBottom: "12px" }}>📅</div>
                <p style={{ color: "var(--gray)" }}>
                  Bookmark scholarships to track deadlines
                </p>
              </div>
            ) : (
              <div>
                {deadlines.slice(0, 5).map((d) => (
                  <div key={d.scholarship_id} className="d-flex justify-content-between align-items-center py-2"
                    style={{ borderBottom: "1px solid var(--border)" }}>
                    <div>
                      <Link to={`/scholarships/${d.scholarship_id}`}
                        style={{ color: "var(--dark)", textDecoration: "none", fontWeight: 600, fontSize: "0.9rem" }}>
                        {d.scholarship_name}
                      </Link>
                      <div style={{ fontSize: "0.8rem", color: "var(--gray)" }}>
                        Due {d.application_deadline}
                      </div>
                    </div>
                    <span className={
                      d.days_left <= 7 ? "deadline-red" :
                      d.days_left <= 15 ? "deadline-orange" : "deadline-green"
                    } style={{ fontSize: "0.9rem" }}>
                      {d.days_left}d
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* QUICK ACTIONS */}
      <div className="row g-3 mt-4">
        <div className="col-md-3">
          <Link to="/scholarships" className="sn-card text-decoration-none d-block text-center h-100">
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>🔍</div>
            <strong style={{ color: "var(--dark)" }}>Browse</strong>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--gray)" }}>All scholarships</p>
          </Link>
        </div>
        <div className="col-md-3">
          <Link to="/compare" className="sn-card text-decoration-none d-block text-center h-100">
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>⚖️</div>
            <strong style={{ color: "var(--dark)" }}>Compare</strong>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--gray)" }}>Side by side</p>
          </Link>
        </div>
        <div className="col-md-3">
          <Link to="/bookmarks" className="sn-card text-decoration-none d-block text-center h-100">
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>🔖</div>
            <strong style={{ color: "var(--dark)" }}>Bookmarks</strong>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--gray)" }}>Saved items</p>
          </Link>
        </div>
        <div className="col-md-3">
          <Link to="/profile" className="sn-card text-decoration-none d-block text-center h-100">
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>👤</div>
            <strong style={{ color: "var(--dark)" }}>Profile</strong>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--gray)" }}>Update details</p>
          </Link>
        </div>
      </div>
    </div>
  );
}