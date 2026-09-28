import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import Dashboard from "./pages/Dashboard";
import ScholarshipList from "./pages/ScholarshipList";
import ScholarshipDetails from "./pages/ScholarshipDetails";
import Recommendations from "./pages/Recommendations";
import Compare from "./pages/Compare";
import Bookmarks from "./pages/Bookmarks";
import Deadlines from "./pages/Deadlines";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/scholarships" element={<ScholarshipList />} />
        <Route path="/scholarships/:id" element={<ScholarshipDetails />} />
        <Route path="/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
        <Route path="/compare" element={<ProtectedRoute><Compare /></ProtectedRoute>} />
        <Route path="/bookmarks" element={<ProtectedRoute><Bookmarks /></ProtectedRoute>} />
        <Route path="/deadlines" element={<ProtectedRoute><Deadlines /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <div className="sn-footer">
        © 2026 <strong>ScholarNexus</strong> — Smart Student Funding Assistant
      </div>
    </BrowserRouter>
  );
}