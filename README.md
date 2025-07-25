# VISION - Visual Intelligence System for Institutional Operations & Navigation

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/yourusername/vision)

## 🔍 Overview

**VISION** is an advanced AI-powered classroom attendance system that leverages computer vision and facial recognition technology to automate attendance tracking in educational institutions. The system provides intelligent operations and navigation capabilities for seamless institutional management.

### 📖 What does VISION stand for?

- **V**isual - Computer vision-based processing
- **I**ntelligence - AI-powered recognition algorithms  
- **S**ystem - Comprehensive attendance platform
- **I**nstitutional - Designed for educational institutions
- **O**perations - Streamlined attendance operations
- **N**avigation - Easy system navigation and management

## ✨ Key Features

### 🤖 AI-Powered Recognition
- **Advanced Face Detection**: Multiple detection algorithms (OpenCV, YOLOv8, MediaPipe)
- **High-Accuracy Recognition**: ≥95% accuracy with FAISS-optimized embeddings
- **Real-Time Processing**: < 5 second response time for attendance marking
- **Multi-Face Detection**: Process up to 100 students per classroom image

### 💻 Web Interface
- **Intuitive Dashboard**: Real-time statistics and system overview
- **Student Registration**: Easy registration with multiple face image upload
- **Attendance Management**: One-click attendance marking from classroom photos
- **Comprehensive Reports**: Detailed analytics and attendance insights

### 🔧 Technical Excellence
- **RESTful API**: Complete API for system integration
- **Database Support**: SQLAlchemy with SQLite/PostgreSQL
- **Docker Ready**: Containerized deployment with Docker Compose
- **Scalable Architecture**: Handles multiple classes and institutions

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/vision.git
cd vision

# Start VISION with Docker
docker-compose up --build
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
alembic upgrade head

# Start VISION
python run_dev.py
```

## 🌐 Access VISION

Once running, access VISION through:

- **🏠 Dashboard**: http://localhost:8000/
- **👤 Student Registration**: http://localhost:8000/register-student
- **📷 Mark Attendance**: http://localhost:8000/mark-attendance
- **📊 Reports**: http://localhost:8000/attendance-reports
- **📖 API Documentation**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:8000/health

## 📱 How VISION Works

### 1. Student Registration
```bash
# Register students with face images
POST /api/students/
POST /api/students/{id}/register-faces
```

### 2. Attendance Marking
```bash
# Upload classroom photo for automatic attendance
POST /api/attendance/mark
```

### 3. Data Retrieval
```bash
# Get attendance data and analytics
GET /api/attendance/{date}
GET /api/students/{id}/attendance
```

## 🏗️ System Architecture

```
VISION/
├── app/                    # FastAPI application
│   ├── main.py            # Application entry point
│   └── database.py        # Database configuration
├── models/                 # Database models
│   ├── student.py         # Student model
│   └── attendance.py      # Attendance models
├── services/              # Core AI services
│   ├── face_detection.py  # Face detection algorithms
│   ├── face_recognition.py # Face recognition & FAISS
│   └── attendance_service.py # Business logic
├── api/                   # REST API endpoints
│   ├── students.py        # Student management
│   └── attendance.py      # Attendance operations
├── templates/             # Web interface templates
├── static/               # CSS, JS, assets
└── config/               # Configuration settings
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./vision.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# AI Configuration
FACE_DETECTION_CONFIDENCE=0.6
FACE_RECOGNITION_TOLERANCE=0.6
MAX_FACES_PER_IMAGE=100

# File Storage
UPLOAD_DIR=./uploads
STUDENT_IMAGES_DIR=./uploads/students
CLASS_IMAGES_DIR=./uploads/classes

# FAISS Index
FAISS_INDEX_PATH=./vision_embeddings.index
STUDENT_IDS_PATH=./vision_student_ids.pkl
```

## 📊 Performance Specifications

| Metric | Specification |
|--------|---------------|
| Response Time | < 5 seconds |
| Recognition Accuracy | ≥ 95% |
| Max Students/Class | 100 students |
| Image Resolution | Minimum 720p |
| Supported Formats | JPG, PNG, WEBP |
| Database | SQLite/PostgreSQL |

## 🛠️ Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black . --line-length 88

# Lint code
flake8 . --max-line-length 88
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 📈 API Endpoints

### Student Management
- `POST /api/students/` - Create student
- `GET /api/students/` - List students
- `GET /api/students/{id}` - Get student details
- `PUT /api/students/{id}` - Update student
- `POST /api/students/{id}/register-faces` - Register face images

### Attendance Operations
- `POST /api/attendance/mark` - Mark attendance from image
- `GET /api/attendance/{date}` - Get attendance by date
- `PUT /api/attendance/override` - Override attendance status
- `GET /api/attendance/analytics/summary` - Get analytics

### System Information
- `GET /health` - System health check
- `GET /api/stats` - System statistics

## 🔒 Security Features

- **JWT Authentication**: Secure API access
- **Input Validation**: Comprehensive data validation
- **File Validation**: Secure image upload handling
- **Rate Limiting**: API rate limiting protection
- **Error Handling**: Secure error responses

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:

- 📧 **Email**: support@vision-system.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/vision/issues)
- 📖 **Documentation**: [API Docs](http://localhost:8000/docs)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/vision/discussions)

## 🏆 Acknowledgments

- **OpenCV** - Computer vision library
- **face_recognition** - Face recognition algorithms
- **FastAPI** - Modern web framework
- **FAISS** - Efficient similarity search
- **SQLAlchemy** - Database ORM
- **Bootstrap** - UI framework

---

<div align="center">

**🔍 VISION - See Every Student, Count Every Moment**

*Built with ❤️ for Educational Excellence*

[![GitHub stars](https://img.shields.io/github/stars/yourusername/vision?style=social)](https://github.com/yourusername/vision/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/vision?style=social)](https://github.com/yourusername/vision/network)

</div>
