import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();

  if (loading) return <div className="text-center mt-5">Loading ScholarNexus...</div>;
  if (!token) return <Navigate to="/login" replace />;
  return children;
}