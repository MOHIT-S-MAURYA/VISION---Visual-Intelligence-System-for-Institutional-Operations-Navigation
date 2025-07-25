from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    roll_number = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(15), nullable=True)
    
    # Face embedding stored as binary data
    face_embedding = Column(LargeBinary, nullable=True)
    
    # Registration metadata
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(String(10), default="Active")
    
    # Relationship with attendance
    attendance_records = relationship("Attendance", back_populates="student")
    
    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', roll_number='{self.roll_number}')>"
