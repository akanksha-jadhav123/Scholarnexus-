import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function StudentRoute({ children }) {
  const { user, token, loading } = useAuth();
  if (loading) return <div className="text-center py-5">Loading...</div>;
  if (!token) return <Navigate to="/login" replace />;
  // Admin should not see student pages
  if (user?.role === "admin") return <Navigate to="/admin" replace />;
  return children;
}