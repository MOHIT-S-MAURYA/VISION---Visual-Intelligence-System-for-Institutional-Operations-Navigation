from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import engine, get_db
from models.student import Student
from models.attendance import Attendance, AttendanceSession
from api.students import router as students_router
from api.attendance import router as attendance_router
from config.settings import settings
import os
from datetime import date

# Create database tables
from app.database import Base
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="VISION - Visual Intelligence System for Institutional Operations & Navigation",
    version=settings.app_version,
    description="Advanced AI-powered classroom attendance system using computer vision and face recognition technology for institutional operations and navigation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(students_router, prefix="/api")
app.include_router(attendance_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """VISION System Dashboard"""
    # Get some basic statistics
    total_students = db.query(Student).filter(Student.is_active == "Active").count()
    today = date.today()
    today_attendance = db.query(Attendance).filter(Attendance.date == today).count()
    
    # Calculate attendance percentage for today
    attendance_percentage = 0
    if total_students > 0:
        attendance_percentage = round((today_attendance / total_students) * 100, 1)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_students": total_students,
        "today_attendance": today_attendance,
        "attendance_percentage": attendance_percentage,
        "today_date": today.strftime("%B %d, %Y"),
        "system_name": "VISION",
        "system_tagline": "Visual Intelligence System for Institutional Operations & Navigation"
    })

@app.get("/register-student", response_class=HTMLResponse)
async def register_student_page(request: Request):
    """Student registration page"""
    return templates.TemplateResponse("register_student.html", {
        "request": request,
        "system_name": "VISION",
        "system_tagline": "Visual Intelligence System for Institutional Operations & Navigation"
    })

@app.get("/mark-attendance", response_class=HTMLResponse)
async def mark_attendance_page(request: Request):
    """Mark attendance page"""
    return templates.TemplateResponse("mark_attendance.html", {
        "request": request,
        "system_name": "VISION",
        "system_tagline": "Visual Intelligence System for Institutional Operations & Navigation"
    })

@app.get("/view-students", response_class=HTMLResponse)
async def view_students_page(request: Request, db: Session = Depends(get_db)):
    """View all students page"""
    students = db.query(Student).filter(Student.is_active == "Active").all()
    return templates.TemplateResponse("view_students.html", {
        "request": request,
        "students": students,
        "system_name": "VISION",
        "system_tagline": "Visual Intelligence System for Institutional Operations & Navigation"
    })

@app.get("/attendance-reports", response_class=HTMLResponse)
async def attendance_reports_page(request: Request):
    """Attendance reports page"""
    return templates.TemplateResponse("attendance_reports.html", {
        "request": request,
        "system_name": "VISION",
        "system_tagline": "Visual Intelligence System for Institutional Operations & Navigation"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "system": "VISION",
        "full_name": "Visual Intelligence System for Institutional Operations & Navigation",
        "message": "VISION is running optimally",
        "version": settings.app_version
    }

@app.get("/api/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get VISION system statistics"""
    total_students = db.query(Student).count()
    active_students = db.query(Student).filter(Student.is_active == "Active").count()
    total_attendance_records = db.query(Attendance).count()
    
    return {
        "system": "VISION",
        "full_name": "Visual Intelligence System for Institutional Operations & Navigation",
        "total_students": total_students,
        "active_students": active_students,
        "total_attendance_records": total_attendance_records,
        "system_status": "operational",
        "version": settings.app_version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
