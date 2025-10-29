import React, { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function Attendance() {
  const [department, setDepartment] = useState("");
  const [classYear, setClassYear] = useState("");
  const [subject, setSubject] = useState("");
  const [session, setSession] = useState(null);
  const [running, setRunning] = useState(false);
  const [recognized, setRecognized] = useState([]);
  const webcamRef = useRef(null);
  const intervalRef = useRef(null);
  const canvasRef = useRef(null);
  const [intervalMs, setIntervalMs] = useState(800);

  async function createSession(e) {
    e.preventDefault();
    // Frontend validation for required fields
    if (!department.trim() || !classYear.trim() || !subject.trim()) {
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
        body: JSON.stringify({ department, class_year: classYear, subject }),
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
    // Check if session is still active before marking
    if (!session || !session.is_active) {
      setRunning(false);
      clearInterval(intervalRef.current);
      alert("Session is no longer active. Stopping attendance marking.");
      return;
    }

    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) return;
    const formData = new FormData();
    const blob = await (await fetch(imageSrc)).blob();
    formData.append("frame", blob, "frame.jpg");

    try {
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
          ts: Date.now(),
        }));
      if (newly.length) {
        setRecognized((prev) => [...newly, ...prev].slice(0, 50));
      }
    } catch (err) {
      // ignore transient errors
    }
  }

  function drawFaces(payload) {
    try {
      const canvas = canvasRef.current;
      const video = webcamRef.current?.video;
      if (!canvas || !video) return;
      const ctx = canvas.getContext("2d");
      const vw = video.videoWidth || 640;
      const vh = video.videoHeight || 480;
      canvas.width = vw;
      canvas.height = vh;
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
        ctx.lineWidth = 2;
        ctx.strokeStyle = f.recognized ? "#22c55e" : "#ef4444"; // green for recognized, red for unknown
        ctx.strokeRect(rx1, ry1, rw, rh);
        const label =
          f.recognized && f.student ? `${f.student.full_name}` : "Unknown";
        ctx.fillStyle = f.recognized
          ? "rgba(34,197,94,0.85)"
          : "rgba(239,68,68,0.85)";
        ctx.font = "12px sans-serif";
        const tw = ctx.measureText(label).width + 8;
        const th = 16;
        ctx.fillRect(rx1, Math.max(0, ry1 - th), tw, th);
        ctx.fillStyle = "#fff";
        ctx.fillText(label, rx1 + 4, Math.max(12, ry1 - 4));
      });
    } catch {}
  }

  useEffect(() => () => clearInterval(intervalRef.current), []);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Start Attendance</h2>

      <form
        onSubmit={createSession}
        className="bg-white shadow rounded p-6 grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <Input
          label="Department"
          value={department}
          onChange={setDepartment}
          placeholder="e.g., CSE, ECE"
          hint="Enter department code or name"
          required
        />
        <Input
          label="Class / Year"
          value={classYear}
          onChange={setClassYear}
          placeholder="e.g., First Year"
          hint="Student year or class"
          required
        />
        <Input
          label="Subject"
          value={subject}
          onChange={setSubject}
          placeholder="e.g., Data Structures"
          hint="Subject or course name"
          required
        />
        <div className="flex items-end">
          <button className="bg-blue-600 text-white px-4 py-2 rounded w-full">
            Create Session
          </button>
        </div>
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
            videoConstraints={{ facingMode: "user" }}
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
              Scan Interval:
            </label>
            <input
              type="number"
              min={300}
              max={3000}
              step={100}
              value={intervalMs}
              onChange={(e) => setIntervalMs(parseInt(e.target.value) || 800)}
              className="w-24 border rounded px-2 py-1 focus:ring-2 focus:ring-blue-500"
              title="Time between face scans in milliseconds"
            />
            <span className="text-xs text-gray-500">ms</span>
            <span className="text-xs text-gray-400">
              (300-3000ms, faster = more frequent scans)
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
