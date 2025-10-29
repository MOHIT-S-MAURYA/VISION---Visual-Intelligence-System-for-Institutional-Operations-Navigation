import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { DEPARTMENTS } from "../constants/departments";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function TeacherRegistration() {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    confirmPassword: "",
    email: "",
    full_name: "",
    department: "",
    employee_id: "",
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  async function onSubmit(e) {
    e.preventDefault();
    setError(null);

    // Validation
    if (
      !formData.username ||
      !formData.password ||
      !formData.full_name ||
      !formData.department
    ) {
      setError("Please fill in all required fields");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters long");
      return;
    }

    try {
      const res = await fetch(`${API_URL}/api/teachers/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          email: formData.email,
          full_name: formData.full_name,
          department: formData.department,
          employee_id: formData.employee_id || null,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        const errorMsg =
          data.username?.[0] ||
          data.employee_id?.[0] ||
          data.detail ||
          "Registration failed";
        throw new Error(errorMsg);
      }

      setSuccess(true);
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err) {
      setError(err.message);
    }
  }

  if (success) {
    return (
      <div className="max-w-md mx-auto bg-white shadow rounded p-6">
        <div className="text-center">
          <div className="text-green-600 text-5xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-green-800 mb-2">
            Registration Successful!
          </h2>
          <p className="text-gray-600 mb-4">
            Your teacher account has been created successfully.
          </p>
          <p className="text-sm text-gray-500">Redirecting to login page...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto bg-white shadow rounded p-6">
      <h2 className="text-2xl font-bold mb-2">Teacher Registration</h2>
      <p className="text-gray-600 mb-6">
        Create your teacher account to manage students and attendance
      </p>

      <form onSubmit={onSubmit} className="space-y-4">
        {/* Account Information */}
        <div className="border-b pb-4">
          <h3 className="text-lg font-semibold mb-3">Account Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Choose a username"
                className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                autoComplete="username"
              />
              <p className="text-xs text-gray-500 mt-1">
                This will be used for login
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email (Optional)
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.email@example.com"
                className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                autoComplete="email"
              />
              <p className="text-xs text-gray-500 mt-1">For account recovery</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Minimum 6 characters"
                className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                autoComplete="new-password"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Re-enter password"
                className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                autoComplete="new-password"
              />
            </div>
          </div>
        </div>

        {/* Personal Information */}
        <div className="border-b pb-4">
          <h3 className="text-lg font-semibold mb-3">Personal Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="Enter your full name"
                className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                autoComplete="name"
              />
              <p className="text-xs text-gray-500 mt-1">
                As per official records
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Employee ID (Optional)
              </label>
              <input
                type="text"
                name="employee_id"
                value={formData.employee_id}
                onChange={handleChange}
                placeholder="e.g., T123456"
                className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Your official employee ID
              </p>
            </div>
          </div>
        </div>

        {/* Department Selection */}
        <div className="pb-4">
          <h3 className="text-lg font-semibold mb-3">Department Assignment</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Department <span className="text-red-500">*</span>
            </label>
            <select
              name="department"
              value={formData.department}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">-- Select Department --</option>
              {DEPARTMENTS.map((dept) => (
                <option key={dept.value} value={dept.value}>
                  {dept.label}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              ⚠️ Important: You will only be able to manage students, subjects,
              and attendance for this department
            </p>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-100 text-red-800 rounded border border-red-200">
            {error}
          </div>
        )}

        <div className="flex justify-between items-center pt-4">
          <button
            type="button"
            onClick={() => navigate("/login")}
            className="text-blue-600 hover:text-blue-800 underline"
          >
            Already have an account? Login
          </button>
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-medium"
          >
            Register
          </button>
        </div>
      </form>
    </div>
  );
}
