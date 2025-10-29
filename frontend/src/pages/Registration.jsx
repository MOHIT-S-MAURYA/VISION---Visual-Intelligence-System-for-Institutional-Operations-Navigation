import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import { DEPARTMENTS, getYearOptions } from "../constants/departments";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function Registration() {
  const webcamRef = useRef(null);
  const [rollNumber, setRollNumber] = useState("");
  const [fullName, setFullName] = useState("");
  const [department, setDepartment] = useState("");
  const [classYear, setClassYear] = useState("");
  const [captured, setCaptured] = useState(null);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [frames, setFrames] = useState([]);
  const [frameCount, setFrameCount] = useState(5);

  // Get available years based on selected department
  const availableYears = department ? getYearOptions(department) : [];

  // Reset year when department changes
  const handleDepartmentChange = (value) => {
    setDepartment(value);
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
      formData.append("department", department);
      formData.append("class_year", classYear);
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
            placeholder="e.g., CS2021001"
            hint="Unique student identification number"
            required
          />
          <Input
            label="Full Name"
            value={fullName}
            onChange={setFullName}
            placeholder="e.g., John Doe"
            hint="Student's complete name"
            required
          />
          <Select
            label="Department"
            value={department}
            onChange={handleDepartmentChange}
            options={DEPARTMENTS.map((d) => ({
              value: d.value,
              label: d.label,
            }))}
            hint="Select department or program"
            required
          />
          <Select
            label="Class / Year"
            value={classYear}
            onChange={setClassYear}
            options={availableYears}
            hint="Select current year"
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
