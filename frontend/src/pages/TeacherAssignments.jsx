import React, { useEffect, useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function TeacherAssignments() {
  const [assignments, setAssignments] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    teacher: "",
    subject: "",
    academic_year:
      new Date().getFullYear() + "-" + (new Date().getFullYear() + 1),
    notes: "",
  });
  const [filters, setFilters] = useState({
    teacher: "",
    department: "",
    search: "",
  });

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    setLoading(true);
    const token = localStorage.getItem("teacher_token");

    try {
      // Fetch all necessary data in parallel
      const [assignmentsRes, teachersRes, subjectsRes, deptRes] =
        await Promise.all([
          fetch(`${API_URL}/api/teacher-assignments/`, {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          }),
          fetch(`${API_URL}/api/teachers/`, {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          }),
          fetch(`${API_URL}/api/subjects/`, {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          }),
          fetch(`${API_URL}/api/departments/`, {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          }),
        ]);

      const [assignmentsData, teachersData, subjectsData, deptData] =
        await Promise.all([
          assignmentsRes.json(),
          teachersRes.json(),
          subjectsRes.json(),
          deptRes.json(),
        ]);

      setAssignments(assignmentsData);
      setTeachers(teachersData);
      setSubjects(subjectsData);
      setDepartments(deptData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const filteredAssignments = assignments.filter((a) => {
    if (filters.teacher && a.teacher !== parseInt(filters.teacher))
      return false;
    if (filters.department) {
      const subject = subjects.find((s) => s.id === a.subject);
      if (!subject || subject.department !== parseInt(filters.department))
        return false;
    }
    if (filters.search) {
      const term = filters.search.toLowerCase();
      const teacher = teachers.find((t) => t.id === a.teacher);
      const subject = subjects.find((s) => s.id === a.subject);
      return (
        (teacher && teacher.full_name.toLowerCase().includes(term)) ||
        (subject && subject.subject_name.toLowerCase().includes(term))
      );
    }
    return true;
  });

  async function handleSubmit(e) {
    e.preventDefault();
    const token = localStorage.getItem("teacher_token");

    try {
      const res = await fetch(`${API_URL}/api/teacher-assignments/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to create assignment");
      }

      await fetchData();
      setShowModal(false);
      setFormData({
        teacher: "",
        subject: "",
        academic_year:
          new Date().getFullYear() + "-" + (new Date().getFullYear() + 1),
        notes: "",
      });
    } catch (err) {
      alert(err.message);
    }
  }

  async function deleteAssignment(assignment) {
    if (
      !window.confirm(
        `Remove assignment for ${getTeacherName(assignment.teacher)}?`
      )
    )
      return;

    const token = localStorage.getItem("teacher_token");

    try {
      const res = await fetch(
        `${API_URL}/api/teacher-assignments/${assignment.id}/`,
        {
          method: "DELETE",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );

      if (!res.ok) throw new Error("Failed to delete assignment");

      await fetchData();
    } catch (err) {
      alert(err.message);
    }
  }

  function getTeacherName(teacherId) {
    const teacher = teachers.find((t) => t.id === teacherId);
    return teacher ? teacher.full_name : "Unknown";
  }

  function getSubjectName(subjectId) {
    const subject = subjects.find((s) => s.id === subjectId);
    return subject ? subject.subject_name : "Unknown";
  }

  function getSubjectDetails(subjectId) {
    const subject = subjects.find((s) => s.id === subjectId);
    if (!subject) return { dept: "-", year: "-" };
    return {
      dept: subject.department_code || "-",
      year: subject.class_year || "-",
    };
  }

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error}</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Teacher Subject Assignments</h2>
          <p className="text-gray-600">
            Assign teachers to subjects across departments and years
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-medium"
        >
          + Assign Teacher
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Filter by Teacher
          </label>
          <select
            value={filters.teacher}
            onChange={(e) =>
              setFilters((f) => ({ ...f, teacher: e.target.value }))
            }
            className="w-full border rounded px-3 py-2"
          >
            <option value="">All Teachers</option>
            {teachers.map((t) => (
              <option key={t.id} value={t.id}>
                {t.full_name} ({t.employee_id})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Filter by Department
          </label>
          <select
            value={filters.department}
            onChange={(e) =>
              setFilters((f) => ({ ...f, department: e.target.value }))
            }
            className="w-full border rounded px-3 py-2"
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.code} - {d.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <input
            type="text"
            value={filters.search}
            onChange={(e) =>
              setFilters((f) => ({ ...f, search: e.target.value }))
            }
            placeholder="Search teacher or subject..."
            className="w-full border rounded px-3 py-2"
          />
        </div>
      </div>

      {/* Results */}
      <div className="bg-gray-50 p-3 rounded text-sm text-gray-700">
        Showing {filteredAssignments.length} assignments
      </div>

      <div className="bg-white shadow rounded overflow-auto">
        <table className="min-w-full">
          <thead>
            <tr className="text-left bg-gray-50">
              <th className="px-3 py-2 text-sm font-semibold">Teacher</th>
              <th className="px-3 py-2 text-sm font-semibold">Subject</th>
              <th className="px-3 py-2 text-sm font-semibold">Department</th>
              <th className="px-3 py-2 text-sm font-semibold">Year</th>
              <th className="px-3 py-2 text-sm font-semibold">Academic Year</th>
              <th className="px-3 py-2 text-sm font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredAssignments.map((a) => {
              const details = getSubjectDetails(a.subject);
              return (
                <tr key={a.id} className="border-t hover:bg-gray-50">
                  <td className="px-3 py-2 text-sm">
                    {getTeacherName(a.teacher)}
                  </td>
                  <td className="px-3 py-2 text-sm">
                    {getSubjectName(a.subject)}
                  </td>
                  <td className="px-3 py-2 text-sm">{details.dept}</td>
                  <td className="px-3 py-2 text-sm">{details.year}</td>
                  <td className="px-3 py-2 text-sm">
                    {a.academic_year || "-"}
                  </td>
                  <td className="px-3 py-2 text-sm">
                    <button
                      onClick={() => deleteAssignment(a)}
                      className="text-red-600 hover:text-red-800 font-medium"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              );
            })}
            {filteredAssignments.length === 0 && (
              <tr>
                <td colSpan={6} className="px-3 py-6 text-center text-gray-500">
                  No assignments found. Click "Assign Teacher" to create one.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Create Assignment Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-bold">Assign Teacher to Subject</h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Teacher <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.teacher}
                  onChange={(e) =>
                    setFormData((f) => ({ ...f, teacher: e.target.value }))
                  }
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  <option value="">-- Select Teacher --</option>
                  {teachers.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.full_name} ({t.employee_id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.subject}
                  onChange={(e) =>
                    setFormData((f) => ({ ...f, subject: e.target.value }))
                  }
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  <option value="">-- Select Subject --</option>
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.department_code} - {s.class_year} - {s.subject_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Academic Year
                </label>
                <input
                  type="text"
                  value={formData.academic_year}
                  onChange={(e) =>
                    setFormData((f) => ({
                      ...f,
                      academic_year: e.target.value,
                    }))
                  }
                  placeholder="e.g., 2024-25"
                  className="w-full border rounded px-3 py-2"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Optional: Specify the academic year
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) =>
                    setFormData((f) => ({ ...f, notes: e.target.value }))
                  }
                  placeholder="Any additional notes..."
                  className="w-full border rounded px-3 py-2"
                  rows={3}
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Assign
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
