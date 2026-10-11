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
import AdminRoute from "./components/AdminRoute";
import AdminDashboard from "./pages/AdminDashboard";
import AdminScholarships from "./pages/AdminScholarships";
import AdminSources from "./pages/AdminSources";
import AdminUsers from "./pages/AdminUsers";
import Applications from "./pages/Applications";
import Documents from "./pages/Documents";
import Notifications from "./pages/Notifications";
import StudentRoute from "./components/StudentRoute";

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
        <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
<Route path="/admin/scholarships" element={<AdminRoute><AdminScholarships /></AdminRoute>} />
<Route path="/admin/sources" element={<AdminRoute><AdminSources /></AdminRoute>} />
<Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
<Route path="/applications" element={<ProtectedRoute><Applications /></ProtectedRoute>} />
<Route path="/documents/:id" element={<ProtectedRoute><Documents /></ProtectedRoute>} />
<Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
<Route path="/dashboard" element={<StudentRoute><Dashboard /></StudentRoute>} />
<Route path="/recommendations" element={<StudentRoute><Recommendations /></StudentRoute>} />
<Route path="/bookmarks" element={<StudentRoute><Bookmarks /></StudentRoute>} />
<Route path="/deadlines" element={<StudentRoute><Deadlines /></StudentRoute>} />
<Route path="/compare" element={<StudentRoute><Compare /></StudentRoute>} />
<Route path="/applications" element={<StudentRoute><Applications /></StudentRoute>} />
<Route path="/documents/:id" element={<StudentRoute><Documents /></StudentRoute>} />
<Route path="/notifications" element={<StudentRoute><Notifications /></StudentRoute>} />
<Route path="/profile" element={<StudentRoute><Profile /></StudentRoute>} />

// Public routes (both can access)
<Route path="/scholarships" element={<ScholarshipList />} />
<Route path="/scholarships/:id" element={<ScholarshipDetails />} />
      </Routes>
      <div className="sn-footer">
        © 2026 <strong>ScholarNexus</strong> — Smart Student Funding Assistant
      </div>
    </BrowserRouter>
  );
}