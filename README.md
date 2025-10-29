# Face Recognition Attendance System

A modern attendance management system using face recognition technology.

## 🏗️ Project Structure

```
vision/
├── backend/              # Django REST Framework - Main API
├── ai_service/          # FastAPI - Face Recognition Service
├── frontend/            # React + TailwindCSS
└── venv/               # Python virtual environment
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 16+
- Webcam/Camera

### Backend Setup (Django)

1. **Activate virtual environment:**

   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run migrations (already done):**

   ```bash
   cd backend
   python manage.py migrate
   ```

4. **Create superuser:**

   ```bash
   python manage.py createsuperuser
   ```

5. **Run Django server:**
   ```bash
   python manage.py runserver
   ```
   Server will run at: `http://localhost:8000`

### AI Service Setup (FastAPI)

1. **Install dependencies:**

   ```bash
   pip install -r ai_service/requirements.txt
   ```

2. **Run FastAPI server:**
   ```bash
   cd ai_service
   python main.py
   ```
   Server will run at: `http://localhost:8001`

### Frontend Setup (React)

1. **Navigate to frontend:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Run development server:**
   ```bash
   npm start
   ```
   App will run at: `http://localhost:3000`

## 📡 API Endpoints

### Django Backend (Port 8000)

#### Students

- `GET /api/students/` - List all students
- `POST /api/students/` - Create new student
- `GET /api/students/{id}/` - Get student details
- `PUT /api/students/{id}/` - Update student
- `DELETE /api/students/{id}/` - Delete student
- `GET /api/students/by_class/?department=X&class_year=Y` - Filter by class

#### Attendance

- `GET /api/attendance/sessions/` - List all sessions
- `POST /api/attendance/sessions/` - Create new session
- `GET /api/attendance/sessions/{id}/` - Get session details
- `POST /api/attendance/sessions/{id}/end_session/` - End session
- `POST /api/attendance/sessions/{id}/mark_attendance/` - Mark attendance

### AI Service (Port 8001)

- `POST /api/face/register` - Register student face
- `POST /api/face/recognize` - Recognize face from image

## 🔑 Key Features

1. **Student Registration**

   - Capture face via webcam
   - Store student details
   - Generate face embeddings using FaceNet

2. **Live Attendance**

   - Real-time face detection
   - Automatic attendance marking
   - Confidence scoring

3. **Reports**
   - View attendance history
   - Export as CSV/PDF
   - Filter by date, class, subject

## 🛠️ Technology Stack

| Component        | Technology            |
| ---------------- | --------------------- |
| Backend API      | Django REST Framework |
| AI Service       | FastAPI + DeepFace    |
| Frontend         | React + TailwindCSS   |
| Database         | SQLite                |
| Vector DB        | FAISS                 |
| Face Recognition | FaceNet / DeepFace    |

## 📝 Database Models

### Student

- roll_number (unique)
- full_name
- department
- class_year
- face_embedding_id
- face_image

### AttendanceSession

- department
- class_year
- subject
- start_time
- end_time
- is_active

### AttendanceRecord

- session (FK)
- student (FK)
- marked_at
- confidence
- status

## 🔧 Development Notes

- Virtual environment is in `venv/`
- Database file: `backend/db.sqlite3`
- FAISS index: `ai_service/faiss_index/`
- Media files: `backend/media/`

## 🎯 Next Steps

1. Complete AI service implementation (face recognition logic)
2. Build React frontend components
3. Integrate webcam capture
4. Add authentication (JWT)
5. Implement export functionality
6. Add error handling and validation

## 📄 License

This project is for educational purposes.
