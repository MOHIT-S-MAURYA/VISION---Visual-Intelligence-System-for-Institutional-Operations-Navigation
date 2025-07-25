from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from models.student import Student
from services.attendance_service import AttendanceService
from pydantic import BaseModel
import shutil
import os
from config.settings import settings
from datetime import datetime

router = APIRouter(prefix="/students", tags=["students"])

# Pydantic models for request/response
class StudentCreate(BaseModel):
    name: str
    roll_number: str
    email: Optional[str] = None
    phone: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    roll_number: str
    email: Optional[str]
    phone: Optional[str]
    registration_date: datetime
    is_active: str
    
    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[str] = None

# Initialize services
attendance_service = AttendanceService()

@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student"""
    try:
        # Check if roll number already exists
        existing = db.query(Student).filter(Student.roll_number == student.roll_number).first()
        if existing:
            raise HTTPException(status_code=400, detail="Student with this roll number already exists")
        
        # Create new student
        db_student = Student(**student.dict())
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        
        return db_student
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating student: {str(e)}")

@router.get("/", response_model=List[StudentResponse])
async def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all students with pagination"""
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get a specific student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    """Update student information"""
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Update only provided fields
        update_data = student_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)
        
        db.commit()
        db.refresh(student)
        
        return student
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating student: {str(e)}")

@router.delete("/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student"""
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Remove from face recognition index
        # attendance_service.face_recognizer.remove_student_embedding(student_id)
        
        db.delete(student)
        db.commit()
        
        return {"message": "Student deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting student: {str(e)}")

@router.post("/{student_id}/register-faces")
async def register_student_faces(
    student_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Register face images for a student"""
    try:
        # Verify student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Create student directory
        student_dir = os.path.join(settings.student_images_dir, str(student_id))
        os.makedirs(student_dir, exist_ok=True)
        
        # Save uploaded files
        saved_files = []
        for file in files:
            if not file.content_type.startswith('image/'):
                continue
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(student_dir, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            saved_files.append(file_path)
        
        if not saved_files:
            raise HTTPException(status_code=400, detail="No valid image files provided")
        
        # Register faces with attendance service
        result = attendance_service.register_student_faces(student_id, saved_files, db)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering faces: {str(e)}")

@router.get("/{student_id}/attendance")
async def get_student_attendance(
    student_id: int,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """Get attendance history for a student"""
    try:
        # Verify student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get attendance history
        attendance_history = attendance_service.get_student_attendance_history(student_id, db, limit)
        
        return {
            "student_id": student_id,
            "student_name": student.name,
            "roll_number": student.roll_number,
            "attendance_history": attendance_history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting attendance: {str(e)}")

@router.get("/roll/{roll_number}", response_model=StudentResponse)
async def get_student_by_roll_number(roll_number: str, db: Session = Depends(get_db)):
    """Get student by roll number"""
    student = db.query(Student).filter(Student.roll_number == roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
