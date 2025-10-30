"""Face recognition utilities using InsightFace (ArcFace) and FAISS

Enhancements:
- Multi-frame enrollment and recognition with quality filtering
- Aggregation of embeddings across frames (mean of top-K by quality)
- HNSW index for fast similarity search at scale
- Quality gating to prevent low-quality registrations
- Metadata storage for tracking and analytics
- Performance monitoring and metrics
"""
import os
import pickle
import json
import time
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime

import faiss
import numpy as np
import cv2
from insightface.app import FaceAnalysis


def _l2_normalize(vec: np.ndarray, eps: float = 1e-10) -> np.ndarray:
    """L2-normalize a 1D or 2D numpy array."""
    if vec.ndim == 1:
        denom = np.linalg.norm(vec) + eps
        return vec / denom
    # assume shape (n, d)
    norms = np.linalg.norm(vec, axis=1, keepdims=True) + eps
    return vec / norms


class FaceRecognitionSystem:
    # Quality thresholds
    MIN_QUALITY_THRESHOLD = 0.65  # Minimum quality score for registration
    RECOGNITION_THRESHOLD = 0.70   # Similarity threshold for recognition (70%)
    
    def __init__(self, index_path: str = "faiss_index", use_hnsw: bool = True):
        """Initialize face recognition system with enhanced features.
        
        Args:
            index_path: Directory to store FAISS index and metadata
            use_hnsw: Use HNSW index for faster search (recommended for >100 students)
        """
        # Persist FAISS artifacts relative to this file so they survive cwd changes
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.index_dir = os.path.join(base_dir, index_path)
        os.makedirs(self.index_dir, exist_ok=True)

        self.index: Optional[faiss.Index] = None
        self.student_ids: list[str] = []
        self.metadata: Dict[str, Dict[str, Any]] = {}  # Store metadata per student
        self.use_hnsw = use_hnsw
        
        # ArcFace (buffalo_l) embedding dimension
        self.dimension = 512
        
        # Performance metrics
        self.metrics = {
            'search_times': [],
            'registration_times': [],
            'quality_scores': [],
            'total_searches': 0,
            'total_registrations': 0
        }

        # Initialize InsightFace FaceAnalysis (CPU)
        # buffalo_sc: SCRFD detector (6.9x faster than RetinaFace, 98.57% accuracy on LFW)
        self.face_app = FaceAnalysis(name='buffalo_sc', providers=['CPUExecutionProvider'])
        # Larger det_size improves detection quality
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))

        self.load_or_create_index()
        print(f"✓ FaceRecognitionSystem initialized")
        print(f"  - Model: InsightFace buffalo_sc (SCRFD + ArcFace)")
        print(f"  - Detection: SCRFD (6.9x faster, 98.57% accuracy)")
        print(f"  - Recognition: ArcFace (99.83% accuracy)")
        print(f"  - Index type: {'HNSW (fast)' if use_hnsw else 'Flat (exact)'}")
        print(f"  - Dimension: {self.dimension}")
        print(f"  - Students registered: {len(self.student_ids)}")

    def load_or_create_index(self) -> None:
        """Load existing FAISS index or create a new one with optional HNSW."""
        index_file = os.path.join(self.index_dir, "index.faiss")
        ids_file = os.path.join(self.index_dir, "student_ids.pkl")
        metadata_file = os.path.join(self.index_dir, "metadata.json")

        if os.path.exists(index_file) and os.path.exists(ids_file):
            self.index = faiss.read_index(index_file)
            with open(ids_file, "rb") as f:
                self.student_ids = pickle.load(f)
            
            # Load metadata if exists
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    self.metadata = json.load(f)
            
            # Safety: ensure index dimension matches expected
            if self.index.d != self.dimension:
                print(f"⚠️  Index dimension mismatch: {self.index.d} != {self.dimension}. Recreating...")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self) -> None:
        """Create a new FAISS index based on configuration."""
        if self.use_hnsw:
            # HNSW: Hierarchical Navigable Small World
            # Best for: Fast approximate search, read-heavy workloads
            # M=32: number of bi-directional links per node (higher = more accuracy, more memory)
            # efConstruction=40: quality during construction
            # efSearch will be set dynamically during search
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            self.index.hnsw.efConstruction = 40
            print("✓ Created HNSW index for fast similarity search")
        else:
            # Flat: Exact brute-force search using inner product
            # Use inner product on L2-normalized embeddings -> cosine similarity
            self.index = faiss.IndexFlatIP(self.dimension)
            print("✓ Created Flat index for exact search")
        
        self.student_ids = []
        self.metadata = {}

    def save_index(self) -> None:
        """Persist FAISS index, student IDs, and metadata to disk."""
        index_file = os.path.join(self.index_dir, "index.faiss")
        ids_file = os.path.join(self.index_dir, "student_ids.pkl")
        metadata_file = os.path.join(self.index_dir, "metadata.json")
        
        # Create backup before saving (keep last version)
        backup_dir = os.path.join(self.index_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        if os.path.exists(index_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"index_backup_{timestamp}.faiss")
            try:
                import shutil
                shutil.copy2(index_file, backup_file)
                # Keep only last 3 backups
                backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("index_backup_")])
                for old_backup in backups[:-3]:
                    os.remove(os.path.join(backup_dir, old_backup))
            except Exception as e:
                print(f"⚠️  Backup failed: {e}")

        # Save index and data
        faiss.write_index(self.index, index_file)
        with open(ids_file, "wb") as f:
            pickle.dump(self.student_ids, f)
        with open(metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def extract_embedding(self, image_path: str) -> np.ndarray:
        """Extract a L2-normalized face embedding using InsightFace ArcFace.

        Returns a 512-dim normalized embedding (float32).
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise Exception("Image load failed")
            faces = self.face_app.get(img)
            if not faces:
                raise Exception("No face detected")
            # Choose best face by detection score, fallback to largest area
            best = max(
                faces,
                key=lambda f: getattr(f, 'det_score', 0.0) * 10.0 + (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
            )
            emb = best.normed_embedding.astype("float32")
            # normed_embedding is already L2-normalized, normalize again for safety
            return _l2_normalize(emb)
        except Exception as e:
            raise Exception(f"Face extraction failed: {str(e)}")

    # -------- Enhanced Quality Assessment --------
    @staticmethod
    def _image_quality_score(image_path: str, face_obj=None) -> float:
        """Compute comprehensive quality score for face image.

        Factors considered:
        - Sharpness/Blur: Variance of Laplacian (40% weight)
        - Brightness: Mean pixel intensity (25% weight)
        - Face Size: Larger faces = better quality (20% weight)
        - Detection Confidence: InsightFace detection score (15% weight)
        
        Returns: Quality score in range [0.0, 1.0]
        """
        img = cv2.imread(image_path)
        if img is None:
            return 0.0
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # 1. Sharpness (Laplacian variance) - 40%
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Normalize: typical range 0-500, good images > 100
        sharpness_score = min(laplacian_var / 150.0, 1.0)
        
        # 2. Brightness (optimal range: 100-150) - 25%
        mean_brightness = float(np.mean(gray))
        brightness_score = 1.0 - min(abs(mean_brightness - 125.0) / 125.0, 1.0)
        
        # 3. Face Size (percentage of image area) - 20%
        face_size_score = 0.5  # default
        if face_obj is not None:
            bbox = face_obj.bbox
            face_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            image_area = h * w
            face_ratio = face_area / image_area
            # Optimal face size: 15-40% of image
            if 0.15 <= face_ratio <= 0.40:
                face_size_score = 1.0
            elif face_ratio < 0.15:
                face_size_score = face_ratio / 0.15  # Too small
            else:
                face_size_score = max(0.4, 1.0 - (face_ratio - 0.40) / 0.30)  # Too large
        
        # 4. Detection Confidence - 15%
        det_confidence_score = 0.8  # default
        if face_obj is not None and hasattr(face_obj, 'det_score'):
            det_confidence_score = min(face_obj.det_score, 1.0)
        
        # Weighted combination
        total_score = (
            0.40 * sharpness_score +
            0.25 * brightness_score +
            0.20 * face_size_score +
            0.15 * det_confidence_score
        )
        
        return round(total_score, 3)

    def _aggregate_embeddings(self, emb_list: List[np.ndarray], topk: int = 5) -> Optional[np.ndarray]:
        if not emb_list:
            return None
        # emb_list may be pre-filtered; take mean of up to topk
        stack = np.stack(emb_list[:topk], axis=0).astype("float32")
        mean_emb = np.mean(stack, axis=0)
        return _l2_normalize(mean_emb)

    def register_face(self, image_path: str, student_id: str) -> bool:
        """Register a new face in FAISS index (persistent)."""
        embedding = self.extract_embedding(image_path)

        self.index.add(np.expand_dims(embedding, axis=0))
        self.student_ids.append(student_id)
        self.save_index()
        return True

    def register_face_multi(self, image_paths: List[str], student_id: str) -> bool:
        """Register using multiple frames: quality filter + aggregate embeddings.
        
        Args:
            image_paths: List of paths to face images
            student_id: Unique identifier for the student
            
        Returns:
            True if registration successful
            
        Raises:
            Exception: If no valid faces found or aggregation fails
        """
        scored: List[Tuple[float, np.ndarray]] = []
        errors = []
        
        for idx, p in enumerate(image_paths):
            try:
                emb = self.extract_embedding(p)
                q = self._image_quality_score(p)
                scored.append((q, emb))
            except Exception as e:
                errors.append(f"Frame {idx}: {str(e)}")
                continue
        
        if not scored:
            error_detail = "; ".join(errors) if errors else "Unknown error"
            raise Exception(f"No valid faces found in {len(image_paths)} frames. Details: {error_detail}")
        
        # Require at least 3 valid faces for robust registration
        if len(scored) < min(3, len(image_paths)):
            raise Exception(
                f"Only {len(scored)} valid faces found out of {len(image_paths)} frames. "
                f"Need at least 3 clear face images for reliable registration."
            )
        
        # Sort by quality desc and aggregate top frames
        scored.sort(key=lambda x: x[0], reverse=True)
        emb_list = [e for _, e in scored]
        quality_scores = [q for q, _ in scored]
        
        # Quality Gating: Check if best frame meets minimum quality
        best_quality = quality_scores[0]
        avg_quality = np.mean(quality_scores)
        
        if best_quality < self.MIN_QUALITY_THRESHOLD:
            raise Exception(
                f"Face quality too low (best: {best_quality:.2f}, required: {self.MIN_QUALITY_THRESHOLD:.2f}). "
                f"Please ensure good lighting, remove glasses, and keep face centered."
            )
        
        print(f"  Quality scores: best={best_quality:.3f}, avg={avg_quality:.3f}, frames={len(scored)}")
        
        # Use top 5 highest quality frames for aggregation
        agg = self._aggregate_embeddings(emb_list, topk=min(5, len(emb_list)))
        if agg is None:
            raise Exception("Failed to aggregate embeddings")
        
        # Track registration time
        reg_start = time.time()
        
        # Add to FAISS index
        self.index.add(np.expand_dims(agg, axis=0))
        self.student_ids.append(student_id)
        
        # Store metadata
        self.metadata[student_id] = {
            'registration_date': datetime.now().isoformat(),
            'quality_best': float(best_quality),
            'quality_avg': float(avg_quality),
            'frames_used': len(scored),
            'frames_total': len(image_paths),
            'model_version': 'buffalo_l',
            'embedding_norm': float(np.linalg.norm(agg)),
            'threshold_used': self.RECOGNITION_THRESHOLD
        }
        
        # Save everything
        self.save_index()
        
        reg_time = (time.time() - reg_start) * 1000
        self.metrics['registration_times'].append(reg_time)
        self.metrics['quality_scores'].append(avg_quality)
        self.metrics['total_registrations'] += 1
        
        print(f"✓ Registered student {student_id} with {len(scored)}/{len(image_paths)} valid frames")
        print(f"  Registration time: {reg_time:.1f}ms")
        return True

    def recognize_face(self, image_path: str, threshold: float = 0.70):
        """Recognize a face and return the best match if over cosine threshold.

        Using inner product on normalized embeddings -> cosine similarity (higher is better).
        Default threshold: 0.70 (70%) for high security and accuracy.
        """
        if self.index is None or self.index.ntotal == 0:
            return None

        # Set HNSW search quality if using HNSW index
        if self.use_hnsw and hasattr(self.index, 'hnsw'):
            self.index.hnsw.efSearch = 32  # Higher = more accurate but slower
        
        search_start = time.time()
        embedding = self.extract_embedding(image_path)
        sims, indices = self.index.search(np.expand_dims(embedding, axis=0), k=1)
        search_time = (time.time() - search_start) * 1000

        idx = int(indices[0][0]) if indices.size > 0 else -1
        sim = float(sims[0][0]) if sims.size > 0 else -1.0

        # Track search performance
        self.metrics['search_times'].append(search_time)
        self.metrics['total_searches'] += 1

        if idx >= 0 and sim >= threshold:
            student_id = self.student_ids[idx]
            # confidence ~ normalize similarity into 0..1 with threshold as baseline
            confidence = max(0.0, min(1.0, (sim - threshold) / (1.0 - threshold)))
            return {"student_id": student_id, "confidence": confidence, "similarity": sim}

        return None

    def recognize_face_multi(self, image_paths: List[str], threshold: float = None, min_votes_ratio: float = 0.6):
        """Recognize across multiple frames with robust voting mechanism.

        Strategy: 
        - Extract embeddings from all frames
        - Search FAISS for nearest neighbor per frame
        - Aggregate votes: only count frames where similarity >= threshold
        - Require super-majority (60%+) of valid frames to agree on same ID
        - Return highest confidence match if voting threshold met

        Args:
            image_paths: List of image paths to process
            threshold: Minimum cosine similarity (default: 0.70 = 70% for high security)
            min_votes_ratio: Minimum ratio of frames that must agree (0.6 = 60%)

        Returns:
            Dict with student_id, confidence, similarity, frames, votes
            None if no confident match found
        """
        if self.index is None or self.index.ntotal == 0:
            return None
        
        # Use class threshold if not specified
        if threshold is None:
            threshold = self.RECOGNITION_THRESHOLD
        
        # Set HNSW search quality if using HNSW index
        if self.use_hnsw and hasattr(self.index, 'hnsw'):
            self.index.hnsw.efSearch = 32  # Higher = more accurate but slower
        
        multi_search_start = time.time()
        
        # Track votes and similarities for each student ID
        votes = {}  # {student_id: vote_count}
        similarities = {}  # {student_id: [similarities]}
        valid_frames = 0
        total_frames = 0
        
        for idx, p in enumerate(image_paths):
            try:
                emb = self.extract_embedding(p)
            except Exception as e:
                # Skip frames with no face detected
                continue
            
            total_frames += 1
            
            # Search FAISS index for nearest match
            sims, indices = self.index.search(np.expand_dims(emb, axis=0), k=1)
            match_idx = int(indices[0][0]) if indices.size > 0 else -1
            similarity = float(sims[0][0]) if sims.size > 0 else -1.0
            
            if match_idx >= 0 and similarity >= threshold:
                sid = self.student_ids[match_idx]
                votes[sid] = votes.get(sid, 0) + 1
                if sid not in similarities:
                    similarities[sid] = []
                similarities[sid].append(similarity)
                valid_frames += 1

        # No valid matches found
        if valid_frames == 0 or not votes:
            return None

        # Find student with most votes
        winner_id = max(votes.items(), key=lambda kv: kv[1])[0]
        winner_votes = votes[winner_id]
        winner_sims = similarities[winner_id]
        
        # Security check: require super-majority of valid frames
        vote_ratio = winner_votes / valid_frames if valid_frames > 0 else 0
        
        if vote_ratio >= min_votes_ratio:
            # Use average of top similarities for robust confidence
            avg_similarity = float(np.mean(sorted(winner_sims, reverse=True)[:min(3, len(winner_sims))]))
            confidence = max(0.0, min(1.0, (avg_similarity - threshold) / (1.0 - threshold)))
            
            # Track performance
            multi_search_time = (time.time() - multi_search_start) * 1000
            self.metrics['search_times'].append(multi_search_time)
            self.metrics['total_searches'] += 1
            
            return {
                "student_id": winner_id,
                "confidence": confidence,
                "similarity": avg_similarity,
                "max_similarity": float(max(winner_sims)),
                "frames": total_frames,
                "valid_frames": valid_frames,
                "votes": winner_votes,
                "vote_ratio": vote_ratio,
                "search_time_ms": round(multi_search_time, 2)
            }
        
        # Not enough consensus
        return None

    def stats(self) -> dict:
        """Get comprehensive statistics about the face recognition system."""
        avg_search_time = np.mean(self.metrics['search_times'][-100:]) if self.metrics['search_times'] else 0
        avg_reg_time = np.mean(self.metrics['registration_times'][-100:]) if self.metrics['registration_times'] else 0
        avg_quality = np.mean(self.metrics['quality_scores'][-100:]) if self.metrics['quality_scores'] else 0
        
        return {
            "index_path": self.index_dir,
            "dimension": self.dimension,
            "index_type": "HNSW" if self.use_hnsw else "Flat",
            "ntotal": int(self.index.ntotal) if self.index is not None else 0,
            "registered_students": len(self.student_ids),
            "model": "InsightFace buffalo_l (ArcFace)",
            "thresholds": {
                "recognition": self.RECOGNITION_THRESHOLD,
                "min_quality": self.MIN_QUALITY_THRESHOLD
            },
            "performance": {
                "avg_search_time_ms": round(avg_search_time, 2),
                "avg_registration_time_ms": round(avg_reg_time, 2),
                "total_searches": self.metrics['total_searches'],
                "total_registrations": self.metrics['total_registrations']
            },
            "quality": {
                "avg_quality_score": round(avg_quality, 3),
                "samples": len(self.metrics['quality_scores'])
            },
            "registered_students": len(self.student_ids),
        }

    # -------- Multi-face recognition on a single image --------
    def recognize_faces_in_image(self, image_path: str, threshold: float = 0.35):
        """Detect multiple faces in a single image and recognize each independently.
        
        Optimized for speed:
        - Single face detection pass
        - Batch FAISS search for all faces
        - Returns bounding boxes and recognition results
        
        Returns dict: 
        { 
            image: {width, height}, 
            faces: [{
                bbox:[x1,y1,x2,y2], 
                recognized:bool, 
                student_id:str|None, 
                similarity:float|None, 
                confidence:float|None,
                det_score:float
            }] 
        }
        """
        img = cv2.imread(image_path)
        if img is None:
            raise Exception("Image load failed")

        h, w = img.shape[:2]
        faces = self.face_app.get(img) or []

        if not faces:
            return {"image": {"width": w, "height": h}, "faces": []}

        results = []
        
        # Batch process all embeddings for speed
        embeddings = []
        face_data = []
        
        for f in faces:
            bbox = getattr(f, 'bbox', None)
            emb = getattr(f, 'normed_embedding', None)
            det_score = getattr(f, 'det_score', 0.0)
            rect = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])] if bbox is not None else [0, 0, 0, 0]
            
            face_data.append({
                "bbox": rect,
                "det_score": float(det_score)
            })
            
            if emb is not None:
                embeddings.append(_l2_normalize(emb.astype("float32")))
            else:
                embeddings.append(None)

        # Batch FAISS search for all valid embeddings (fast!)
        if self.index is not None and self.index.ntotal > 0:
            valid_embs = [e for e in embeddings if e is not None]
            if valid_embs:
                # Single batch search for all faces - much faster than individual searches
                emb_array = np.stack(valid_embs, axis=0)
                sims, indices = self.index.search(emb_array, k=1)
                
                valid_idx = 0
                for i, emb in enumerate(embeddings):
                    if emb is None:
                        # No embedding extracted for this face
                        results.append({
                            **face_data[i],
                            "recognized": False,
                            "student_id": None,
                            "similarity": None,
                            "confidence": None,
                        })
                    else:
                        # Use pre-computed batch search result
                        match_idx = int(indices[valid_idx][0])
                        similarity = float(sims[valid_idx][0])
                        valid_idx += 1
                        
                        if match_idx >= 0 and similarity >= threshold:
                            sid = self.student_ids[match_idx]
                            conf = max(0.0, min(1.0, (similarity - threshold) / (1.0 - threshold)))
                            results.append({
                                **face_data[i],
                                "recognized": True,
                                "student_id": sid,
                                "similarity": similarity,
                                "confidence": conf,
                            })
                        else:
                            results.append({
                                **face_data[i],
                                "recognized": False,
                                "student_id": None,
                                "similarity": similarity if match_idx >= 0 else None,
                                "confidence": None,
                            })
            else:
                # No valid embeddings extracted
                for i in range(len(face_data)):
                    results.append({
                        **face_data[i],
                        "recognized": False,
                        "student_id": None,
                        "similarity": None,
                        "confidence": None,
                    })
        else:
            # No index or empty index
            for i in range(len(face_data)):
                results.append({
                    **face_data[i],
                    "recognized": False,
                    "student_id": None,
                    "similarity": None,
                    "confidence": None,
                })

        return {"image": {"width": int(w), "height": int(h)}, "faces": results}
