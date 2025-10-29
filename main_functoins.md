## 🎯 Prototype Functional Overview

### Core Users

- **Teacher** — Primary user for prototype (manages registration and attendance)
- **Student** — Only appears as data; no login or direct interface

---

## 🚀 Core Functionalities

### 1. **Student Registration**

#### Goal

Register a new student with their details and facial embedding (captured live from the camera).

#### Workflow

1. **Navigate to Registration Page**

   - Form fields:

     - Full Name
     - Roll Number / ID
     - Department (dropdown or input)
     - Class / Year

   - “Open Camera” button

2. **Live Face Capture**

   - Opens webcam feed inside the form.
   - The teacher clicks **“Capture Face”** — the app:

     - Takes 3–5 frames of the student.
     - Sends them to backend `/api/face/register` endpoint (FastAPI service).
     - Backend extracts **face embeddings** using **FaceNet / DeepFace** and stores:

       - Student metadata (name, roll number, dept, class)
       - Face embeddings in **FAISS** index.
       - Reference image (optional) in Media/Storage service (e.g., S3/local).

3. **Confirmation**

   - Displays “✅ Student Registered Successfully”
   - Shows thumbnail of captured face.

#### Technical Flow

- **Frontend**: React + Camera API → Base64 image → POST to `/api/face/register`
- **Backend (FastAPI)**: Extract embeddings → Store in FAISS → Return success response
- **Database**: Student details + embedding ID linked.

---

### 2. **Start Attendance**

#### Goal

Automatically mark attendance using the live camera for a selected class and subject.

#### Workflow

1. **Navigate to Attendance Page**

   - Dropdowns:

     - Department
     - Class / Year
     - Subject

   - “Start Attendance” button.

2. **Live Detection Mode**

   - Opens webcam in full screen.
   - Streams frames to backend `/api/face/recognize`.
   - Backend compares embeddings (FAISS search) → identifies known faces → marks attendance in database.

3. **Real-Time UI**

   - Detected student faces appear in a grid with:

     - Name
     - Roll Number
     - Confidence %
     - ✅ “Present” badge

4. **Stop Attendance**

   - “Stop Session” button → ends capture session.
   - Attendance summary table appears:

     | Roll No | Name         | Status     | Time     |
     | ------- | ------------ | ---------- | -------- |
     | 01      | Mohit Maurya | ✅ Present | 09:45 AM |
     | 02      | Priya Singh  | ❌ Absent  | —        |

5. **Save Report**

   - Option to export as `.csv` or `.pdf`
   - Automatically stored in backend under `/api/attendance/session/<id>/report`

#### Technical Flow

- **Frontend**: React camera stream → WebSocket or interval POST to `/api/face/recognize`
- **Backend (FastAPI)**: Match embeddings → Respond with recognized student info
- **Backend (DRF)**: Update attendance DB → Return session report
- **Frontend**: Render dynamic recognition results.

---

## 🧠 Design Philosophy

- **Simplicity**: Two major pages → Register & Attendance.
- **Minimal Interaction**: Teacher can operate with minimal clicks.
- **Live Camera Only**: No photo uploads; all real-time.
- **Modern UI**: Tailwind CSS + React animations.
- **Instant Feedback**: Loading states, success toasts, and clear confirmation messages.

---

## 🧩 Prototype Pages (Frontend)

| Page               | Path          | Description                             |
| ------------------ | ------------- | --------------------------------------- |
| `Login`            | `/login`      | Simple login for teacher                |
| `Register Student` | `/register`   | Add student details + capture face      |
| `Attendance`       | `/attendance` | Start/stop live camera-based attendance |
| `Reports`          | `/reports`    | View and export attendance records      |

---

## ⚙️ Tech Stack Overview

| Layer                  | Technology                   | Description                                |
| ---------------------- | ---------------------------- | ------------------------------------------ |
| **Frontend**           | React + TailwindCSS          | Clean UI with responsive design            |
| **Backend API (Core)** | Django REST Framework        | Handles attendance data, user, and storage |
| **AI / Vision Engine** | FastAPI + DeepFace / FaceNet | Handles embedding creation and recognition |
| **Database**           | SQLite + FAISS Vector DB     | Relational + vector search hybrid          |
| **Media Storage**      | Local /                      | Stores face images or session captures     |

---
