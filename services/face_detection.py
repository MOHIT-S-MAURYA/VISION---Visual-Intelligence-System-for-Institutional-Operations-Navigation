import cv2
import numpy as np
from ultralytics import YOLO
import face_recognition
from typing import List, Tuple, Optional
from config.settings import settings

class FaceDetector:
    def __init__(self):
        """Initialize face detection models"""
        self.yolo_model = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def _load_yolo_model(self):
        """Load YOLO model for face detection"""
        try:
            self.yolo_model = YOLO('yolov8n-face.pt')  # You'll need to download this
        except Exception as e:
            print(f"YOLO face model not available: {e}")
            self.yolo_model = None
    
    def detect_faces_opencv(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using OpenCV Haar Cascades
        Returns list of (x, y, width, height) tuples
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return [(x, y, w, h) for (x, y, w, h) in faces]
    
    def detect_faces_face_recognition(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using face_recognition library
        Returns list of (top, right, bottom, left) converted to (x, y, width, height)
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect face locations
        face_locations = face_recognition.face_locations(rgb_image)
        
        # Convert (top, right, bottom, left) to (x, y, width, height)
        faces = []
        for (top, right, bottom, left) in face_locations:
            x, y = left, top
            w, h = right - left, bottom - top
            faces.append((x, y, w, h))
        
        return faces
    
    def detect_faces_yolo(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using YOLO model
        Returns list of (x, y, width, height) tuples
        """
        if self.yolo_model is None:
            self._load_yolo_model()
        
        if self.yolo_model is None:
            return []
        
        try:
            results = self.yolo_model(image)
            faces = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        confidence = box.conf[0]
                        if confidence >= settings.face_detection_confidence:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            x, y = int(x1), int(y1)
                            w, h = int(x2 - x1), int(y2 - y1)
                            faces.append((x, y, w, h))
            
            return faces
        except Exception as e:
            print(f"YOLO face detection error: {e}")
            return []
    
    def detect_faces(self, image: np.ndarray, method: str = "face_recognition") -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using specified method
        
        Args:
            image: Input image as numpy array
            method: Detection method ('opencv', 'face_recognition', 'yolo')
        
        Returns:
            List of face bounding boxes as (x, y, width, height) tuples
        """
        if method == "opencv":
            return self.detect_faces_opencv(image)
        elif method == "face_recognition":
            return self.detect_faces_face_recognition(image)
        elif method == "yolo":
            return self.detect_faces_yolo(image)
        else:
            # Default to face_recognition
            return self.detect_faces_face_recognition(image)
    
    def extract_face_roi(self, image: np.ndarray, face_box: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract face region of interest from image
        
        Args:
            image: Input image
            face_box: Face bounding box (x, y, width, height)
        
        Returns:
            Cropped face image
        """
        x, y, w, h = face_box
        return image[y:y+h, x:x+w]
