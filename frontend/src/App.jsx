import React, { useEffect, useState } from "react";
import { Routes, Route, Link, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Registration from "./pages/Registration";
import Attendance from "./pages/Attendance";
import Reports from "./pages/Reports";
import Students from "./pages/Students";
import SubjectsManagement from "./pages/SubjectsManagement";
import TeacherAssignments from "./pages/TeacherAssignments";
import Login from "./pages/Login";
import TeacherRegistration from "./pages/TeacherRegistration";

function ProtectedRoute({ children }) {
  const [authed, setAuthed] = useState(
    () => !!localStorage.getItem("teacher_token")
  );
  useEffect(() => {
    const onStorage = () => setAuthed(!!localStorage.getItem("teacher_token"));
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);
  return authed ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const [authed, setAuthed] = useState(
    () => !!localStorage.getItem("teacher_token")
  );

  useEffect(() => {
    const onStorage = () => setAuthed(!!localStorage.getItem("teacher_token"));
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  function handleLogout() {
    localStorage.removeItem("teacher_token");
    localStorage.removeItem("teacher_refresh");
    setAuthed(false);
    window.dispatchEvent(new StorageEvent("storage", { key: "teacher_token" }));
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold">Face Recognition Attendance</h1>
          <nav className="space-x-4 flex items-center">
            <Link to="/" className="hover:underline">
              Dashboard
            </Link>
            <Link to="/register" className="hover:underline">
              Register
            </Link>
            <Link to="/students" className="hover:underline">
              Students
            </Link>
            <Link to="/subjects" className="hover:underline">
              Subjects
            </Link>
            <Link to="/assignments" className="hover:underline">
              Assignments
            </Link>
            <Link to="/attendance" className="hover:underline">
              Attendance
            </Link>
            <Link to="/reports" className="hover:underline">
              Reports
            </Link>
            {authed ? (
              <button
                onClick={handleLogout}
                className="bg-red-500 hover:bg-red-600 px-3 py-1 rounded text-sm"
              >
                Logout
              </button>
            ) : (
              <Link to="/login" className="hover:underline">
                Login
              </Link>
            )}
          </nav>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/register" element={<Registration />} />
          <Route
            path="/students"
            element={
              <ProtectedRoute>
                <Students />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subjects"
            element={
              <ProtectedRoute>
                <SubjectsManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assignments"
            element={
              <ProtectedRoute>
                <TeacherAssignments />
              </ProtectedRoute>
            }
          />
          <Route
            path="/attendance"
            element={
              <ProtectedRoute>
                <Attendance />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<Login />} />
          <Route path="/teacher-register" element={<TeacherRegistration />} />
        </Routes>
      </main>
    </div>
  );
}
