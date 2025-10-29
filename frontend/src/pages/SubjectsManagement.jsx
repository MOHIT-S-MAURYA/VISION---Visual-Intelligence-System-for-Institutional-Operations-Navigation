import React, { useEffect, useState } from "react";
import { DEPARTMENTS, getYearOptions } from "../constants/departments";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function SubjectsManagement() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    department: "",
    classYear: "",
    search: "",
  });
  const [showModal, setShowModal] = useState(false);
  const [editingSubject, setEditingSubject] = useState(null);
  const [formData, setFormData] = useState({
    department: "",
    class_year: "",
    subject_name: "",
    subject_code: "",
  });
  const [teacherDepartment, setTeacherDepartment] = useState(null);
  const [isDepartmentLocked, setIsDepartmentLocked] = useState(false);

  // Fetch teacher's department on mount
  useEffect(() => {
    const fetchTeacherInfo = async () => {
      const token = localStorage.getItem("teacher_token");
      if (!token) return;

      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.teacher && data.teacher.department) {
            setTeacherDepartment(data.teacher.department);
            setFilters((prev) => ({
              ...prev,
              department: data.teacher.department,
            }));
            setIsDepartmentLocked(true);
          }
        }
      } catch (error) {
        console.error("Error fetching teacher info:", error);
      }
    };

    fetchTeacherInfo();
  }, []);

  // Get available years based on selected department
  const availableFilterYears = filters.department
    ? getYearOptions(filters.department)
    : [];

  const availableFormYears = formData.department
    ? getYearOptions(formData.department)
    : [];

  async function loadSubjects() {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("teacher_token");
      const params = new URLSearchParams();
      if (filters.department) params.append("department", filters.department);
      if (filters.classYear) params.append("class_year", filters.classYear);

      const res = await fetch(`${API_URL}/api/subjects/?${params}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to load subjects");
      setSubjects(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSubjects();
  }, [filters.department, filters.classYear]);

  const filteredSubjects = subjects.filter((s) => {
    if (filters.search) {
      const term = filters.search.toLowerCase();
      return (
        s.subject_name.toLowerCase().includes(term) ||
        (s.subject_code && s.subject_code.toLowerCase().includes(term))
      );
    }
    return true;
  });

  function openCreateModal() {
    setEditingSubject(null);
    setFormData({
      department: teacherDepartment || "",
      class_year: "",
      subject_name: "",
      subject_code: "",
    });
    setShowModal(true);
  }

  function openEditModal(subject) {
    setEditingSubject(subject);
    setFormData({
      department: subject.department,
      class_year: subject.class_year,
      subject_name: subject.subject_name,
      subject_code: subject.subject_code || "",
    });
    setShowModal(true);
  }

  function closeModal() {
    setShowModal(false);
    setEditingSubject(null);
    setFormData({
      department: "",
      class_year: "",
      subject_name: "",
      subject_code: "",
    });
  }

  const handleFormDepartmentChange = (value) => {
    setFormData((f) => ({ ...f, department: value, class_year: "" }));
  };

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const token = localStorage.getItem("teacher_token");
      const url = editingSubject
        ? `${API_URL}/api/subjects/${editingSubject.id}/`
        : `${API_URL}/api/subjects/`;
      const method = editingSubject ? "PUT" : "POST";

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
        editingSubject
          ? "Subject updated successfully!"
          : "Subject created successfully!"
      );
      closeModal();
      loadSubjects();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  }

  async function deleteSubject(subject) {
    if (
      !window.confirm(
        `Delete subject "${subject.subject_name}"? This action cannot be undone.`
      )
    )
      return;

    try {
      const token = localStorage.getItem("teacher_token");
      const res = await fetch(`${API_URL}/api/subjects/${subject.id}/`, {
        method: "DELETE",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to delete subject");
      }

      alert("Subject deleted successfully!");
      loadSubjects();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Subjects Management</h2>
        <div className="space-x-3">
          <button
            onClick={openCreateModal}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            + Add Subject
          </button>
          <button
            onClick={loadSubjects}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="bg-white shadow rounded p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
        <Select
          label="Department"
          value={filters.department}
          onChange={(v) => {
            setFilters((f) => ({ ...f, department: v, classYear: "" }));
          }}
          options={DEPARTMENTS.map((d) => ({ value: d.value, label: d.label }))}
          hint={
            isDepartmentLocked
              ? "🔒 Showing your department only"
              : "Filter by department"
          }
          disabled={isDepartmentLocked}
        />
        <Select
          label="Class / Year"
          value={filters.classYear}
          onChange={(v) => setFilters((f) => ({ ...f, classYear: v }))}
          options={availableFilterYears}
          hint="Filter by year"
          disabled={!filters.department}
        />
        <Input
          label="Search"
          value={filters.search}
          onChange={(v) => setFilters((f) => ({ ...f, search: v }))}
          placeholder="Search by subject name..."
          hint="Search subjects"
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
            Showing {filteredSubjects.length} subjects
          </div>

          <div className="bg-white shadow rounded overflow-auto">
            <table className="min-w-full">
              <thead>
                <tr className="text-left bg-gray-50">
                  <Th>Department</Th>
                  <Th>Year</Th>
                  <Th>Subject Name</Th>
                  <Th>Subject Code</Th>
                  <Th>Actions</Th>
                </tr>
              </thead>
              <tbody>
                {filteredSubjects.map((s) => (
                  <tr key={s.id} className="border-t hover:bg-gray-50">
                    <Td>{s.department}</Td>
                    <Td>{s.class_year}</Td>
                    <Td>{s.subject_name}</Td>
                    <Td>
                      {s.subject_code || (
                        <span className="text-gray-400">-</span>
                      )}
                    </Td>
                    <Td>
                      <div className="flex gap-2">
                        <button
                          onClick={() => openEditModal(s)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          title="Edit subject"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => deleteSubject(s)}
                          className="text-red-600 hover:text-red-800 text-sm font-medium"
                          title="Delete subject"
                        >
                          Delete
                        </button>
                      </div>
                    </Td>
                  </tr>
                ))}
                {filteredSubjects.length === 0 && (
                  <tr>
                    <Td colSpan={5}>
                      <div className="text-center text-gray-500 py-6">
                        No subjects found. Add some subjects to get started.
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
                {editingSubject ? "Edit Subject" : "Add New Subject"}
              </h3>
              <button
                onClick={closeModal}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              <FormSelect
                label="Department"
                value={formData.department}
                onChange={handleFormDepartmentChange}
                options={DEPARTMENTS.map((d) => ({
                  value: d.value,
                  label: d.label,
                }))}
                hint={
                  isDepartmentLocked
                    ? "🔒 Department is locked to your assigned department"
                    : "Select department"
                }
                disabled={isDepartmentLocked}
                required
              />
              <FormSelect
                label="Class / Year"
                value={formData.class_year}
                onChange={(v) => setFormData((f) => ({ ...f, class_year: v }))}
                options={availableFormYears}
                hint="Select year"
                disabled={!formData.department}
                required
              />
              <FormInput
                label="Subject Name"
                value={formData.subject_name}
                onChange={(v) =>
                  setFormData((f) => ({ ...f, subject_name: v }))
                }
                placeholder="e.g., Data Structures"
                hint="Full name of the subject"
                required
              />
              <FormInput
                label="Subject Code"
                value={formData.subject_code}
                onChange={(v) =>
                  setFormData((f) => ({ ...f, subject_code: v }))
                }
                placeholder="e.g., CS201 (optional)"
                hint="Subject code (optional)"
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
                  {editingSubject ? "Update" : "Create"}
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

function Select({ label, value, onChange, options, hint, disabled }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
      >
        <option value="">All</option>
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
