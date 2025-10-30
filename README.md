# 👨‍🎓 Face Recognition Attendance System

**High-performance attendance tracking system using AI-powered face recognition**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal.svg)](https://fastapi.tiangolo.com/)
[![Accuracy](https://img.shields.io/badge/Accuracy-98.57%25-brightgreen.svg)](#performance-metrics)

---

## 🌟 Highlights

✨ **98.57% accuracy** on LFW benchmark (tested on 140 real faces)  
⚡ **35ms detection time** (6.9x faster than previous version)  
🚀 **28 faces per second** real-time processing  
🎯 **99.83% recognition accuracy** with ArcFace  
🔒 **Production-ready** with quality gating and security

---

## 🏗️ Project Structure

```
vision/
├── backend/           # Django REST Framework - Main API
├── ai_service/        # FastAPI - Face Recognition Service
├── frontend/          # React + TailwindCSS - User Interface
├── docs/              # Documentation
├── start.sh           # Start all services at once
└── requirements.txt   # Python dependencies
```

---

## �� Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+
- Webcam/Camera

### One-Command Start (Recommended)

```bash
# Clone and navigate
git clone <repository-url>
cd vision

# Setup environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Run migrations and create admin
cd backend
python manage.py migrate
python manage.py createsuperuser
cd ..

# Start all services at once
./start.sh
```

**That's it!** The script automatically starts:
- 🌐 Frontend: http://localhost:3000
- 🔗 Backend API: http://localhost:8000
- 🤖 AI Service: http://localhost:8001
- 📚 API Docs: http://localhost:8001/docs

Press **Ctrl+C** to stop all services gracefully.

### Manual Start (Alternative)

If you prefer starting services individually:

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
cd backend
python manage.py runserver
```

**Terminal 2 - AI Service:**
```bash
source venv/bin/activate
cd ai_service
uvicorn main:app --port 8001 --reload
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## 📋 System Features

### 🎯 Face Recognition
- **SCRFD Detection** - Ultra-fast face detection (35ms)
- **ArcFace Recognition** - Industry-leading accuracy (99.83%)
- **FAISS Vector Search** - Lightning-fast similarity search
- **Quality Gating** - Automatic rejection of poor-quality images

### 👥 User Management
- **Role-Based Access** - Admin, Teacher, Student roles
- **Department Organization** - Multi-department support
- **JWT Authentication** - Secure token-based auth
- **Auto Roll Numbers** - Automatic roll number generation

### 📊 Attendance Management
- **Real-time Detection** - Live webcam face recognition
- **Session Management** - Create and manage attendance sessions
- **Subject Tracking** - Track attendance by subject
- **Statistics & Reports** - Comprehensive attendance analytics

### 🎨 Modern UI
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Real-time Updates** - Live attendance status
- **Interactive Dashboard** - Role-specific dashboards
- **Dark Mode** - Easy on the eyes

---

## 📚 Documentation

Comprehensive documentation available in the `docs/` folder:

- **[Project Report](docs/PROJECT_REPORT.md)** - Complete 50+ page project report
- **[Technical Specification](docs/TECHNICAL_SPECIFICATION.md)** - Detailed technical specs and API docs
- **[Development Timeline](docs/DEVELOPMENT_TIMELINE.md)** - Complete development history
- **[API Documentation](http://localhost:8001/docs)** - Interactive API docs (when running)

---

## 🎯 Performance Metrics

| Metric | Value | Details |
|--------|-------|---------|
| Face Detection Accuracy | **98.57%** | Tested on 140 LFW faces |
| Detection Speed | **35ms** | Per face detection |
| Recognition Accuracy | **99.83%** | Same person matching |
| Throughput | **~28 faces/sec** | Real-time processing |
| Model Size | 2.5MB | SCRFD buffalo_sc |
| Embedding Size | 512 dimensions | ArcFace features |

---

## 🛠️ Technology Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API development
- **SQLite/PostgreSQL** - Database
- **JWT** - Authentication

### AI/ML
- **FastAPI** - High-performance API
- **InsightFace** - Face recognition models
- **SCRFD** - Face detection (buffalo_sc)
- **ArcFace** - Face recognition (w600k_r50)
- **FAISS** - Vector similarity search
- **ONNX Runtime** - Model inference

### Frontend
- **React 18** - UI library
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **React Router** - Routing
- **Vite** - Build tool

---

## 📱 Usage Workflow

### For Teachers:
1. **Login** to the system
2. **Create Session** - Select department, subject, date/time
3. **Mark Attendance** - Capture group photo or individual photos
4. **View Reports** - Check attendance statistics

### For Students:
1. **Register** with photo upload
2. **View Profile** - Check roll number and details
3. **View Attendance** - See attendance history and statistics

### For Admins:
1. **Manage Users** - Create/edit teachers and students
2. **Manage Departments** - Add/edit departments
3. **System Analytics** - View overall system statistics
4. **Data Export** - Export attendance reports

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:8001 | xargs kill -9  # AI Service
lsof -ti:3000 | xargs kill -9  # Frontend
```

### Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Issues
```bash
# Reset database
cd backend
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Face Detection Not Working
- Ensure camera permissions are granted
- Check if AI service is running on port 8001
- Verify FAISS index is initialized
- Check lighting conditions (good lighting required)

---

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test

# AI Service tests
cd ai_service
pytest tests/ -v
```

---

## 🚀 Production Deployment

See comprehensive guides in:
- **[Deployment Guide](docs/PROJECT_REPORT.md#deployment-guide)**
- **[Security Guide](docs/TECHNICAL_SPECIFICATION.md#security-specifications)**

**Quick Production Checklist:**
- [ ] Set `DEBUG=False` in Django settings
- [ ] Configure PostgreSQL database
- [ ] Set strong `SECRET_KEY`
- [ ] Configure CORS properly
- [ ] Setup SSL/HTTPS
- [ ] Use Gunicorn/Uvicorn with workers
- [ ] Setup Nginx reverse proxy
- [ ] Configure static file serving

---

## 📊 Project Statistics

- **Total Files:** 152
- **Lines of Code:** 19,952
- **Test Coverage:** 82%
- **Development Time:** 16 weeks

---

## 🙏 Acknowledgments

- **InsightFace** - For excellent face recognition models
- **FAISS** - For fast similarity search
- **Django & React** - For robust frameworks
- **Open Source Community** - For incredible tools and libraries

---

**Made with ❤️ using Django, React, and FastAPI**

**⭐ Star this repository if you find it helpful!**
