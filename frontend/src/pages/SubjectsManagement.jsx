import React, { useEffect, useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function SubjectsManagement() {
  const [subjects, setSubjects] = useState([]);
  const [departments, setDepartments] = useState([]);
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
    credits: 3,
  });
  const [teacherAssignments, setTeacherAssignments] = useState([]);
  const [selectedDepartmentObj, setSelectedDepartmentObj] = useState(null);
  const [selectedFilterDeptObj, setSelectedFilterDeptObj] = useState(null);

  // Fetch departments and teacher info on mount
  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("teacher_token");

      // Fetch departments
      try {
        const deptResponse = await fetch(`${API_URL}/api/departments/`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });

        if (deptResponse.ok) {
          const deptData = await deptResponse.json();
          setDepartments(deptData);
        }
      } catch (error) {
        console.error("Error fetching departments:", error);
      }

      // Fetch teacher info if logged in
      if (token) {
        try {
          const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });

          if (response.ok) {
            const data = await response.json();
            if (data.teacher && data.teacher.assignments) {
              setTeacherAssignments(data.teacher.assignments);
            }
          }
        } catch (error) {
          console.error("Error fetching teacher info:", error);
        }
      }
    };

    fetchData();
  }, []);

  // Get available departments based on teacher assignments
  const availableDepartments =
    teacherAssignments.length > 0
      ? departments.filter((dept) =>
          teacherAssignments.some(
            (assignment) => assignment.department.id === dept.id
          )
        )
      : departments;

  // Get available class years for filter based on department and teacher assignments
  const getAvailableFilterYears = () => {
    if (!selectedFilterDeptObj) return [];

    if (teacherAssignments.length > 0) {
      const yearsSet = new Set();
      teacherAssignments
        .filter((a) => a.department.id === selectedFilterDeptObj.id)
        .forEach((a) => yearsSet.add(a.subject.class_year));
      return Array.from(yearsSet).sort();
    }

    const years = [];
    const yearNames = ["First", "Second", "Third", "Fourth", "Fifth"];
    for (let i = 0; i < selectedFilterDeptObj.duration_years; i++) {
      years.push(`${yearNames[i]} Year`);
    }
    return years;
  };

  // Get available class years for form based on department
  const getAvailableFormYears = () => {
    if (!selectedDepartmentObj) return [];

    const years = [];
    const yearNames = ["First", "Second", "Third", "Fourth", "Fifth"];
    for (let i = 0; i < selectedDepartmentObj.duration_years; i++) {
      years.push(`${yearNames[i]} Year`);
    }
    return years;
  };

  const availableFilterYears = getAvailableFilterYears();
  const availableFormYears = getAvailableFormYears();

  async function loadSubjects() {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("teacher_token");
      const params = new URLSearchParams();
      if (filters.department)
        params.append("department_id", filters.department); // department_id for filtering
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    const defaultDept = availableDepartments[0]?.id || "";
    setFormData({
      department: defaultDept,
      class_year: "",
      subject_name: "",
      subject_code: "",
      credits: 3,
    });
    if (defaultDept) {
      setSelectedDepartmentObj(departments.find((d) => d.id === defaultDept));
    }
    setShowModal(true);
  }

  function openEditModal(subject) {
    setEditingSubject(subject);
    setFormData({
      department: subject.department, // department ID
      class_year: subject.class_year,
      subject_name: subject.subject_name,
      subject_code: subject.subject_code || "",
      credits: subject.credits || 3,
    });
    setSelectedDepartmentObj(
      departments.find((d) => d.id === subject.department)
    );
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
      credits: 3,
    });
    setSelectedDepartmentObj(null);
  }

  const handleFormDepartmentChange = (value) => {
    const deptId = parseInt(value);
    setFormData((f) => ({ ...f, department: deptId, class_year: "" }));
    setSelectedDepartmentObj(departments.find((d) => d.id === deptId));
  };

  const handleFilterDepartmentChange = (value) => {
    const deptId = value ? parseInt(value) : "";
    setFilters((f) => ({ ...f, department: deptId, classYear: "" }));
    setSelectedFilterDeptObj(
      deptId ? departments.find((d) => d.id === deptId) : null
    );
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
          onChange={handleFilterDepartmentChange}
          options={availableDepartments.map((d) => ({
            value: d.id,
            label: `${d.code} - ${d.name}`,
          }))}
          hint={
            teacherAssignments.length > 0
              ? "🎓 Showing only your assigned departments"
              : "Filter by department"
          }
        />
        <Select
          label="Class / Year"
          value={filters.classYear}
          onChange={(v) => setFilters((f) => ({ ...f, classYear: v }))}
          options={availableFilterYears.map((y) => ({ value: y, label: y }))}
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
            onClick={() => {
              setFilters({ department: "", classYear: "", search: "" });
              setSelectedFilterDeptObj(null);
            }}
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
                  <Th>Credits</Th>
                  <Th>Actions</Th>
                </tr>
              </thead>
              <tbody>
                {filteredSubjects.map((s) => (
                  <tr key={s.id} className="border-t hover:bg-gray-50">
                    <Td>{s.department_code || s.department}</Td>
                    <Td>{s.class_year}</Td>
                    <Td>{s.subject_name}</Td>
                    <Td>
                      {s.subject_code || (
                        <span className="text-gray-400">-</span>
                      )}
                    </Td>
                    <Td>{s.credits || 3}</Td>
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
                    <Td colSpan={6}>
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
                options={availableDepartments.map((d) => ({
                  value: d.id,
                  label: `${d.code} - ${d.name}`,
                }))}
                hint={
                  teacherAssignments.length > 0
                    ? "🎓 Showing only your assigned departments"
                    : "Select department"
                }
                required
              />
              <FormSelect
                label="Class / Year"
                value={formData.class_year}
                onChange={(v) => setFormData((f) => ({ ...f, class_year: v }))}
                options={availableFormYears.map((y) => ({
                  value: y,
                  label: y,
                }))}
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
                placeholder="e.g., Data Structures and Algorithms"
                hint="Full name of the subject"
                required
              />
              <FormInput
                label="Subject Code"
                value={formData.subject_code}
                onChange={(v) =>
                  setFormData((f) => ({ ...f, subject_code: v }))
                }
                placeholder="e.g., CS301 (optional)"
                hint="Official subject code (optional)"
              />
              <FormInput
                label="Credits"
                type="number"
                value={formData.credits}
                onChange={(v) =>
                  setFormData((f) => ({ ...f, credits: parseInt(v) || 3 }))
                }
                placeholder="e.g., 4"
                hint="Number of credits for this subject"
                min="1"
                max="10"
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

function FormInput({
  label,
  value,
  onChange,
  placeholder,
  hint,
  required,
  type = "text",
  min,
  max,
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500"> *</span>}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        min={min}
        max={max}
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
