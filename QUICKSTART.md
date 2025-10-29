# 🚀 Quick Start Guide

## Initial Setup (One-time)

### 1. Backend Setup

```bash
# Activate virtual environment (already created)
source venv/bin/activate

# Django backend is already set up with migrations applied
# Create a superuser for admin access
cd backend
python manage.py createsuperuser
cd ..
```

### 2. Start Development Servers

#### Option A: Using the startup script

```bash
./start.sh
```

#### Option B: Manual start

**Terminal 1 - Django Backend:**

```bash
source venv/bin/activate
cd backend
python manage.py runserver
# Runs on http://localhost:8000
```

**Terminal 2 - AI Service (when ready):**

```bash
source venv/bin/activate
# First install AI dependencies if not already done
pip install -r ai_service/requirements.txt
cd ai_service
python main.py
# Runs on http://localhost:8001
```

**Terminal 3 - Frontend (when ready):**

```bash
cd frontend
npm install  # First time only
npm start
# Runs on http://localhost:3000
```

## Testing the API

### Test Django Backend

```bash
# List students
curl http://localhost:8000/api/students/

# Create a student
curl -X POST http://localhost:8000/api/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "001",
    "full_name": "John Doe",
    "department": "Computer Science",
    "class_year": "2024"
  }'
```

### Access Admin Panel

1. Visit: http://localhost:8000/admin
2. Login with superuser credentials
3. Manage students and attendance records

## Current Status

✅ **Completed:**

- Python virtual environment
- Django project structure
- Database models (Student, AttendanceSession, AttendanceRecord)
- REST API endpoints
- Database migrations
- FastAPI skeleton
- Project documentation

🔄 **Next Steps:**

1. Implement face recognition logic in AI service
2. Build React frontend components
3. Integrate webcam functionality
4. Connect frontend with backend APIs

## Project Structure

```
vision/
├── backend/                    # Django REST API
│   ├── attendance_system/      # Main project settings
│   ├── students/               # Student app
│   ├── attendance/             # Attendance app
│   └── db.sqlite3             # Database
├── ai_service/                 # FastAPI face recognition
│   ├── main.py                # API endpoints
│   └── face_recognition.py    # Face detection logic
├── frontend/                   # React app (to be built)
├── venv/                       # Python virtual environment
└── requirements.txt           # Python dependencies
```

## Troubleshooting

**Port already in use:**

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Virtual environment issues:**

```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate
```

**Database issues:**

```bash
cd backend
python manage.py migrate
```
