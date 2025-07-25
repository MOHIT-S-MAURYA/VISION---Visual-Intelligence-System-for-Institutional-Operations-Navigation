import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "AI-Based Classroom Attendance System" in data["message"]

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_create_student():
    """Test student creation"""
    student_data = {
        "name": "John Doe",
        "roll_number": "CS001",
        "email": "john@example.com",
        "phone": "1234567890"
    }
    response = client.post("/api/students/", json=student_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["roll_number"] == "CS001"

def test_get_students():
    """Test getting students list"""
    response = client.get("/api/students/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_system_stats():
    """Test system statistics endpoint"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert "system_status" in data
