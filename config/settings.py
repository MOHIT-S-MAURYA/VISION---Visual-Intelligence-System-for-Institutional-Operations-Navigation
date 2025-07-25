from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./vision.db"
    
    # Security
    secret_key: str = "vision-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    app_name: str = "VISION - Visual Intelligence System for Institutional Operations & Navigation"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Face Recognition
    face_detection_confidence: float = 0.6
    face_recognition_tolerance: float = 0.6
    max_faces_per_image: int = 100
    
    # File Storage
    upload_dir: str = "./uploads"
    student_images_dir: str = "./uploads/students"
    class_images_dir: str = "./uploads/classes"
    
    # FAISS Index
    faiss_index_path: str = "./vision_embeddings.index"
    student_ids_path: str = "./vision_student_ids.pkl"
    
    class Config:
        env_file = ".env"

settings = Settings()
