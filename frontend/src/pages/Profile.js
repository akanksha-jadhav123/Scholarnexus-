import React, { useEffect, useState } from "react";
import { getProfile, saveProfile, getProfileCompletion } from "../services/api";

const STATES = ["All", "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "Uttar Pradesh", "Delhi", "Other"];
const CATEGORIES = ["General", "OBC", "SC", "ST", "Minority"];
const GENDERS = ["Male", "Female", "Other"];
const COURSES = ["B.Tech", "B.Sc", "B.Com", "B.A", "M.Tech", "MBA", "Other"];

export default function Profile() {
  const [form, setForm] = useState({
    state: "", category: "", gender: "", income: "", course: "",
    branch: "", year: "", percentage: "", college: ""
  });
  const [completion, setCompletion] = useState(0);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => { loadProfile(); }, []);

  const loadProfile = async () => {
    try {
      const res = await getProfile();
      if (res.data && res.data.user_id) setForm(res.data);
      const c = await getProfileCompletion();
      setCompletion(c.data.completion);
    } catch (e) {}
  };

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(""); setError("");
    try {
      await saveProfile(form);
      const c = await getProfileCompletion();
      setCompletion(c.data.completion);
      setMessage("✅ Profile saved successfully!");
    } catch (err) {
      setError(err.response?.data?.error || "Save failed");
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-9">
        <div className="card p-4">
          <h3>👤 My Profile</h3>
          <div className="progress mb-3" style={{ height: "10px" }}>
            <div className="progress-bar bg-success" style={{ width: `${completion}%` }}></div>
          </div>
          <p className="text-muted small">Profile completion: {completion}%</p>
          {message && <div className="alert alert-success">{message}</div>}
          {error && <div className="alert alert-danger">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">State *</label>
                <select name="state" className="form-select" value={form.state} onChange={handleChange} required>
                  <option value="">Select</option>
                  {STATES.map((s) => <option key={s}>{s}</option>)}
                </select>
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Category *</label>
                <select name="category" className="form-select" value={form.category} onChange={handleChange} required>
                  <option value="">Select</option>
                  {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Gender *</label>
                <select name="gender" className="form-select" value={form.gender} onChange={handleChange} required>
                  <option value="">Select</option>
                  {GENDERS.map((g) => <option key={g}>{g}</option>)}
                </select>
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Annual Family Income (₹) *</label>
                <input type="number" name="income" className="form-control" value={form.income} onChange={handleChange} required min="0" />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Course *</label>
                <select name="course" className="form-select" value={form.course} onChange={handleChange} required>
                  <option value="">Select</option>
                  {COURSES.map((c) => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Branch</label>
                <input name="branch" className="form-control" value={form.branch} onChange={handleChange} />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Year</label>
                <input name="year" className="form-control" value={form.year} onChange={handleChange} />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">Percentage / CGPA *</label>
                <input type="number" step="0.01" name="percentage" className="form-control" value={form.percentage} onChange={handleChange} required min="0" max="100" />
              </div>
              <div className="col-md-12 mb-3">
                <label className="form-label">College Name</label>
                <input name="college" className="form-control" value={form.college} onChange={handleChange} />
              </div>
            </div>
            <button className="btn btn-primary">Save Profile</button>
          </form>
        </div>
      </div>
    </div>
  );
}