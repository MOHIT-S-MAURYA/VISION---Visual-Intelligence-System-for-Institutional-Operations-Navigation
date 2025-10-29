import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
const AI_URL = process.env.REACT_APP_AI_SERVICE_URL || "http://localhost:8001";

export default function Dashboard() {
  const [backendStatus, setBackendStatus] = useState("🔄");
  const [aiStatus, setAiStatus] = useState("🔄");
  const [totalStudents, setTotalStudents] = useState("-");

  async function checkStatus() {
    try {
      const token = localStorage.getItem("teacher_token");
      const res = await fetch(`${API_URL}/api/students/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        setBackendStatus("✅");
        const data = await res.json();
        setTotalStudents(data.length);
      } else setBackendStatus("❌");
    } catch {
      setBackendStatus("❌");
      setTotalStudents("0");
    }

    try {
      const res = await fetch(`${AI_URL}/`);
      setAiStatus(res.ok ? "✅" : "❌");
    } catch {
      setAiStatus("❌");
    }
  }

  useEffect(() => {
    checkStatus();
    const t = setInterval(checkStatus, 30000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Register Student" icon="👤" to="/register" color="blue" />
        <Card
          title="Start Attendance"
          icon="📸"
          to="/attendance"
          color="green"
        />
        <Card title="View Reports" icon="📊" to="/reports" color="purple" />
      </div>

      <div className="bg-white shadow rounded p-6">
        <h2 className="text-xl font-bold mb-4">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Metric label="Total Students" value={totalStudents} color="blue" />
          <Metric label="Backend Status" value={backendStatus} color="green" />
          <Metric label="AI Service Status" value={aiStatus} color="purple" />
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded p-4">
        <h3 className="font-semibold text-blue-900 mb-2">Quick Start</h3>
        <ol className="list-decimal list-inside text-blue-800 space-y-1">
          <li>Register students with face capture</li>
          <li>Create a session and start attendance</li>
          <li>View/export reports</li>
        </ol>
      </div>
    </div>
  );
}

function Card({ title, icon, to, color }) {
  const colorMap = {
    blue: "bg-blue-600 hover:bg-blue-700",
    green: "bg-green-600 hover:bg-green-700",
    purple: "bg-purple-600 hover:bg-purple-700",
  };
  return (
    <div className="bg-white shadow rounded p-6">
      <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center text-3xl mb-3">
        {icon}
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <Link
        className={`inline-block text-white px-4 py-2 rounded ${colorMap[color]}`}
        to={to}
      >
        Open →
      </Link>
    </div>
  );
}

function Metric({ label, value, color }) {
  const border = {
    blue: "border-blue-500",
    green: "border-green-500",
    purple: "border-purple-500",
  }[color];
  return (
    <div className={`border-l-4 ${border} pl-4`}>
      <p className="text-gray-600 text-sm">{label}</p>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}
