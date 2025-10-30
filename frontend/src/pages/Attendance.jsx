import React, { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import { DEPARTMENTS, getYearOptions } from "../constants/departments";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function Attendance() {
  const [departmentId, setDepartmentId] = useState("");
  const [departmentCode, setDepartmentCode] = useState("");
  const [departmentName, setDepartmentName] = useState("");
  const [classYear, setClassYear] = useState("");
  const [subject, setSubject] = useState("");
  const [session, setSession] = useState(null);
  const [running, setRunning] = useState(false);
  const [recognized, setRecognized] = useState([]);
  const webcamRef = useRef(null);
  const intervalRef = useRef(null);
  const canvasRef = useRef(null);
  const [intervalMs, setIntervalMs] = useState(400); // Faster refresh: 400ms = 2.5 FPS
  const [availableSubjects, setAvailableSubjects] = useState([]);
  const processingRef = useRef(false); // Prevent overlapping requests

  // Teacher's teaching options from backend
  const [teacherDepartments, setTeacherDepartments] = useState([]);
  const [availableYears, setAvailableYears] = useState([]);
  const [loading, setLoading] = useState(true); // Fetch teacher's teaching options (departments and years they teach)
  useEffect(() => {
    const fetchTeachingOptions = async () => {
      const token = localStorage.getItem("teacher_token");
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `${API_URL}/api/teacher-assignments/my_teaching_options/`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setTeacherDepartments(data.departments || []);
          console.log("Teacher's departments:", data.departments);
        } else {
          console.error("Failed to fetch teaching options");
        }
      } catch (error) {
        console.error("Error fetching teaching options:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTeachingOptions();
  }, []);

  // Update available years when department changes
  useEffect(() => {
    if (departmentId) {
      const selectedDept = teacherDepartments.find(
        (d) => d.id.toString() === departmentId
      );
      if (selectedDept) {
        setAvailableYears(selectedDept.years || []);
      }
    } else {
      setAvailableYears([]);
    }
  }, [departmentId, teacherDepartments]);

  // Fetch subjects from API when department or year changes
  useEffect(() => {
    const fetchSubjects = async () => {
      if (!departmentId || !classYear) {
        setAvailableSubjects([]);
        return;
      }

      const token = localStorage.getItem("teacher_token");
      if (!token) return;

      try {
        const response = await fetch(
          `${API_URL}/api/subjects/?department=${departmentId}&class_year=${encodeURIComponent(
            classYear
          )}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        if (response.ok) {
          const data = await response.json();
          console.log("Available subjects:", data);
          setAvailableSubjects(data);
        } else {
          console.error("Failed to fetch subjects");
          setAvailableSubjects([]);
        }
      } catch (error) {
        console.error("Error fetching subjects:", error);
        setAvailableSubjects([]);
      }
    };

    fetchSubjects();
  }, [departmentId, classYear]);

  // Reset year and subject when department changes
  const handleDepartmentChange = (value) => {
    setDepartmentId(value);
    const selectedDept = teacherDepartments.find(
      (d) => d.id.toString() === value
    );
    if (selectedDept) {
      setDepartmentCode(selectedDept.code);
      setDepartmentName(selectedDept.name);
    }
    setClassYear("");
    setSubject("");
    setAvailableSubjects([]);
  };

  // Reset subject when year changes
  const handleYearChange = (value) => {
    setClassYear(value);
    setSubject("");
  };

  async function createSession(e) {
    e.preventDefault();
    // Frontend validation for required fields
    if (!departmentCode || !classYear.trim() || !subject.trim()) {
      alert(
        "Please fill all required fields: Department, Class/Year, Subject."
      );
      return;
    }
    try {
      const token = localStorage.getItem("teacher_token");
      const res = await fetch(`${API_URL}/api/attendance/sessions/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          department: departmentCode,
          class_year: classYear,
          subject,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        // Show backend validation errors if present
        let msg = data.error || data.detail || "Failed to create session";
        // If DRF serializer errors, show all field errors
        if (typeof data === "object" && data && !data.error && !data.detail) {
          const fieldErrors = Object.entries(data)
            .filter(([k, v]) => Array.isArray(v) && v.length)
            .map(([k, v]) => `${k}: ${v.join(", ")}`);
          if (fieldErrors.length) {
            msg = fieldErrors.join("\n");
          }
        }
        throw new Error(msg);
      }

      const data = await res.json();
      setSession(data);
      alert(`Session #${data.id} created successfully!`);
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  }

  function start() {
    if (!session) return alert("Create a session first");
    if (!session.is_active)
      return alert("Session is not active. Click 'Start Session' first.");
    setRunning(true);
    detectAndMarkFrame();
    intervalRef.current = setInterval(detectAndMarkFrame, intervalMs);
  }

  async function endSession() {
    if (!session) return;
    // Stop recognition if running
    if (running) {
      setRunning(false);
      clearInterval(intervalRef.current);
    }
    try {
      const token = localStorage.getItem("teacher_token");
      const res = await fetch(
        `${API_URL}/api/attendance/sessions/${session.id}/end_session/`,
        {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      if (res.ok) {
        const data = await res.json();
        setSession(data);
        alert("Session ended successfully!");
      } else {
        alert("Failed to end session");
      }
    } catch (err) {
      alert("Error ending session");
    }
  }

  async function startSession() {
    if (!session) return;
    try {
      const token = localStorage.getItem("teacher_token");
      const res = await fetch(
        `${API_URL}/api/attendance/sessions/${session.id}/start_session/`,
        {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      if (res.ok) {
        const data = await res.json();
        setSession(data);
        alert("Session started successfully!");
      } else {
        alert("Failed to start session");
      }
    } catch (err) {
      alert("Error starting session");
    }
  }

  async function stop() {
    setRunning(false);
    clearInterval(intervalRef.current);
    if (session) {
      try {
        const token = localStorage.getItem("teacher_token");
        await fetch(
          `${API_URL}/api/attendance/sessions/${session.id}/end_session/`,
          {
            method: "POST",
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          }
        );
      } catch {}
    }
  }

  async function detectAndMarkFrame() {
    // Skip if already processing (prevents request queuing)
    if (processingRef.current) return;

    // Check if session is still active before marking
    if (!session || !session.is_active) {
      setRunning(false);
      clearInterval(intervalRef.current);
      alert("Session is no longer active. Stopping attendance marking.");
      return;
    }

    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) return;

    processingRef.current = true;

    try {
      const formData = new FormData();
      const blob = await (await fetch(imageSrc)).blob();
      formData.append("frame", blob, "frame.jpg");

      const token = localStorage.getItem("teacher_token");
      const res = await fetch(
        `${API_URL}/api/attendance/sessions/${session.id}/recognize_frame/`,
        {
          method: "POST",
          body: formData,
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );

      if (!res.ok) {
        // Session might have been ended
        if (res.status === 400) {
          setRunning(false);
          clearInterval(intervalRef.current);
          alert("Session is not active. Stopping attendance.");
        }
        return;
      }

      const data = await res.json();
      drawFaces(data);

      const faces = Array.isArray(data.faces) ? data.faces : [];
      const newly = faces
        .filter((f) => f.recognized && f.student)
        .map((f) => ({
          student: f.student,
          confidence: f.confidence || 0,
          similarity: f.similarity || 0,
          ts: Date.now(),
        }));

      if (newly.length) {
        setRecognized((prev) => [...newly, ...prev].slice(0, 50));
      }
    } catch (err) {
      // Ignore transient errors but log them
      console.error("Recognition error:", err);
    } finally {
      processingRef.current = false;
    }
  }

  function drawFaces(payload) {
    // Use requestAnimationFrame for smoother rendering
    requestAnimationFrame(() => {
      try {
        const canvas = canvasRef.current;
        const video = webcamRef.current?.video;
        if (!canvas || !video) return;

        const ctx = canvas.getContext("2d");
        const vw = video.videoWidth || 1280;
        const vh = video.videoHeight || 720;

        // Only resize canvas if dimensions changed
        if (canvas.width !== vw || canvas.height !== vh) {
          canvas.width = vw;
          canvas.height = vh;
        }

        ctx.clearRect(0, 0, vw, vh);

        const imgW = payload?.image?.width || vw;
        const imgH = payload?.image?.height || vh;
        const sx = vw / imgW;
        const sy = vh / imgH;

        const faces = Array.isArray(payload?.faces) ? payload.faces : [];

        faces.forEach((f) => {
          const [x1, y1, x2, y2] = f.bbox || [0, 0, 0, 0];
          const rx1 = Math.max(0, Math.round(x1 * sx));
          const ry1 = Math.max(0, Math.round(y1 * sy));
          const rw = Math.max(1, Math.round((x2 - x1) * sx));
          const rh = Math.max(1, Math.round((y2 - y1) * sy));

          // Draw bounding box with thicker line for better visibility
          ctx.lineWidth = 3;
          ctx.strokeStyle = f.recognized ? "#22c55e" : "#ef4444"; // green for recognized, red for unknown
          ctx.strokeRect(rx1, ry1, rw, rh);

          // Draw label with better styling
          const label =
            f.recognized && f.student ? `${f.student.full_name}` : "Unknown";
          const similarity = f.similarity
            ? ` (${Math.round(f.similarity * 100)}%)`
            : "";
          const fullLabel = label + similarity;

          ctx.fillStyle = f.recognized
            ? "rgba(34,197,94,0.9)"
            : "rgba(239,68,68,0.9)";
          ctx.font = "bold 14px sans-serif";

          const tw = ctx.measureText(fullLabel).width + 12;
          const th = 20;
          ctx.fillRect(rx1, Math.max(0, ry1 - th - 2), tw, th);

          ctx.fillStyle = "#fff";
          ctx.fillText(fullLabel, rx1 + 6, Math.max(14, ry1 - 6));
        });
      } catch (err) {
        console.error("Draw error:", err);
      }
    });
  }

  useEffect(() => () => clearInterval(intervalRef.current), []);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Start Attendance</h2>

      <form
        onSubmit={createSession}
        className="bg-white shadow rounded p-6 grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        {loading ? (
          <div className="col-span-4 text-center py-4 text-gray-500">
            Loading your teaching assignments...
          </div>
        ) : teacherDepartments.length === 0 ? (
          <div className="col-span-4 text-center py-4 text-red-600">
            No teaching assignments found. Please contact admin.
          </div>
        ) : (
          <>
            <Select
              label="Department"
              value={departmentId}
              onChange={handleDepartmentChange}
              options={teacherDepartments.map((d) => ({
                value: d.id.toString(),
                label: `${d.code} - ${d.name}`,
              }))}
              hint="Select department you teach"
              required
            />
            <Select
              label="Class / Year"
              value={classYear}
              onChange={handleYearChange}
              options={availableYears.map((year) => ({
                value: year,
                label: year,
              }))}
              hint="Select class year"
              disabled={!departmentId}
              required
            />
            <Select
              label="Subject"
              value={subject}
              onChange={setSubject}
              options={availableSubjects.map((s) => ({
                value: s.subject_name,
                label: `${s.subject_code} - ${s.subject_name}`,
              }))}
              hint="Select subject"
              disabled={!departmentId || !classYear}
              required
            />
            <div className="flex items-end">
              <button
                className="bg-blue-600 text-white px-4 py-2 rounded w-full hover:bg-blue-700 disabled:bg-gray-400"
                disabled={loading || teacherDepartments.length === 0}
              >
                Create Session
              </button>
            </div>
          </>
        )}
      </form>

      {session && (
        <div className="flex items-center justify-between text-sm text-gray-700 bg-white rounded border p-3">
          <div>
            Session #{session.id}: {session.department} • {session.class_year} •{" "}
            {session.subject}
            <span
              className={`ml-2 text-xs px-2 py-1 rounded ${
                session.is_active
                  ? "bg-green-100 text-green-800"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {session.is_active ? "Active" : "Ended"}
            </span>
          </div>
          <div className="space-x-2">
            <button
              onClick={startSession}
              className="px-3 py-1 rounded border bg-green-50 hover:bg-green-100 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={session.is_active}
            >
              Start Session
            </button>
            <button
              onClick={endSession}
              className="px-3 py-1 rounded border bg-red-50 hover:bg-red-100 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!session.is_active}
            >
              End Session
            </button>
          </div>
        </div>
      )}

      <div className="bg-white shadow rounded p-4 flex flex-col md:flex-row gap-6">
        <div className="relative inline-block">
          <div className="mb-2">
            <p className="text-sm font-medium text-gray-700">
              Live Camera Feed
            </p>
            <p className="text-xs text-gray-500">
              Position student's face in the camera frame
            </p>
          </div>
          <Webcam
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            className="rounded border"
            videoConstraints={{
              facingMode: "user",
              width: { ideal: 1280 },
              height: { ideal: 720 },
              frameRate: { ideal: 30 },
            }}
            mirrored={true}
          />
          <canvas
            ref={canvasRef}
            className="absolute left-0 top-0 pointer-events-none"
          />
          <div className="mt-3 space-x-3 flex items-center gap-3">
            {!running ? (
              <button
                onClick={start}
                className="bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!session || !session.is_active}
                title={
                  !session
                    ? "Create a session first"
                    : !session.is_active
                    ? "Session is not active"
                    : "Start marking attendance automatically"
                }
              >
                Start Attendance
              </button>
            ) : (
              <button
                onClick={stop}
                className="bg-red-600 text-white px-4 py-2 rounded"
                title="Stop marking attendance"
              >
                Stop
              </button>
            )}
            <label className="text-sm font-medium text-gray-700">
              Scan Speed:
            </label>
            <input
              type="number"
              min={200}
              max={2000}
              step={100}
              value={intervalMs}
              onChange={(e) => setIntervalMs(parseInt(e.target.value) || 400)}
              className="w-24 border rounded px-2 py-1 focus:ring-2 focus:ring-blue-500"
              title="Time between scans (lower = faster response)"
            />
            <span className="text-xs text-gray-500">ms</span>
            <span className="text-xs text-green-600 font-medium">
              ({(1000 / intervalMs).toFixed(1)} FPS)
            </span>
            <span className="text-xs text-gray-400">
              Recommended: 300-500ms for best performance
            </span>
          </div>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold mb-2">Recognized</h3>
          <div className="space-y-2 max-h-96 overflow-auto">
            {recognized.map((item, idx) => (
              <div
                key={`${item.ts}-${idx}`}
                className="bg-gray-50 border rounded p-3 flex items-center justify-between"
              >
                <div>
                  <div className="font-semibold">
                    {item.student.full_name}{" "}
                    <span className="text-gray-500">
                      ({item.student.roll_number})
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {item.student.department} • {item.student.class_year}
                  </div>
                </div>
                <div className="text-sm">
                  Confidence: {(item.confidence * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {session && (
        <div className="flex items-center gap-4">
          <a
            className="text-blue-600 underline"
            href={`${API_URL}/api/attendance/sessions/${session.id}/export_csv/`}
            target="_blank"
            rel="noreferrer"
          >
            Download CSV
          </a>
          <span className="text-xs text-gray-500">Times in IST</span>
        </div>
      )}
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
