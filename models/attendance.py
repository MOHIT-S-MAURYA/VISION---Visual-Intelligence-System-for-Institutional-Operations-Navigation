from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    status = Column(String(10), nullable=False, default="Present")  # Present, Absent
    
    # Metadata
    marked_at = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(String(10), nullable=True)  # Face recognition confidence
    
    # Relationship with student
    student = relationship("Student", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<Attendance(student_id={self.student_id}, date='{self.date}', status='{self.status}')>"

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    class_name = Column(String(50), nullable=True)
    teacher_name = Column(String(100), nullable=True)
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_detected = Column(Integer, default=0)
    total_recognized = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<AttendanceSession(id={self.id}, date='{self.date}', class='{self.class_name}')>"
