import React, { useEffect, useState } from "react";
import { getBookmarks, toggleBookmark } from "../services/api";
import ScholarshipCard from "../components/ScholarshipCard";

export default function Bookmarks() {
  const [items, setItems] = useState([]);

  useEffect(() => { load(); }, []);

  const load = async () => {
    const res = await getBookmarks();
    setItems(res.data || []);
  };

  const handleBookmark = async (id) => {
    await toggleBookmark(id);
    load();
  };

  return (
    <div>
      <h3>🔖 My Bookmarks</h3>
      {items.length === 0 ? (
        <p className="text-muted">No bookmarks yet.</p>
      ) : (
        items.map((s) => <ScholarshipCard key={s.scholarship_id} scholarship={s} onBookmark={handleBookmark} />)
      )}
    </div>
  );
}