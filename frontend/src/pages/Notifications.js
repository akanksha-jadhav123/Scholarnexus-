import React, { useEffect, useState } from "react";
import { listNotifications, markAllNotificationsRead } from "../services/api";

export default function Notifications() {
  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);

  useEffect(() => { load(); }, []);

  const load = async () => {
    const res = await listNotifications();
    setItems(res.data.notifications || []);
    setUnread(res.data.unread || 0);
  };

  const markAll = async () => {
    await markAllNotificationsRead();
    load();
  };

  return (
    <div className="animate-in">
      <div className="d-flex justify-content-between mb-4">
        <div>
          <h2 style={{ fontWeight: 800, margin: 0 }}>🔔 Notifications</h2>
          <p style={{ color: "var(--gray)", margin: 0 }}>{unread} unread</p>
        </div>
        {unread > 0 && <button className="btn-sn-outline" onClick={markAll}>Mark all read</button>}
      </div>

      {items.length === 0 ? (
        <div className="sn-card text-center py-5">
          <div style={{ fontSize: "3rem" }}>🔕</div>
          <p style={{ color: "var(--gray)" }}>No notifications yet</p>
        </div>
      ) : (
        items.map((n, i) => (
          <div className="sn-card mb-2" key={i}
            style={{ borderLeft: n.read_status ? "4px solid var(--border)" : "4px solid var(--primary)" }}>
            <div style={{ fontWeight: 600 }}>{n.message}</div>
            <div style={{ fontSize: "0.8rem", color: "var(--gray)" }}>
              {n.type} • {new Date(n.created_at).toLocaleString()}
            </div>
          </div>
        ))
      )}
    </div>
  );
}