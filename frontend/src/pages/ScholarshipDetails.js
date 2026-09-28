import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getScholarship, checkEligibility, toggleBookmark } from "../services/api";

export default function ScholarshipDetails() {
  const { id } = useParams();
  const [s, setS] = useState(null);
  const [elig, setElig] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => { load(); }, [id]);

  const load = async () => {
    try {
      const res = await getScholarship(id);
      setS(res.data);
    } catch (e) { setError("Scholarship not found"); }
  };

  const handleEligibility = async () => {
    try { const res = await checkEligibility(id); setElig(res.data); }
    catch (err) { alert(err.response?.data?.error || "Complete profile first"); }
  };

  const handleBookmark = async () => {
    try { const res = await toggleBookmark(id); alert(res.data.message); }
    catch (e) { alert("Login required"); }
  };

  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!s) return <div className="text-center py-5">Loading...</div>;

  return (
    <div className="animate-in">
      {/* HERO */}
      <div className="sn-card mb-4" style={{
        background: "linear-gradient(135deg, #4f46e5 0%, #0ea5e9 100%)",
        color: "white", border: "none"
      }}>
        <div className="row align-items-center">
          <div className="col-md-8">
            <span className="home-badge" style={{ marginBottom: "12px" }}>{s.provider}</span>
            <h2 style={{ fontWeight: 800, marginBottom: "8px" }}>{s.scholarship_name}</h2>
            <p style={{ opacity: 0.9, marginBottom: 0 }}>{s.eligibility_description}</p>
          </div>
          <div className="col-md-4 text-md-end mt-3 mt-md-0">
            <div style={{ fontSize: "0.85rem", opacity: 0.9 }}>Scholarship Amount</div>
            <div style={{ fontSize: "2rem", fontWeight: 800 }}>₹{s.scholarship_amount?.toLocaleString()}</div>
          </div>
        </div>
      </div>

      {/* QUICK INFO */}
      <div className="row g-3 mb-4">
        {[
          { icon: "📅", label: "Deadline", value: s.application_deadline, danger: true },
          { icon: "📚", label: "Course", value: s.course },
          { icon: "🎯", label: "Min %", value: `${s.minimum_percentage}%` },
          { icon: "💵", label: "Max Income", value: `₹${s.max_family_income?.toLocaleString()}` },
          { icon: "📍", label: "State", value: s.state },
          { icon: "👥", label: "Category", value: s.category },
          { icon: "⚧", label: "Gender", value: s.gender }
        ].map((item, i) => (
          <div className="col-md-6 col-lg-3" key={i}>
            <div className="sn-card-flat">
              <div style={{ fontSize: "1.2rem", marginBottom: "6px" }}>{item.icon}</div>
              <div style={{ fontSize: "0.75rem", color: "var(--gray)", textTransform: "uppercase", fontWeight: 600 }}>
                {item.label}
              </div>
              <div style={{ fontWeight: 700, fontSize: "0.95rem" }}>{item.value || "All"}</div>
            </div>
          </div>
        ))}
      </div>

      {/* ACTION BUTTONS */}
      <div className="sn-card mb-4">
        <h5 style={{ fontWeight: 700, marginBottom: "16px" }}>⚡ Actions</h5>
        <div className="d-flex gap-2 flex-wrap">
          <button className="btn-sn" onClick={handleEligibility}>
            ✅ Check My Eligibility
          </button>
          <button className="btn-sn-outline" onClick={handleBookmark}>
            🔖 Bookmark
          </button>
          <a className="btn-sn-ghost" href={s.application_url} target="_blank" rel="noreferrer"
             style={{ padding: "12px 22px", textDecoration: "none" }}>
            🌐 Apply on Official Site →
          </a>
        </div>
      </div>

      {/* EXPLAINABLE ELIGIBILITY RESULT */}
      {elig && (
        <div className="sn-card mb-4">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 style={{ fontWeight: 700, margin: 0 }}>🎯 Eligibility Result</h5>
            <span className={`status-badge status-${elig.status.replace("_", "")}`}>
              {elig.status.replace("_", " ")}
            </span>
          </div>

          <p style={{ color: "var(--gray)", marginBottom: "20px" }}>{elig.reason}</p>

          <div className="row g-3">
            <div className="col-md-6">
              <h6 style={{ fontWeight: 700, color: "var(--success)", marginBottom: "12px" }}>
                ✓ You Match ({elig.matched.length})
              </h6>
              {elig.matched.map((m, i) => (
                <div key={i} className="criteria-item criteria-matched">
                  <span className="criteria-icon">✓</span>
                  <span>{m}</span>
                </div>
              ))}
            </div>

            {elig.failed.length > 0 && (
              <div className="col-md-6">
                <h6 style={{ fontWeight: 700, color: "var(--danger)", marginBottom: "12px" }}>
                  ✗ Not Matched ({elig.failed.length})
                </h6>
                {elig.failed.map((f, i) => (
                  <div key={i} className="criteria-item criteria-failed">
                    <span className="criteria-icon">✗</span>
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* DOCUMENTS */}
      <div className="sn-card mb-4">
        <h5 style={{ fontWeight: 700, marginBottom: "16px" }}>📄 Required Documents</h5>
        <div className="row g-2">
          {(s.required_documents || []).map((d, i) => (
            <div className="col-md-6" key={i}>
              <div style={{
                padding: "12px 16px",
                background: "var(--light)",
                borderRadius: "10px",
                display: "flex",
                alignItems: "center",
                gap: "10px"
              }}>
                <span style={{ color: "var(--primary)", fontSize: "1.1rem" }}>📎</span>
                <span style={{ fontWeight: 500 }}>{d}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}