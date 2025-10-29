import React, { useEffect, useMemo, useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function Students() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    department: "",
    classYear: "",
    search: "",
  });

  async function loadStudents() {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("teacher_token");
      const refresh = localStorage.getItem("teacher_refresh");
      let res = await fetch(`${API_URL}/api/students/`, {
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
            res = await fetch(`${API_URL}/api/students/`, {
              headers: { Authorization: `Bearer ${t.access}` },
            });
          }
        } else {
          localStorage.removeItem("teacher_token");
          localStorage.removeItem("teacher_refresh");
        }
      }
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to load students");
      // Sort by roll number
      data.sort((a, b) => a.roll_number.localeCompare(b.roll_number));
      setStudents(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadStudents();
  }, []);

  const filtered = useMemo(() => {
    return students.filter((s) => {
      if (filters.department && s.department !== filters.department)
        return false;
      if (filters.classYear && s.class_year !== filters.classYear) return false;
      if (filters.search) {
        const term = filters.search.toLowerCase();
        return (
          s.roll_number.toLowerCase().includes(term) ||
          s.full_name.toLowerCase().includes(term)
        );
      }
      return true;
    });
  }, [students, filters]);

  // Get unique departments and class years for filter dropdowns
  const departments = [...new Set(students.map((s) => s.department))].sort();
  const classYears = [...new Set(students.map((s) => s.class_year))].sort();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">All Students</h2>
        <button
          onClick={loadStudents}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Refresh
        </button>
      </div>

      <div className="bg-white shadow rounded p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
        <Input
          label="Search"
          value={filters.search}
          onChange={(v) => setFilters((f) => ({ ...f, search: v }))}
          placeholder="Search by name or roll number..."
          hint="Search student records"
        />
        <Select
          label="Department"
          value={filters.department}
          onChange={(v) => setFilters((f) => ({ ...f, department: v }))}
          options={departments}
          hint="Filter by department"
        />
        <Select
          label="Class / Year"
          value={filters.classYear}
          onChange={(v) => setFilters((f) => ({ ...f, classYear: v }))}
          options={classYears}
          hint="Filter by year"
        />
        <div className="flex items-end">
          <button
            className="border px-4 py-2 rounded w-full hover:bg-gray-50"
            onClick={() =>
              setFilters({ department: "", classYear: "", search: "" })
            }
            title="Clear all filters"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {loading && <div>Loading...</div>}
      {error && (
        <div className="bg-red-100 text-red-800 p-3 rounded">{error}</div>
      )}

      {!loading && !error && (
        <>
          <div className="bg-gray-50 p-3 rounded text-sm text-gray-700">
            Showing {filtered.length} of {students.length} students
          </div>

          <div className="bg-white shadow rounded overflow-auto">
            <table className="min-w-full">
              <thead>
                <tr className="text-left bg-gray-50">
                  <Th>Roll Number</Th>
                  <Th>Full Name</Th>
                  <Th>Department</Th>
                  <Th>Class/Year</Th>
                  <Th>Face Image</Th>
                  <Th>Registered</Th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((s) => (
                  <tr key={s.id} className="border-t hover:bg-gray-50">
                    <Td>
                      <span className="font-mono">{s.roll_number}</span>
                    </Td>
                    <Td>{s.full_name}</Td>
                    <Td>{s.department}</Td>
                    <Td>{s.class_year}</Td>
                    <Td>
                      {s.face_image ? (
                        <a
                          href={`${API_URL}${s.face_image}`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-blue-600 hover:underline text-sm"
                        >
                          View
                        </a>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </Td>
                    <Td>
                      {s.face_embedding_id ? (
                        <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                          ✓ Yes
                        </span>
                      ) : (
                        <span className="text-xs px-2 py-1 bg-gray-100 text-gray-800 rounded">
                          ✗ No
                        </span>
                      )}
                    </Td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <Td colSpan={6}>
                      <div className="text-center text-gray-500 py-6">
                        No students found.
                      </div>
                    </Td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

function Input({ label, value, onChange, placeholder, hint }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
      {hint && <p className="text-xs text-gray-500 mt-1">{hint}</p>}
    </div>
  );
}

function Select({ label, value, onChange, options, hint }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">All</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
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
