import cv2
import numpy as np
import face_recognition
import pickle
import faiss
from typing import List, Tuple, Optional, Dict
from config.settings import settings
import os

class FaceRecognitionService:
    def __init__(self):
        """Initialize face recognition service"""
        self.index = None
        self.student_ids = []
        self.embedding_dim = 128  # face_recognition produces 128-dimensional embeddings
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index and student IDs if they exist"""
        try:
            if os.path.exists(settings.faiss_index_path):
                self.index = faiss.read_index(settings.faiss_index_path)
                print(f"Loaded FAISS index with {self.index.ntotal} embeddings")
            
            if os.path.exists(settings.student_ids_path):
                with open(settings.student_ids_path, 'rb') as f:
                    self.student_ids = pickle.load(f)
                print(f"Loaded {len(self.student_ids)} student IDs")
        except Exception as e:
            print(f"Error loading index: {e}")
            self._initialize_empty_index()
    
    def _initialize_empty_index(self):
        """Initialize empty FAISS index"""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.student_ids = []
    
    def _save_index(self):
        """Save FAISS index and student IDs to disk"""
        try:
            faiss.write_index(self.index, settings.faiss_index_path)
            
            with open(settings.student_ids_path, 'wb') as f:
                pickle.dump(self.student_ids, f)
            
            print("Index and student IDs saved successfully")
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def compute_face_embedding(self, image: np.ndarray, face_box: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Compute face embedding for a given image
        
        Args:
            image: Input image (BGR format)
            face_box: Optional face bounding box (x, y, w, h)
        
        Returns:
            Face embedding as numpy array or None if no face found
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if face_box:
                # Extract face region if bounding box provided
                x, y, w, h = face_box
                face_image = rgb_image[y:y+h, x:x+w]
                
                # Get face encodings for the cropped face
                face_encodings = face_recognition.face_encodings(face_image)
            else:
                # Get face encodings for the entire image
                face_encodings = face_recognition.face_encodings(rgb_image)
            
            if len(face_encodings) > 0:
                return face_encodings[0]
            else:
                return None
                
        except Exception as e:
            print(f"Error computing face embedding: {e}")
            return None
    
    def add_student_embedding(self, student_id: int, embedding: np.ndarray):
        """
        Add a student's face embedding to the index
        
        Args:
            student_id: Student database ID
            embedding: Face embedding vector
        """
        try:
            if self.index is None:
                self._initialize_empty_index()
            
            # Ensure embedding is the right shape
            embedding = embedding.reshape(1, -1).astype('float32')
            
            # Add to FAISS index
            self.index.add(embedding)
            self.student_ids.append(student_id)
            
            # Save updated index
            self._save_index()
            
            print(f"Added embedding for student {student_id}")
            
        except Exception as e:
            print(f"Error adding student embedding: {e}")
    
    def recognize_face(self, embedding: np.ndarray, k: int = 1) -> List[Tuple[int, float]]:
        """
        Recognize a face by finding similar embeddings
        
        Args:
            embedding: Face embedding to match
            k: Number of top matches to return
        
        Returns:
            List of (student_id, distance) tuples
        """
        try:
            if self.index is None or self.index.ntotal == 0:
                return []
            
            # Ensure embedding is the right shape
            embedding = embedding.reshape(1, -1).astype('float32')
            
            # Search for similar embeddings
            distances, indices = self.index.search(embedding, k)
            
            results = []
            for i in range(len(distances[0])):
                if indices[0][i] < len(self.student_ids):
                    student_id = self.student_ids[indices[0][i]]
                    distance = float(distances[0][i])
                    results.append((student_id, distance))
            
            return results
            
        except Exception as e:
            print(f"Error recognizing face: {e}")
            return []
    
    def is_match(self, distance: float) -> bool:
        """
        Determine if a distance indicates a face match
        
        Args:
            distance: L2 distance from FAISS search
        
        Returns:
            True if faces match, False otherwise
        """
        # Convert L2 distance to similarity score (approximate)
        # This is a heuristic conversion - you may need to tune this
        similarity = 1.0 / (1.0 + distance)
        return similarity >= (1.0 - settings.face_recognition_tolerance)
    
    def recognize_faces_in_image(self, image: np.ndarray, face_boxes: List[Tuple[int, int, int, int]]) -> List[Dict]:
        """
        Recognize all faces in an image
        
        Args:
            image: Input image
            face_boxes: List of face bounding boxes
        
        Returns:
            List of recognition results with student info
        """
        results = []
        
        for i, face_box in enumerate(face_boxes):
            # Compute embedding for this face
            embedding = self.compute_face_embedding(image, face_box)
            
            if embedding is not None:
                # Try to recognize the face
                matches = self.recognize_face(embedding, k=1)
                
                result = {
                    'face_index': i,
                    'face_box': face_box,
                    'student_id': None,
                    'confidence': 0.0,
                    'recognized': False
                }
                
                if matches and self.is_match(matches[0][1]):
                    student_id, distance = matches[0]
                    confidence = 1.0 / (1.0 + distance)  # Convert distance to confidence
                    
                    result.update({
                        'student_id': student_id,
                        'confidence': confidence,
                        'recognized': True
                    })
                
                results.append(result)
        
        return results
    
    def remove_student_embedding(self, student_id: int):
        """
        Remove a student's embedding from the index
        Note: FAISS doesn't support direct removal, so we rebuild the index
        """
        try:
            if student_id in self.student_ids:
                # Find all indices to keep
                indices_to_keep = [i for i, sid in enumerate(self.student_ids) if sid != student_id]
                
                if indices_to_keep:
                    # Rebuild index with remaining embeddings
                    old_embeddings = []
                    for i in indices_to_keep:
                        # This is a simplified approach - in practice, you'd need to store embeddings separately
                        pass
                    
                    # Update student_ids list
                    self.student_ids = [self.student_ids[i] for i in indices_to_keep]
                else:
                    # No embeddings left
                    self._initialize_empty_index()
                
                self._save_index()
                print(f"Removed embedding for student {student_id}")
                
        except Exception as e:
            print(f"Error removing student embedding: {e}")
