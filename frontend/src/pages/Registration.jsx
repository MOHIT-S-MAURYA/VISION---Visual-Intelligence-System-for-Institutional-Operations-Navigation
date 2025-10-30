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
    setMessage({
      type: "info",
      text: "Capturing multiple frames for robust registration...",
    });

    // Capture N frames over ~1-2s window for quality
    const N = Math.max(5, Math.min(10, frameCount));
    const captured = [];

    try {
      for (let i = 0; i < N; i++) {
        const imageSrc = webcamRef.current.getScreenshot({
          width: 640,
          height: 480,
        });
        if (imageSrc) captured.push(imageSrc);
        // 150ms interval = ~1.5s total for 10 frames
        await new Promise((r) => setTimeout(r, 150));
      }

      if (captured.length < 5) {
        setMessage({
          type: "error",
          text: `Only captured ${captured.length} frames. Please try again with better lighting.`,
        });
        return;
      }

      setCaptured(captured[captured.length - 1] || null);
      setFrames(captured);
      setMessage({
        type: "success",
        text: `✓ Captured ${captured.length} frames successfully. Ready to register!`,
      });
    } catch (error) {
      setMessage({
        type: "error",
        text: "Failed to capture frames. Please try again.",
      });
    }
  };

  const retake = () => {
    setCaptured(null);
    setFrames([]);
    setMessage(null);
  };

  async function onSubmit(e) {
    e.preventDefault();

    // Validation
    if (!captured || frames.length === 0) {
      setMessage({ type: "error", text: "Please capture face images first." });
      return;
    }

    if (frames.length < 5) {
      setMessage({
        type: "error",
        text: `Only ${frames.length} frames captured. Need at least 5 for reliable registration.`,
      });
      return;
    }

    setLoading(true);
    setMessage({ type: "info", text: `Processing ${frames.length} frames...` });

    try {
      const formData = new FormData();
      formData.append("roll_number", rollNumber);
      formData.append("full_name", fullName);
      formData.append("department", department); // Sends department ID (number)
      formData.append("class_year", classYear);
      if (email) formData.append("email", email);
      if (phone) formData.append("phone", phone);

      // Attach multiple frames
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

      if (!resp.ok) {
        const errorMsg = data.error || data.detail || "Registration failed";
        throw new Error(errorMsg);
      }

      // Success
      setMessage({
        type: "success",
        text: `✓ ${
          data.message || "Student registered successfully!"
        } (Frames: ${data.frames_processed || frames.length})`,
      });

      // Reset form
      setRollNumber("");
      setFullName("");
      setEmail("");
      setPhone("");
      setDepartment("");
      setClassYear("");
      setCaptured(null);
      setFrames([]);
      setSelectedDepartmentObj(null);
    } catch (err) {
      setMessage({
        type: "error",
        text: `Registration failed: ${err.message}`,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold flex items-center gap-3">
          👨‍🎓 Student Registration
        </h2>
        <p className="text-blue-100 mt-2">
          Register new student with face recognition for automated attendance
          tracking
        </p>
      </div>

      {message && (
        <div
          className={`p-4 rounded-lg border-l-4 ${
            message.type === "error"
              ? "bg-red-50 border-red-500 text-red-800"
              : message.type === "success"
              ? "bg-green-50 border-green-500 text-green-800"
              : "bg-blue-50 border-blue-500 text-blue-800"
          }`}
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">
              {message.type === "error"
                ? "❌"
                : message.type === "success"
                ? "✅"
                : "ℹ️"}
            </span>
            <div>
              <p className="font-semibold">
                {message.type === "error"
                  ? "Registration Failed"
                  : message.type === "success"
                  ? "Registration Successful"
                  : "Information"}
              </p>
              <p className="mt-1">{message.text}</p>
            </div>
          </div>
        </div>
      )}

      <form
        onSubmit={onSubmit}
        className="bg-white shadow-lg rounded-lg p-8 space-y-6"
      >
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2 mb-1">
            📋 Student Information
          </h3>
          <p className="text-sm text-gray-600">
            Enter student details below. Fields marked with * are required.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Roll Number / Student ID"
            value={rollNumber}
            onChange={setRollNumber}
            placeholder="Leave empty for auto-generation (e.g., CSE-2025-00001)"
            hint="💡 Optional - System will auto-generate format: DEPT-YEAR-XXXXX if left blank"
          />
          <Input
            label="Full Name *"
            value={fullName}
            onChange={setFullName}
            placeholder="Enter student's complete name"
            hint="📝 First name and last name (e.g., Rahul Kumar Sharma)"
            required
          />
          <Input
            label="Email Address"
            value={email}
            onChange={setEmail}
            placeholder="student@example.com"
            hint="📧 Optional - For communication and notifications"
            type="email"
          />
          <Input
            label="Phone Number"
            value={phone}
            onChange={setPhone}
            placeholder="+91 98765 43210"
            hint="📱 Optional - 10-digit mobile number with country code"
            type="tel"
          />
          <Select
            label="Department / Program *"
            value={department}
            onChange={handleDepartmentChange}
            options={availableDepartments.map((d) => ({
              value: d.id,
              label: `${d.code} - ${d.name}`,
            }))}
            hint={
              teacherAssignments.length > 0
                ? "🎓 Showing only departments you teach"
                : "🏫 Select the student's department or program"
            }
            required
          />
          <Select
            label="Academic Year / Semester *"
            value={classYear}
            onChange={setClassYear}
            options={availableYears.map((y) => ({ value: y, label: y }))}
            hint={
              teacherAssignments.length > 0 && department
                ? "📚 Showing only years you teach in this department"
                : "📅 Select current year of study (e.g., First Year, Second Year)"
            }
            disabled={!department}
            required
          />
        </div>

        <div className="pt-4 border-t">
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            📸 Face Recognition Setup *
            {frames.length > 0 && (
              <span className="text-sm font-normal text-green-600">
                ✓ {frames.length} frames captured successfully
              </span>
            )}
          </h3>
          <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-3">
            <p className="text-sm text-blue-900 font-semibold mb-2">
              📋 Important Guidelines for Face Capture:
            </p>
            <ul className="text-sm text-blue-800 ml-4 list-disc space-y-1.5">
              <li>
                <strong>Lighting:</strong> Ensure your face is well-lit (avoid
                backlighting or shadows)
              </li>
              <li>
                <strong>Position:</strong> Keep your face centered in the camera
                frame
              </li>
              <li>
                <strong>Accessories:</strong> Remove glasses, hats, masks, or
                face coverings
              </li>
              <li>
                <strong>Expression:</strong> Look directly at the camera with a
                neutral expression
              </li>
              <li>
                <strong>Distance:</strong> Position yourself 1-2 feet from the
                camera
              </li>
              <li>
                <strong>Auto-capture:</strong> System will capture {frameCount}{" "}
                frames automatically (~1-2 seconds)
              </li>
            </ul>
            <p className="text-xs text-blue-700 mt-2 italic">
              💡 Tip: Multiple frames ensure accurate face recognition during
              attendance
            </p>
          </div>
          {!captured ? (
            <div className="space-y-3">
              <Webcam
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={{
                  facingMode: "user",
                  width: 640,
                  height: 480,
                }}
                className="rounded border w-full"
                style={{ maxWidth: "640px" }}
              />
              <div className="bg-gray-50 border rounded p-3">
                <div className="flex items-center gap-3">
                  <label className="text-sm font-semibold text-gray-800 min-w-fit">
                    📊 Capture Quality:
                  </label>
                  <input
                    type="number"
                    min={5}
                    max={10}
                    value={frameCount}
                    onChange={(e) =>
                      setFrameCount(parseInt(e.target.value) || 7)
                    }
                    className="w-20 border-2 rounded-md px-3 py-2 text-center font-semibold focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    title="Number of frames to capture for face registration"
                  />
                  <span className="text-sm text-gray-700">frames</span>
                </div>
                <p className="text-xs text-gray-600 mt-2 ml-1">
                  ✓ <strong>5-7 frames:</strong> Standard accuracy (faster) •
                  <strong> 8-10 frames:</strong> Maximum accuracy (recommended)
                </p>
              </div>
              <button
                type="button"
                onClick={capture}
                className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all flex items-center gap-2"
              >
                📷 Start Face Capture ({frameCount} frames)
              </button>
              <p className="text-xs text-gray-500 italic">
                Click to begin automatic multi-frame capture process
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4">
                <p className="text-green-800 font-semibold mb-2 flex items-center gap-2">
                  ✓ Face Captured Successfully
                </p>
                <img
                  src={captured}
                  alt="Student face preview"
                  className="rounded-lg border-2 border-green-300 max-w-md"
                />
              </div>
              <div className="space-x-3">
                <button
                  type="button"
                  onClick={retake}
                  className="bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 rounded-lg font-medium shadow hover:shadow-md transition-all"
                >
                  🔄 Retake Photos
                </button>
                <span className="text-sm text-gray-600">
                  Not satisfied with the capture? Try again for better results
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={() => window.history.back()}
            className="bg-gray-400 hover:bg-gray-500 text-white px-6 py-3 rounded-lg font-medium"
          >
            Cancel
          </button>
          <button
            disabled={loading || !captured}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin">⏳</span>
                Processing {frames.length} frames...
              </>
            ) : (
              <>✅ Complete Registration</>
            )}
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
