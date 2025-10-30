from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import tempfile
from typing import Optional
from .face_recognition import FaceRecognitionSystem
import cv2

app = FastAPI(title="Face Recognition AI Service")

# Initialize face recognition system
face_system = FaceRecognitionSystem()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Face Recognition AI Service Running", "status": "active"}

@app.post("/api/face/register")
async def register_face(
    file: UploadFile = File(...),
    student_id: str = Form(...)
):
    """Register a new student's face"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Register face using face recognition system
            success = face_system.register_face(temp_file_path, student_id)
            
            if success:
                return {
                    "status": "success",
                    "message": "Face registered successfully",
                    "embedding_id": student_id,
                    "student_id": student_id
                }
            else:
                raise HTTPException(status_code=400, detail="Face registration failed")
                
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing face: {str(e)}")

@app.post("/api/face/recognize")
async def recognize_face(file: UploadFile = File(...)):
    """Recognize a face from the uploaded image"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Recognize face
            result = face_system.recognize_face(temp_file_path)
            
            if result:
                return {
                    "status": "success",
                    "recognized": True,
                    "student_id": result["student_id"],
                    "confidence": result["confidence"],
                    "similarity": result.get("similarity")
                }
            else:
                return {
                    "status": "success",
                    "recognized": False,
                    "message": "No matching face found"
                }
                
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recognizing face: {str(e)}")

@app.post("/api/face/register_multi")
async def register_face_multi(
    files: List[UploadFile] = File(...),
    student_id: str = Form(...)
):
    """Register a new student's face from multiple frames with quality validation."""
    temp_paths = []
    try:
        # Validate minimum frames
        if len(files) < 3:
            raise HTTPException(
                status_code=400, 
                detail=f"At least 3 frames required for robust registration. Received: {len(files)}"
            )
        
        if len(files) > 15:
            raise HTTPException(
                status_code=400, 
                detail=f"Maximum 15 frames allowed. Received: {len(files)}"
            )
        
        # Save uploaded frames to temporary files
        for idx, f in enumerate(files):
            content = await f.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail=f"Frame {idx} is empty")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tf:
                tf.write(content)
                temp_paths.append(tf.name)
        
        # Register face with multi-frame aggregation
        success = face_system.register_face_multi(temp_paths, student_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Face registered successfully using {len(temp_paths)} frames",
                "embedding_id": student_id,
                "student_id": student_id,
                "frames": len(temp_paths),
                "method": "multi-frame-aggregation"
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail="Face registration failed. No valid faces detected in provided frames."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "No face detected" in error_msg or "No valid faces" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail="No clear face detected in images. Please ensure face is well-lit and clearly visible."
            )
        raise HTTPException(
            status_code=500, 
            detail=f"Face processing error: {error_msg}"
        )
    finally:
        # Clean up temporary files
        for p in temp_paths:
            if os.path.exists(p):
                try:
                    os.unlink(p)
                except Exception:
                    pass

@app.post("/api/face/recognize_multi")
async def recognize_face_multi(files: List[UploadFile] = File(...)):
    """Recognize a face from multiple frames and aggregate results."""
    temp_paths = []
    try:
        for f in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tf:
                tf.write(await f.read())
                temp_paths.append(tf.name)
        result = face_system.recognize_face_multi(temp_paths)
        if result:
            return {
                "status": "success",
                "recognized": True,
                "student_id": result["student_id"],
                "confidence": result["confidence"],
                "similarity": result.get("similarity"),
                "frames": result.get("frames", len(temp_paths)),
                "votes": result.get("votes", 0),
            }
        else:
            return {
                "status": "success",
                "recognized": False,
                "message": "No matching face found across frames",
                "frames": len(temp_paths),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recognizing faces: {str(e)}")
    finally:
        for p in temp_paths:
            if os.path.exists(p):
                os.unlink(p)

@app.get("/api/face/stats")
async def get_stats():
    """Get statistics about FAISS index and registered faces"""
    return face_system.stats()

@app.post("/api/face/recognize_frame")
async def recognize_frame(file: UploadFile = File(...)):
    """Detect multiple faces in a single frame and recognize each if possible.
    
    Uses 0.7 threshold (70% similarity) for marking attendance - High accuracy.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tf:
            tf.write(await file.read())
            path = tf.name
        try:
            # Use 0.7 threshold = 70% similarity minimum for high accuracy attendance marking
            result = face_system.recognize_faces_in_image(path, threshold=0.7)
            return result
        finally:
            if os.path.exists(path):
                os.unlink(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recognizing frame: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
