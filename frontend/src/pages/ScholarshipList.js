import React, { useEffect, useState } from "react";
import { searchScholarships, toggleBookmark } from "../services/api";
import ScholarshipCard from "../components/ScholarshipCard";

const STATES = ["All", "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "Uttar Pradesh"];
const CATEGORIES = ["All", "General", "OBC", "SC", "ST", "Minority"];
const GENDERS = ["All", "Male", "Female", "Other"];
const COURSES = ["All", "B.Tech", "B.Sc", "B.Com", "B.A"];

export default function ScholarshipList() {
  const [filters, setFilters] = useState({
    q: "", state: "All", category: "All", gender: "All", course: "All",
    max_income: "", min_percentage: "", sort_by: "application_deadline", order: "asc"
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetchResults(); }, []);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const params = {};
      Object.entries(filters).forEach(([k, v]) => { if (v && v !== "All") params[k] = v; });
      const res = await searchScholarships(params);
      setResults(res.data.results || []);
    } finally { setLoading(false); }
  };

  const handleFilter = (e) => setFilters({ ...filters, [e.target.name]: e.target.value });

  const handleBookmark = async (id) => {
    try { await toggleBookmark(id); alert("Bookmark updated!"); }
    catch (e) { alert("Login required"); }
  };

  return (
    <div>
      <h3>🔍 Scholarships</h3>
      <div className="card p-3 mb-3">
        <div className="row g-2">
          <div className="col-md-3"><input name="q" className="form-control" placeholder="Search name/provider" value={filters.q} onChange={handleFilter} /></div>
          <div className="col-md-2"><select name="state" className="form-select" value={filters.state} onChange={handleFilter}>{STATES.map((s) => <option key={s}>{s}</option>)}</select></div>
          <div className="col-md-2"><select name="category" className="form-select" value={filters.category} onChange={handleFilter}>{CATEGORIES.map((s) => <option key={s}>{s}</option>)}</select></div>
          <div className="col-md-2"><select name="gender" className="form-select" value={filters.gender} onChange={handleFilter}>{GENDERS.map((s) => <option key={s}>{s}</option>)}</select></div>
          <div className="col-md-3"><select name="course" className="form-select" value={filters.course} onChange={handleFilter}>{COURSES.map((s) => <option key={s}>{s}</option>)}</select></div>
          <div className="col-md-3"><input type="number" name="max_income" className="form-control" placeholder="Max income" value={filters.max_income} onChange={handleFilter} /></div>
          <div className="col-md-3"><input type="number" name="min_percentage" className="form-control" placeholder="Min %" value={filters.min_percentage} onChange={handleFilter} /></div>
          <div className="col-md-3">
            <select name="sort_by" className="form-select" value={filters.sort_by} onChange={handleFilter}>
              <option value="application_deadline">Sort: Deadline</option>
              <option value="scholarship_amount">Sort: Amount</option>
              <option value="minimum_percentage">Sort: Min %</option>
            </select>
          </div>
          <div className="col-md-3"><button className="btn btn-primary w-100" onClick={fetchResults}>Apply Filters</button></div>
        </div>
      </div>
      {loading ? <p>Loading...</p> : results.length === 0 ? (
        <p className="text-muted">No scholarships found.</p>
      ) : (
        results.map((s) => <ScholarshipCard key={s.scholarship_id} scholarship={s} onBookmark={handleBookmark} />)
      )}
    </div>
  );
}