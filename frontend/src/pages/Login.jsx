import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    setError(null);
    if (!username || !password) {
      setError("Please enter username and password");
      return;
    }
    try {
      const res = await fetch(`/api/auth/token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
      if (!data.access) throw new Error("Token not received");
      localStorage.setItem("teacher_token", data.access);
      if (data.refresh) localStorage.setItem("teacher_refresh", data.refresh);
      window.dispatchEvent(
        new StorageEvent("storage", { key: "teacher_token" })
      );
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  function logout() {
    localStorage.removeItem("teacher_token");
    localStorage.removeItem("teacher_refresh");
    window.dispatchEvent(new StorageEvent("storage", { key: "teacher_token" }));
    // Force re-render to show login form
    window.location.reload();
  }

  const authed = !!localStorage.getItem("teacher_token");

  return (
    <div className="max-w-md mx-auto bg-white shadow rounded p-6">
      <h2 className="text-xl font-bold mb-4">Teacher Login</h2>
      {authed ? (
        <div className="space-y-3">
          <div className="p-3 bg-green-50 text-green-800 rounded">
            You are logged in.
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate("/attendance")}
              className="bg-blue-600 text-white px-4 py-2 rounded"
            >
              Go to Attendance
            </button>
            <button
              onClick={logout}
              className="bg-gray-600 text-white px-4 py-2 rounded"
            >
              Logout
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              autoComplete="username"
            />
            <p className="text-xs text-gray-500 mt-1">
              Use your teacher account username
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              autoComplete="current-password"
            />
            <p className="text-xs text-gray-500 mt-1">Your secure password</p>
          </div>
          {error && (
            <div className="p-3 bg-red-100 text-red-800 rounded">{error}</div>
          )}
          <div className="flex justify-between items-center">
            <button
              type="button"
              onClick={() => navigate("/teacher-register")}
              className="text-blue-600 hover:text-blue-800 underline text-sm"
            >
              New teacher? Register here
            </button>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
              Login
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
