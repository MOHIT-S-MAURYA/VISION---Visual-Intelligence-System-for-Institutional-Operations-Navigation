import React, { useEffect, useMemo, useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function Reports() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    department: "",
    classYear: "",
    startDate: "",
    endDate: "",
  });

  async function loadSessions() {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("teacher_token");
      const refresh = localStorage.getItem("teacher_refresh");
      let res = await fetch(`${API_URL}/api/attendance/sessions/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      // On 401, try to refresh token once
      if (res.status === 401 && refresh) {
        const r = await fetch(`${API_URL}/api/auth/token/refresh/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh }),
        });
        if (r.ok) {
          const t = await r.json();
          if (t.access) {
            localStorage.setItem("teacher_token", t.access);
            res = await fetch(`${API_URL}/api/attendance/sessions/`, {
              headers: { Authorization: `Bearer ${t.access}` },
            });
          }
        } else {
          // refresh failed; force logout
          localStorage.removeItem("teacher_token");
          localStorage.removeItem("teacher_refresh");
        }
      }
      const data = await res.json();
      if (!res.ok) {
        // Show specific message for authentication errors
        if (res.status === 401) {
          throw new Error(
            "Authentication required. Please log in to view reports. You need to login as a teacher or admin to access this page."
          );
        }
        throw new Error(data.error || data.detail || "Failed to load sessions");
      }
      // sort by start_time desc if present
      data.sort((a, b) =>
        (b.start_time || "").localeCompare(a.start_time || "")
      );
      setSessions(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function endSession(sessionId) {
    if (!window.confirm("End this session?")) return;
    try {
      const token = localStorage.getItem("teacher_token");
      const res = await fetch(
        `${API_URL}/api/attendance/sessions/${sessionId}/end_session/`,
        {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      if (res.ok) {
        alert("Session ended successfully!");
        loadSessions();
      } else {
        alert("Failed to end session");
      }
    } catch (err) {
      alert("Error ending session");
    }
  }

  async function deleteSession(sessionId) {
    if (!window.confirm("Delete this session? This action cannot be undone."))
      return;
    try {
      const token = localStorage.getItem("teacher_token");
      const res = await fetch(
        `${API_URL}/api/attendance/sessions/${sessionId}/`,
        {
          method: "DELETE",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      if (res.ok) {
        alert("Session deleted successfully!");
        loadSessions();
      } else {
        alert("Failed to delete session");
      }
    } catch (err) {
      alert("Error deleting session");
    }
  }

  useEffect(() => {
    loadSessions();
  }, []);

  const filtered = useMemo(() => {
    return sessions.filter((s) => {
      if (filters.department && s.department !== filters.department)
        return false;
      if (filters.classYear && s.class_year !== filters.classYear) return false;
      // Date range filter (inclusive). Compare against session start_time date.
      if (filters.startDate || filters.endDate) {
        if (!s.start_time) return false;
        const d = new Date(s.start_time);
        if (filters.startDate) {
          const sd = new Date(filters.startDate + "T00:00:00");
          if (d < sd) return false;
        }
        if (filters.endDate) {
          const ed = new Date(filters.endDate + "T23:59:59");
          if (d > ed) return false;
        }
      }
      return true;
    });
  }, [sessions, filters]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Attendance Reports</h2>
        <button
          onClick={loadSessions}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Refresh
        </button>
      </div>

      <div className="bg-white shadow rounded p-4 grid grid-cols-1 md:grid-cols-5 gap-3">
        <Input
          label="Department"
          value={filters.department}
          onChange={(v) => setFilters((f) => ({ ...f, department: v }))}
          placeholder="e.g., CSE"
          hint="Filter by department"
        />
        <Input
          label="Class / Year"
          value={filters.classYear}
          onChange={(v) => setFilters((f) => ({ ...f, classYear: v }))}
          placeholder="e.g., First Year"
          hint="Filter by year"
        />
        <Input
          label="Start Date"
          type="date"
          value={filters.startDate}
          onChange={(v) => setFilters((f) => ({ ...f, startDate: v }))}
          hint="Sessions from this date"
        />
        <Input
          label="End Date"
          type="date"
          value={filters.endDate}
          onChange={(v) => setFilters((f) => ({ ...f, endDate: v }))}
          hint="Sessions until this date"
        />
        <div className="flex items-end">
          <button
            className="border px-4 py-2 rounded w-full hover:bg-gray-50"
            onClick={() =>
              setFilters({
                department: "",
                classYear: "",
                startDate: "",
                endDate: "",
              })
            }
            title="Clear all filters"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {loading && <div>Loading...</div>}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-800 p-4 rounded">
          <div className="flex items-start gap-2">
            <span className="text-xl">🔒</span>
            <div className="flex-1">
              <p className="font-semibold mb-1">Access Denied</p>
              <p className="mb-2">{error}</p>
              <a
                href="/login"
                className="inline-block bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
              >
                Go to Login Page
              </a>
            </div>
          </div>
        </div>
      )}

      {!loading && !error && (
        <div className="bg-white shadow rounded overflow-auto">
          <table className="min-w-full">
            <thead>
              <tr className="text-left bg-gray-50">
                <Th>Session</Th>
                <Th>Department</Th>
                <Th>Class</Th>
                <Th>Subject</Th>
                <Th>Status</Th>
                <Th>Start</Th>
                <Th>End</Th>
                <Th>Marked</Th>
                <Th>Export</Th>
                <Th>Actions</Th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr key={s.id} className="border-t">
                  <Td>#{s.id}</Td>
                  <Td>{s.department}</Td>
                  <Td>{s.class_year}</Td>
                  <Td>{s.subject}</Td>
                  <Td>
                    {s.is_active ? (
                      <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                        Active
                      </span>
                    ) : (
                      <span className="text-xs px-2 py-1 bg-gray-100 text-gray-800 rounded">
                        Ended
                      </span>
                    )}
                  </Td>
                  <Td>{fmt(s.start_time)}</Td>
                  <Td>{fmt(s.end_time)}</Td>
                  <Td>{Array.isArray(s.records) ? s.records.length : 0}</Td>
                  <Td>
                    <a
                      className="text-blue-600 underline text-sm"
                      href={`${API_URL}/api/attendance/sessions/${s.id}/export_csv/`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      CSV
                    </a>
                  </Td>
                  <Td>
                    <div className="flex gap-2">
                      {s.is_active && (
                        <button
                          onClick={() => endSession(s.id)}
                          className="text-xs bg-orange-500 hover:bg-orange-600 text-white px-2 py-1 rounded"
                          title="End Session"
                        >
                          End
                        </button>
                      )}
                      <button
                        onClick={() => deleteSession(s.id)}
                        className="text-xs bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded"
                        title="Delete Session"
                      >
                        Delete
                      </button>
                    </div>
                  </Td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <Td colSpan={10}>
                    <div className="text-center text-gray-500 py-6">
                      No sessions found.
                    </div>
                  </Td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Input({ label, value, onChange, type = "text", placeholder, hint }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
      {hint && <p className="text-xs text-gray-500 mt-1">{hint}</p>}
    </div>
  );
}

function Th({ children }) {
  return <th className="px-3 py-2 text-sm font-semibold">{children}</th>;
}

function Td({ children, colSpan }) {
  return (
    <td className="px-3 py-2 text-sm text-gray-800" colSpan={colSpan}>
      {children}
    </td>
  );
}

function fmt(iso) {
  if (!iso) return "-";
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}
