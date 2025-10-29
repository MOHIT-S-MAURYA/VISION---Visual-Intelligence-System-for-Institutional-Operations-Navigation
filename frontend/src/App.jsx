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

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

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

function AdminRoute({ children }) {
  const [authed, setAuthed] = useState(
    () => !!localStorage.getItem("teacher_token")
  );
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAdmin = async () => {
      const token = localStorage.getItem("teacher_token");
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setIsAdmin(data.is_staff || data.is_superuser);
        }
      } catch (error) {
        console.error("Error checking admin status:", error);
      }
      setLoading(false);
    };

    checkAdmin();
    const onStorage = () => setAuthed(!!localStorage.getItem("teacher_token"));
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  if (loading) {
    return <div className="p-6 text-center">Loading...</div>;
  }

  if (!authed) {
    return <Navigate to="/login" replace />;
  }

  if (!isAdmin) {
    return (
      <div className="p-6 text-center">
        <h2 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h2>
        <p className="text-gray-600">
          This page is only accessible to administrators.
        </p>
        <Link
          to="/"
          className="text-blue-600 hover:underline mt-4 inline-block"
        >
          Go to Dashboard
        </Link>
      </div>
    );
  }

  return children;
}

export default function App() {
  const [authed, setAuthed] = useState(
    () => !!localStorage.getItem("teacher_token")
  );
  const [isAdmin, setIsAdmin] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    const fetchUserInfo = async () => {
      const token = localStorage.getItem("teacher_token");
      if (!token) return;

      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setUserInfo(data);
          setIsAdmin(data.is_staff || data.is_superuser);
        }
      } catch (error) {
        console.error("Error fetching user info:", error);
      }
    };

    fetchUserInfo();
    const onStorage = () => {
      setAuthed(!!localStorage.getItem("teacher_token"));
      if (!localStorage.getItem("teacher_token")) {
        setUserInfo(null);
        setIsAdmin(false);
      } else {
        fetchUserInfo();
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  function handleLogout() {
    localStorage.removeItem("teacher_token");
    localStorage.removeItem("teacher_refresh");
    setAuthed(false);
    setUserInfo(null);
    setIsAdmin(false);
    window.dispatchEvent(new StorageEvent("storage", { key: "teacher_token" }));
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold">Face Recognition Attendance</h1>
          <nav className="space-x-4 flex items-center">
            {authed && (
              <>
                <Link to="/" className="hover:underline">
                  Dashboard
                </Link>
                <Link to="/register" className="hover:underline">
                  Register Student
                </Link>
                <Link to="/attendance" className="hover:underline">
                  Attendance
                </Link>
                <Link to="/students" className="hover:underline">
                  Students
                </Link>
                <Link to="/reports" className="hover:underline">
                  Reports
                </Link>
                {isAdmin && (
                  <>
                    <span className="text-yellow-300">|</span>
                    <Link
                      to="/subjects"
                      className="hover:underline text-yellow-300"
                    >
                      Subjects
                    </Link>
                    <Link
                      to="/assignments"
                      className="hover:underline text-yellow-300"
                    >
                      Assignments
                    </Link>
                  </>
                )}
              </>
            )}
            {authed ? (
              <div className="flex items-center gap-3">
                {userInfo && (
                  <span className="text-sm">
                    👤 {userInfo.full_name}{" "}
                    {isAdmin && (
                      <span className="text-yellow-300">(Admin)</span>
                    )}
                  </span>
                )}
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 px-3 py-1 rounded text-sm"
                >
                  Logout
                </button>
              </div>
            ) : (
              <>
                <Link to="/login" className="hover:underline">
                  Login
                </Link>
                <Link to="/teacher-register" className="hover:underline">
                  Register as Teacher
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Routes>
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/register"
            element={
              <ProtectedRoute>
                <Registration />
              </ProtectedRoute>
            }
          />
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
              <AdminRoute>
                <SubjectsManagement />
              </AdminRoute>
            }
          />
          <Route
            path="/assignments"
            element={
              <AdminRoute>
                <TeacherAssignments />
              </AdminRoute>
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
