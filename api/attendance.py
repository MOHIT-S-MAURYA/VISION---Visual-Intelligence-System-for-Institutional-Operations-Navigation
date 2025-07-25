from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from services.attendance_service import AttendanceService
from models.attendance import Attendance
from models.student import Student
from pydantic import BaseModel
from datetime import date, datetime
import shutil
import os
from config.settings import settings

router = APIRouter(prefix="/attendance", tags=["attendance"])

# Pydantic models
class AttendanceOverride(BaseModel):
    student_id: int
    date: date
    status: str  # Present or Absent

class AttendanceResponse(BaseModel):
    attendance_id: int
    student_id: int
    student_name: str
    roll_number: str
    status: str
    marked_at: Optional[datetime]
    confidence_score: Optional[str]

# Initialize service
attendance_service = AttendanceService()

@router.post("/mark")
async def mark_attendance(
    file: UploadFile = File(...),
    class_name: Optional[str] = Form(None),
    teacher_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Mark attendance from classroom image"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"class_{timestamp}_{file.filename}"
        file_path = os.path.join(settings.class_images_dir, filename)
        
        # Save uploaded file
        os.makedirs(settings.class_images_dir, exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process attendance
        result = attendance_service.mark_attendance_from_image(
            image_path=file_path,
            class_name=class_name,
            teacher_name=teacher_name,
            db=db
        )
        
        if not result["success"]:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking attendance: {str(e)}")

@router.get("/{target_date}")
async def get_attendance_by_date(target_date: date, db: Session = Depends(get_db)):
    """Get attendance records for a specific date"""
    try:
        attendance_records = attendance_service.get_attendance_by_date(target_date, db)
        
        # Get total registered students for statistics
        total_students = db.query(Student).filter(Student.is_active == "Active").count()
        present_count = len([r for r in attendance_records if r["status"] == "Present"])
        absent_count = total_students - present_count
        
        return {
            "date": target_date.isoformat(),
            "total_students": total_students,
            "present_count": present_count,
            "absent_count": absent_count,
            "attendance_percentage": round((present_count / total_students) * 100, 2) if total_students > 0 else 0,
            "records": attendance_records
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting attendance: {str(e)}")

@router.get("/")
async def get_attendance_range(
    start_date: date,
    end_date: date,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get attendance records for a date range, optionally filtered by student"""
    try:
        query = db.query(Attendance).filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        )
        
        if student_id:
            query = query.filter(Attendance.student_id == student_id)
        
        records = query.all()
        
        result = []
        for record in records:
            student = record.student
            result.append({
                "attendance_id": record.id,
                "student_id": student.id,
                "student_name": student.name,
                "roll_number": student.roll_number,
                "date": record.date.isoformat(),
                "status": record.status,
                "marked_at": record.marked_at.isoformat() if record.marked_at else None,
                "confidence_score": record.confidence_score
            })
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_records": len(result),
            "records": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting attendance range: {str(e)}")

@router.put("/override")
async def override_attendance(
    override_data: AttendanceOverride,
    db: Session = Depends(get_db)
):
    """Override attendance status for a student on a specific date"""
    try:
        # Validate student exists
        student = db.query(Student).filter(Student.id == override_data.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Validate status
        if override_data.status not in ["Present", "Absent"]:
            raise HTTPException(status_code=400, detail="Status must be 'Present' or 'Absent'")
        
        # Override attendance
        result = attendance_service.override_attendance(
            student_id=override_data.student_id,
            target_date=override_data.date,
            new_status=override_data.status,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error overriding attendance: {str(e)}")

@router.get("/sessions/{session_date}")
async def get_attendance_sessions(session_date: date, db: Session = Depends(get_db)):
    """Get all attendance sessions for a specific date"""
    try:
        from models.attendance import AttendanceSession
        
        sessions = db.query(AttendanceSession).filter(
            AttendanceSession.date == session_date
        ).all()
        
        result = []
        for session in sessions:
            result.append({
                "session_id": session.id,
                "date": session.date.isoformat(),
                "class_name": session.class_name,
                "teacher_name": session.teacher_name,
                "created_at": session.created_at.isoformat(),
                "total_detected": session.total_detected,
                "total_recognized": session.total_recognized,
                "recognition_rate": round((session.total_recognized / session.total_detected) * 100, 2) if session.total_detected > 0 else 0
            })
        
        return {
            "date": session_date.isoformat(),
            "total_sessions": len(result),
            "sessions": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sessions: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_attendance_session(session_id: int, db: Session = Depends(get_db)):
    """Delete an attendance session and associated image"""
    try:
        from models.attendance import AttendanceSession
        
        session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete associated image file
        if session.image_path and os.path.exists(session.image_path):
            os.remove(session.image_path)
        
        # Delete session
        db.delete(session)
        db.commit()
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.get("/analytics/summary")
async def get_attendance_analytics(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Get attendance analytics for a date range"""
    try:
        # Get all attendance records in range
        records = db.query(Attendance).filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
        
        # Calculate statistics
        total_records = len(records)
        present_records = len([r for r in records if r.status == "Present"])
        absent_records = total_records - present_records
        
        # Get unique students and dates
        unique_students = len(set(r.student_id for r in records))
        unique_dates = len(set(r.date for r in records))
        
        # Calculate average attendance
        avg_attendance = (present_records / total_records * 100) if total_records > 0 else 0
        
        # Daily breakdown
        daily_stats = {}
        for record in records:
            date_str = record.date.isoformat()
            if date_str not in daily_stats:
                daily_stats[date_str] = {"present": 0, "absent": 0}
            
            if record.status == "Present":
                daily_stats[date_str]["present"] += 1
            else:
                daily_stats[date_str]["absent"] += 1
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_days": unique_dates
            },
            "summary": {
                "total_records": total_records,
                "present_records": present_records,
                "absent_records": absent_records,
                "unique_students": unique_students,
                "average_attendance_percentage": round(avg_attendance, 2)
            },
            "daily_breakdown": daily_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")
