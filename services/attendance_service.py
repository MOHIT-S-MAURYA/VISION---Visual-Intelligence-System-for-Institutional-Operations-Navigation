import cv2
import numpy as np
from typing import List, Dict, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from models.student import Student
from models.attendance import Attendance, AttendanceSession
from services.face_detection import FaceDetector
from services.face_recognition import FaceRecognitionService
import os
from config.settings import settings

class AttendanceService:
    def __init__(self):
        """Initialize attendance service"""
        self.face_detector = FaceDetector()
        self.face_recognizer = FaceRecognitionService()
        
        # Ensure upload directories exist
        os.makedirs(settings.upload_dir, exist_ok=True)
        os.makedirs(settings.student_images_dir, exist_ok=True)
        os.makedirs(settings.class_images_dir, exist_ok=True)
    
    def register_student_faces(self, student_id: int, image_files: List[str], db: Session) -> Dict:
        """
        Register multiple face images for a student
        
        Args:
            student_id: Student database ID
            image_files: List of image file paths
            db: Database session
        
        Returns:
            Registration result dictionary
        """
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return {"success": False, "message": "Student not found"}
            
            embeddings = []
            processed_images = 0
            
            for image_path in image_files:
                if not os.path.exists(image_path):
                    continue
                
                # Load and process image
                image = cv2.imread(image_path)
                if image is None:
                    continue
                
                # Detect faces in the image
                faces = self.face_detector.detect_faces(image)
                
                if len(faces) == 0:
                    continue
                
                # Use the largest face (assume it's the main subject)
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                
                # Compute embedding
                embedding = self.face_recognizer.compute_face_embedding(image, largest_face)
                
                if embedding is not None:
                    embeddings.append(embedding)
                    processed_images += 1
            
            if not embeddings:
                return {"success": False, "message": "No valid face embeddings found in uploaded images"}
            
            # Average the embeddings if multiple images
            if len(embeddings) > 1:
                avg_embedding = np.mean(embeddings, axis=0)
            else:
                avg_embedding = embeddings[0]
            
            # Add to FAISS index
            self.face_recognizer.add_student_embedding(student_id, avg_embedding)
            
            # Store embedding in database (optional - for backup)
            student.face_embedding = avg_embedding.tobytes()
            db.commit()
            
            return {
                "success": True,
                "message": f"Successfully registered {processed_images} face images for {student.name}",
                "processed_images": processed_images
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error registering student faces: {str(e)}"}
    
    def mark_attendance_from_image(self, image_path: str, class_name: Optional[str], teacher_name: Optional[str], db: Session) -> Dict:
        """
        Mark attendance for all students detected in a classroom image
        
        Args:
            image_path: Path to classroom image
            class_name: Optional class identifier
            teacher_name: Optional teacher name
            db: Database session
        
        Returns:
            Attendance marking results
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"success": False, "message": "Could not load image"}
            
            # Detect faces
            faces = self.face_detector.detect_faces(image)
            
            if len(faces) == 0:
                return {"success": False, "message": "No faces detected in the image"}
            
            # Recognize faces
            recognition_results = self.face_recognizer.recognize_faces_in_image(image, faces)
            
            # Create attendance session
            today = date.today()
            session = AttendanceSession(
                date=today,
                class_name=class_name,
                teacher_name=teacher_name,
                image_path=image_path,
                total_detected=len(faces),
                total_recognized=sum(1 for r in recognition_results if r['recognized'])
            )
            db.add(session)
            db.flush()  # Get session ID
            
            # Mark attendance for recognized students
            attendance_marked = []
            already_marked = []
            
            for result in recognition_results:
                if result['recognized']:
                    student_id = result['student_id']
                    
                    # Check if already marked today
                    existing = db.query(Attendance).filter(
                        Attendance.student_id == student_id,
                        Attendance.date == today
                    ).first()
                    
                    if existing:
                        already_marked.append(student_id)
                        continue
                    
                    # Mark attendance
                    attendance = Attendance(
                        student_id=student_id,
                        date=today,
                        status="Present",
                        confidence_score=f"{result['confidence']:.2f}"
                    )
                    db.add(attendance)
                    attendance_marked.append(student_id)
            
            db.commit()
            
            # Get student details for response
            marked_students = []
            if attendance_marked:
                students = db.query(Student).filter(Student.id.in_(attendance_marked)).all()
                marked_students = [{"id": s.id, "name": s.name, "roll_number": s.roll_number} for s in students]
            
            already_marked_students = []
            if already_marked:
                students = db.query(Student).filter(Student.id.in_(already_marked)).all()
                already_marked_students = [{"id": s.id, "name": s.name, "roll_number": s.roll_number} for s in students]
            
            return {
                "success": True,
                "message": "Attendance marking completed",
                "session_id": session.id,
                "total_faces_detected": len(faces),
                "total_faces_recognized": len([r for r in recognition_results if r['recognized']]),
                "attendance_marked": len(attendance_marked),
                "already_marked": len(already_marked),
                "marked_students": marked_students,
                "already_marked_students": already_marked_students,
                "unrecognized_faces": len(faces) - len([r for r in recognition_results if r['recognized']])
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error marking attendance: {str(e)}"}
    
    def get_attendance_by_date(self, target_date: date, db: Session) -> List[Dict]:
        """
        Get attendance records for a specific date
        
        Args:
            target_date: Date to get attendance for
            db: Database session
        
        Returns:
            List of attendance records with student details
        """
        try:
            # Get all attendance records for the date
            attendance_records = db.query(Attendance).filter(Attendance.date == target_date).all()
            
            result = []
            for record in attendance_records:
                student = record.student
                result.append({
                    "attendance_id": record.id,
                    "student_id": student.id,
                    "student_name": student.name,
                    "roll_number": student.roll_number,
                    "status": record.status,
                    "marked_at": record.marked_at.isoformat() if record.marked_at else None,
                    "confidence_score": record.confidence_score
                })
            
            return result
            
        except Exception as e:
            print(f"Error getting attendance by date: {e}")
            return []
    
    def get_student_attendance_history(self, student_id: int, db: Session, limit: int = 30) -> List[Dict]:
        """
        Get attendance history for a specific student
        
        Args:
            student_id: Student database ID
            db: Database session
            limit: Maximum number of records to return
        
        Returns:
            List of attendance records
        """
        try:
            records = db.query(Attendance).filter(
                Attendance.student_id == student_id
            ).order_by(Attendance.date.desc()).limit(limit).all()
            
            result = []
            for record in records:
                result.append({
                    "date": record.date.isoformat(),
                    "status": record.status,
                    "marked_at": record.marked_at.isoformat() if record.marked_at else None,
                    "confidence_score": record.confidence_score
                })
            
            return result
            
        except Exception as e:
            print(f"Error getting student attendance history: {e}")
            return []
    
    def override_attendance(self, student_id: int, target_date: date, new_status: str, db: Session) -> Dict:
        """
        Override attendance status for a student on a specific date
        
        Args:
            student_id: Student database ID
            target_date: Date to override
            new_status: New status (Present/Absent)
            db: Database session
        
        Returns:
            Override result
        """
        try:
            # Check if attendance record exists
            record = db.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.date == target_date
            ).first()
            
            if record:
                # Update existing record
                record.status = new_status
                record.marked_at = datetime.utcnow()
                message = f"Updated attendance status to {new_status}"
            else:
                # Create new record
                record = Attendance(
                    student_id=student_id,
                    date=target_date,
                    status=new_status,
                    confidence_score="Manual"
                )
                db.add(record)
                message = f"Created new attendance record with status {new_status}"
            
            db.commit()
            
            return {"success": True, "message": message}
            
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error overriding attendance: {str(e)}"}
