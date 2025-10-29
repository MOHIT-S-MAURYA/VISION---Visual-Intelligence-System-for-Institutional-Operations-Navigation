import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function Registration() {
  const webcamRef = useRef(null);
  const [rollNumber, setRollNumber] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [department, setDepartment] = useState("");
  const [classYear, setClassYear] = useState("");
  const [captured, setCaptured] = useState(null);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [frames, setFrames] = useState([]);
  const [frameCount, setFrameCount] = useState(5);
  const [departments, setDepartments] = useState([]);
  const [teacherAssignments, setTeacherAssignments] = useState([]);
  const [selectedDepartmentObj, setSelectedDepartmentObj] = useState(null);

  // Fetch teacher's assignments and departments on mount
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

  // Get available class years based on selected department and teacher assignments
  const getAvailableYears = () => {
    if (!selectedDepartmentObj) return [];

    if (teacherAssignments.length > 0) {
      // For teachers, show only years they teach in this department
      const yearsSet = new Set();
      teacherAssignments
        .filter((a) => a.department.id === selectedDepartmentObj.id)
        .forEach((a) => yearsSet.add(a.subject.class_year));
      return Array.from(yearsSet).sort();
    }

    // For admins/non-teachers, show all years based on department duration
    const years = [];
    const yearNames = ["First", "Second", "Third", "Fourth", "Fifth"];
    for (let i = 0; i < selectedDepartmentObj.duration_years; i++) {
      years.push(`${yearNames[i]} Year`);
    }
    return years;
  };

  const availableYears = getAvailableYears();

  // Handle department change
  const handleDepartmentChange = (value) => {
    const deptId = parseInt(value);
    setDepartment(deptId);
    const deptObj = departments.find((d) => d.id === deptId);
    setSelectedDepartmentObj(deptObj);
    setClassYear(""); // Reset year when department changes
  };

  const capture = async () => {
    // capture N frames over ~1s window
    const N = Math.max(3, Math.min(10, frameCount));
    const captured = [];
    for (let i = 0; i < N; i++) {
      const imageSrc = webcamRef.current.getScreenshot({
        width: 480,
        height: 360,
      });
      if (imageSrc) captured.push(imageSrc);
      await new Promise((r) => setTimeout(r, 120));
    }
    setCaptured(captured[captured.length - 1] || null);
    setFrames(captured);
  };

  const retake = () => setCaptured(null);

  async function onSubmit(e) {
    e.preventDefault();
    if (!captured || frames.length === 0) {
      setMessage({ type: "error", text: "Please capture a face image." });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append("roll_number", rollNumber);
      formData.append("full_name", fullName);
      formData.append("department", department); // Now sends department ID (number)
      formData.append("class_year", classYear);
      if (email) formData.append("email", email);
      if (phone) formData.append("phone", phone);
      // attach multiple frames
      for (let i = 0; i < frames.length; i++) {
        const res = await fetch(frames[i]);
        const blob = await res.blob();
        formData.append("face_images", blob, `face_${i}.jpg`);
      }

      const token = localStorage.getItem("teacher_token");
      const resp = await fetch(
        `${API_URL}/api/students/register_with_face_multi/`,
        {
          method: "POST",
          body: formData,
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      const data = await resp.json();

      if (!resp.ok) throw new Error(data.error || "Registration failed");
      setMessage({ type: "success", text: "Student registered successfully!" });
      setRollNumber("");
      setFullName("");
      setDepartment("");
      setClassYear("");
      setCaptured(null);
      setFrames([]);
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Student Registration</h2>

      <form
        onSubmit={onSubmit}
        className="bg-white shadow rounded p-6 space-y-4"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Roll Number"
            value={rollNumber}
            onChange={setRollNumber}
            placeholder="e.g., 2025CS001"
            hint="Unique student identification number"
            required
          />
          <Input
            label="Full Name"
            value={fullName}
            onChange={setFullName}
            placeholder="e.g., Rahul Sharma"
            hint="Student's complete name"
            required
          />
          <Input
            label="Email (Optional)"
            value={email}
            onChange={setEmail}
            placeholder="e.g., rahul.sharma@college.edu"
            hint="Student's email address"
            type="email"
          />
          <Input
            label="Phone (Optional)"
            value={phone}
            onChange={setPhone}
            placeholder="e.g., +91 98765 43210"
            hint="Contact number"
            type="tel"
          />
          <Select
            label="Department"
            value={department}
            onChange={handleDepartmentChange}
            options={availableDepartments.map((d) => ({
              value: d.id,
              label: `${d.code} - ${d.name}`,
            }))}
            hint={
              teacherAssignments.length > 0
                ? "🎓 Showing only departments you teach"
                : "Select department or program"
            }
            required
          />
          <Select
            label="Class / Year"
            value={classYear}
            onChange={setClassYear}
            options={availableYears.map((y) => ({ value: y, label: y }))}
            hint={
              teacherAssignments.length > 0 && department
                ? "📚 Showing only years you teach in this department"
                : "Select current year"
            }
            disabled={!department}
            required
          />
        </div>

        <div className="pt-4 border-t">
          <h3 className="font-semibold mb-2">Face Capture</h3>
          <p className="text-sm text-gray-600 mb-3">
            Position your face in the camera and click capture. Multiple frames
            will be captured for better accuracy.
          </p>
          {!captured ? (
            <div className="space-y-3">
              <Webcam
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={{ facingMode: "user" }}
                className="rounded border"
              />
              <div className="flex items-center gap-3">
                <label className="text-sm font-medium text-gray-700">
                  Frames to capture:
                </label>
                <input
                  type="number"
                  min={3}
                  max={10}
                  value={frameCount}
                  onChange={(e) => setFrameCount(parseInt(e.target.value) || 5)}
                  className="w-20 border rounded px-2 py-1 focus:ring-2 focus:ring-blue-500"
                  title="Number of frames to capture (3-10)"
                />
                <span className="text-xs text-gray-500">
                  More frames = better accuracy (recommended: 5-7)
                </span>
              </div>
              <button
                type="button"
                onClick={capture}
                className="bg-green-600 text-white px-4 py-2 rounded"
              >
                Capture Face (Multi-frame)
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <img
                src={captured}
                alt="Captured"
                className="rounded border max-w-md"
              />
              <div className="space-x-3">
                <button
                  type="button"
                  onClick={retake}
                  className="bg-yellow-600 text-white px-4 py-2 rounded"
                >
                  Retake
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end">
          <button
            disabled={loading || !captured}
            className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            {loading ? "Registering..." : "Register Student"}
          </button>
        </div>

        {message && (
          <div
            className={`p-3 rounded ${
              message.type === "success"
                ? "bg-green-100 text-green-800"
                : "bg-red-100 text-red-800"
            }`}
          >
            {message.text}
          </div>
        )}
      </form>
    </div>
  );
}

function Input({ label, value, onChange, required, placeholder, hint }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500"> *</span>}
      </label>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        placeholder={placeholder}
        className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      />
      {hint && <p className="text-xs text-gray-500 mt-1">{hint}</p>}
    </div>
  );
}

function Select({ label, value, onChange, options, hint, required, disabled }) {
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
