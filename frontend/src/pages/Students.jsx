import React, { useEffect, useMemo, useState } from "react";
import { DEPARTMENTS, getYearOptions } from "../constants/departments";

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
  const [showModal, setShowModal] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [formData, setFormData] = useState({
    roll_number: "",
    full_name: "",
    department: "",
    class_year: "",
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

      // Check if response is JSON
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error(
          `Server returned non-JSON response (${res.status}). Please check backend logs.`
        );
      }

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to load students");
      // Sort by roll number
      data.sort((a, b) => a.roll_number.localeCompare(b.roll_number));
      setStudents(data);
    } catch (e) {
      console.error("Error loading students:", e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadStudents();
  }, []);

  // Get available years based on selected department in form
  const availableFormYears = formData.department
    ? getYearOptions(formData.department)
    : [];

  // Handle department change in form - reset year
  const handleFormDepartmentChange = (value) => {
    setFormData((f) => ({ ...f, department: value, class_year: "" }));
  };

  function openCreateModal() {
    setEditingStudent(null);
    setFormData({
      roll_number: "",
      full_name: "",
      department: "",
      class_year: "",
    });
    setShowModal(true);
  }

  function openEditModal(student) {
    setEditingStudent(student);
    setFormData({
      roll_number: student.roll_number,
      full_name: student.full_name,
      department: student.department,
      class_year: student.class_year,
    });
    setShowModal(true);
  }

  function closeModal() {
    setShowModal(false);
    setEditingStudent(null);
    setFormData({
      roll_number: "",
      full_name: "",
      department: "",
      class_year: "",
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const token = localStorage.getItem("teacher_token");
      const url = editingStudent
        ? `${API_URL}/api/students/${editingStudent.id}/`
        : `${API_URL}/api/students/`;
      const method = editingStudent ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (!res.ok) {
        let msg = data.error || data.detail || "Operation failed";
        if (typeof data === "object" && !data.error && !data.detail) {
          const fieldErrors = Object.entries(data)
            .filter(([k, v]) => Array.isArray(v) && v.length)
            .map(([k, v]) => `${k}: ${v.join(", ")}`);
          if (fieldErrors.length) msg = fieldErrors.join("\n");
        }
        throw new Error(msg);
      }

      alert(
        editingStudent
          ? "Student updated successfully!"
          : "Student created successfully!"
      );
      closeModal();
      loadStudents();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  }

  async function deleteStudent(student) {
    if (
      !window.confirm(
        `Delete student ${student.full_name} (${student.roll_number})? This action cannot be undone.`
      )
    )
      return;

    try {
      const token = localStorage.getItem("teacher_token");
      const res = await fetch(`${API_URL}/api/students/${student.id}/`, {
        method: "DELETE",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to delete student");
      }

      alert("Student deleted successfully!");
      loadStudents();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  }

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
        <div className="space-x-3">
          <button
            onClick={openCreateModal}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            + Add Student
          </button>
          <button
            onClick={loadStudents}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Refresh
          </button>
        </div>
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
                  <Th>Actions</Th>
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
                    <Td>
                      <div className="flex gap-2">
                        <button
                          onClick={() => openEditModal(s)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          title="Edit student details"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => deleteStudent(s)}
                          className="text-red-600 hover:text-red-800 text-sm font-medium"
                          title="Delete student"
                        >
                          Delete
                        </button>
                      </div>
                    </Td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <Td colSpan={7}>
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

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-bold">
                {editingStudent ? "Edit Student" : "Add New Student"}
              </h3>
              <button
                onClick={closeModal}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              <FormInput
                label="Roll Number"
                value={formData.roll_number}
                onChange={(v) => setFormData((f) => ({ ...f, roll_number: v }))}
                placeholder="e.g., CS2021001"
                hint="Unique student identification number"
                required
              />
              <FormInput
                label="Full Name"
                value={formData.full_name}
                onChange={(v) => setFormData((f) => ({ ...f, full_name: v }))}
                placeholder="e.g., John Doe"
                hint="Student's complete name"
                required
              />
              <FormSelect
                label="Department"
                value={formData.department}
                onChange={handleFormDepartmentChange}
                options={DEPARTMENTS.map((d) => ({
                  value: d.value,
                  label: d.label,
                }))}
                hint="Select department or program"
                required
              />
              <FormSelect
                label="Class / Year"
                value={formData.class_year}
                onChange={(v) => setFormData((f) => ({ ...f, class_year: v }))}
                options={availableFormYears}
                hint="Select current year"
                disabled={!formData.department}
                required
              />

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  {editingStudent ? "Update" : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
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

function FormInput({ label, value, onChange, placeholder, hint, required }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500"> *</span>}
      </label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
      {hint && <p className="text-xs text-gray-500 mt-1">{hint}</p>}
    </div>
  );
}

function FormSelect({
  label,
  value,
  onChange,
  options,
  hint,
  required,
  disabled,
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500"> *</span>}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        disabled={disabled}
        className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
      >
        <option value="">-- Select {label} --</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {hint && <p className="text-xs text-gray-500 mt-1">{hint}</p>}
      {disabled && (
        <p className="text-xs text-orange-600 mt-1">
          Please select a department first
        </p>
      )}
    </div>
  );
}
