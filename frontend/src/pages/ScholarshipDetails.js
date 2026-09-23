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
    catch (err) { alert(err.response?.data?.error || "Check failed"); }
  };

  const handleBookmark = async () => {
    try { const res = await toggleBookmark(id); alert(res.data.message); }
    catch (e) { alert("Login required"); }
  };

  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!s) return <p>Loading...</p>;

  return (
    <div className="card p-4">
      <h3>{s.scholarship_name}</h3>
      <p className="text-muted">{s.provider}</p>
      <div className="row mt-3">
        <div className="col-md-6"><strong>💰 Amount:</strong> ₹{s.scholarship_amount}</div>
        <div className="col-md-6"><strong>📅 Deadline:</strong> {s.application_deadline}</div>
        <div className="col-md-6"><strong>📚 Course:</strong> {s.course}</div>
        <div className="col-md-6"><strong>📍 State:</strong> {s.state}</div>
        <div className="col-md-6"><strong>👥 Category:</strong> {s.category}</div>
        <div className="col-md-6"><strong>⚧ Gender:</strong> {s.gender}</div>
        <div className="col-md-6"><strong>🎯 Min %:</strong> {s.minimum_percentage}%</div>
        <div className="col-md-6"><strong>💵 Max Income:</strong> ₹{s.max_family_income}</div>
      </div>
      <hr />
      <h5>📄 Required Documents</h5>
      <ul>{(s.required_documents || []).map((d, i) => <li key={i}>{d}</li>)}</ul>
      <h5>📝 Eligibility</h5>
      <p>{s.eligibility_description}</p>
      <div className="d-flex gap-2 mt-3">
        <button className="btn btn-primary" onClick={handleEligibility}>Check My Eligibility</button>
        <button className="btn btn-outline-warning" onClick={handleBookmark}>🔖 Bookmark</button>
        <a className="btn btn-success" href={s.application_url} target="_blank" rel="noreferrer">🌐 Apply on Official Site</a>
      </div>
      {elig && (
        <div className="mt-4">
          <h5>Result: <span className={`badge ${elig.status === "eligible" ? "bg-success" : elig.status === "partial" ? "bg-warning" : "bg-danger"}`}>{elig.status}</span></h5>
          <p>{elig.reason}</p>
          <h6>✅ Matched</h6>
          {elig.matched.map((m, i) => <div key={i} className="criteria-item criteria-matched">{m}</div>)}
          {elig.failed.length > 0 && (
            <>
              <h6 className="mt-3">❌ Failed</h6>
              {elig.failed.map((f, i) => <div key={i} className="criteria-item criteria-failed">{f}</div>)}
            </>
          )}
        </div>
      )}
    </div>
  );
}