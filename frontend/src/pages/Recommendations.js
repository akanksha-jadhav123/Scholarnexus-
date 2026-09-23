import React, { useEffect, useState } from "react";
import { getRecommendations, toggleBookmark } from "../services/api";
import ScholarshipCard from "../components/ScholarshipCard";
import { Link } from "react-router-dom";

export default function Recommendations() {
  const [recs, setRecs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => { load(); }, []);

  const load = async () => {
    try {
      const res = await getRecommendations();
      setRecs(res.data.recommendations || []);
    } catch (err) { setError(err.response?.data?.error || "Failed to load"); }
  };

  const handleBookmark = async (id) => {
    try { await toggleBookmark(id); alert("Bookmark updated!"); }
    catch (e) { alert("Login required"); }
  };

  if (error) return <div className="alert alert-warning">{error} — <Link to="/profile">Complete your profile</Link></div>;

  return (
    <div>
      <h3>🎯 Recommended For You</h3>
      <p className="text-muted">Ranked by match score based on your profile</p>
      {recs.length === 0 ? (
        <p className="text-muted">No recommendations yet. Complete your profile.</p>
      ) : (
        recs.map((s) => <ScholarshipCard key={s.scholarship_id} scholarship={s} onBookmark={handleBookmark} showMatch={true} />)
      )}
    </div>
  );
}