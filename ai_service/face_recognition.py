"""Face recognition utilities using InsightFace (ArcFace) and FAISS

Enhancements:
- Multi-frame enrollment and recognition with basic quality filtering
- Aggregation of embeddings across frames (mean of top-K by quality)
"""
import os
import pickle
from typing import Optional, List, Tuple

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
    def __init__(self, index_path: str = "faiss_index"):
        # Persist FAISS artifacts relative to this file so they survive cwd changes
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.index_dir = os.path.join(base_dir, index_path)
        os.makedirs(self.index_dir, exist_ok=True)

        self.index: Optional[faiss.Index] = None
        self.student_ids: list[str] = []
        # ArcFace (buffalo_l) embedding dimension
        self.dimension = 512

        # Initialize InsightFace FaceAnalysis (CPU)
        self.face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        # Larger det_size improves detection quality
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))

        self.load_or_create_index()

    def load_or_create_index(self) -> None:
        """Load existing FAISS index or create a new one."""
        index_file = os.path.join(self.index_dir, "index.faiss")
        ids_file = os.path.join(self.index_dir, "student_ids.pkl")

        if os.path.exists(index_file) and os.path.exists(ids_file):
            self.index = faiss.read_index(index_file)
            with open(ids_file, "rb") as f:
                self.student_ids = pickle.load(f)
            # Safety: ensure index dimension matches expected
            if self.index.d != self.dimension:
                # Recreate an empty index if incompatible (rare)
                self.index = faiss.IndexFlatIP(self.dimension)
                self.student_ids = []
        else:
            # Use inner product on L2-normalized embeddings -> cosine similarity
            self.index = faiss.IndexFlatIP(self.dimension)
            self.student_ids = []

    def save_index(self) -> None:
        """Persist FAISS index and student IDs to disk."""
        index_file = os.path.join(self.index_dir, "index.faiss")
        ids_file = os.path.join(self.index_dir, "student_ids.pkl")

        faiss.write_index(self.index, index_file)
        with open(ids_file, "wb") as f:
            pickle.dump(self.student_ids, f)

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

    # -------- Quality utilities --------
    @staticmethod
    def _image_quality_score(image_path: str) -> float:
        """Compute a simple quality score combining blur and brightness.

        - Blur: Variance of Laplacian (higher is sharper)
        - Brightness: mean pixel intensity (prefer mid-range)
        Score is a weighted sum scaled to ~[0, 1].
        """
        img = cv2.imread(image_path)
        if img is None:
            return 0.0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Blur measure
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Brightness measure (target ~130)
        mean_brightness = float(np.mean(gray))
        brightness_score = 1.0 - min(abs(mean_brightness - 130.0) / 130.0, 1.0)
        # Normalize focus measure roughly (tune 100.0 based on webcam)
        focus_score = min(fm / 100.0, 1.0)
        return 0.7 * focus_score + 0.3 * brightness_score

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
        """Register using multiple frames: quality filter + aggregate embeddings."""
        scored: List[Tuple[float, np.ndarray]] = []
        for p in image_paths:
            try:
                emb = self.extract_embedding(p)
                q = self._image_quality_score(p)
                scored.append((q, emb))
            except Exception:
                continue
        if not scored:
            raise Exception("No valid faces found in frames")
        # sort by quality desc and aggregate top frames
        scored.sort(key=lambda x: x[0], reverse=True)
        emb_list = [e for _, e in scored]
        agg = self._aggregate_embeddings(emb_list, topk=min(5, len(emb_list)))
        if agg is None:
            raise Exception("Failed to aggregate embeddings")
        self.index.add(np.expand_dims(agg, axis=0))
        self.student_ids.append(student_id)
        self.save_index()
        return True

    def recognize_face(self, image_path: str, threshold: float = 0.35):
        """Recognize a face and return the best match if over cosine threshold.

        Using inner product on normalized embeddings -> cosine similarity (higher is better).
        Typical threshold 0.3-0.5 depending on environment. Default 0.35 is conservative.
        """
        if self.index is None or self.index.ntotal == 0:
            return None

        embedding = self.extract_embedding(image_path)
        sims, indices = self.index.search(np.expand_dims(embedding, axis=0), k=1)

        idx = int(indices[0][0]) if indices.size > 0 else -1
        sim = float(sims[0][0]) if sims.size > 0 else -1.0

        if idx >= 0 and sim >= threshold:
            student_id = self.student_ids[idx]
            # confidence ~ normalize similarity into 0..1 with threshold as baseline
            confidence = max(0.0, min(1.0, (sim - threshold) / (1.0 - threshold)))
            return {"student_id": student_id, "confidence": confidence, "similarity": sim}

        return None

    def recognize_face_multi(self, image_paths: List[str], threshold: float = 0.35):
        """Recognize across multiple frames; aggregate votes and confidence.

        Strategy: for each frame, compute cosine similarity to nearest neighbor; keep best.
        Accept if majority votes for same ID and best similarity >= threshold.
        """
        if self.index is None or self.index.ntotal == 0:
            return None
        votes = {}
        best = {"student_id": None, "similarity": -1.0}
        total_frames = 0
        for p in image_paths:
            try:
                emb = self.extract_embedding(p)
            except Exception:
                continue
            total_frames += 1
            sims, indices = self.index.search(np.expand_dims(emb, axis=0), k=1)
            idx = int(indices[0][0]) if indices.size > 0 else -1
            sim = float(sims[0][0]) if sims.size > 0 else -1.0
            if idx >= 0:
                sid = self.student_ids[idx]
                votes[sid] = votes.get(sid, 0) + (1 if sim >= threshold else 0)
                if sim > best["similarity"]:
                    best = {"student_id": sid, "similarity": sim}

        if total_frames == 0 or best["student_id"] is None:
            return None

        winner = max(votes.items(), key=lambda kv: kv[1])[0] if votes else best["student_id"]
        if best["similarity"] >= threshold and votes.get(winner, 0) >= max(1, total_frames // 3):
            confidence = max(0.0, min(1.0, (best["similarity"] - threshold) / (1.0 - threshold)))
            return {"student_id": winner, "confidence": confidence, "similarity": best["similarity"], "frames": total_frames, "votes": votes.get(winner, 0)}
        return None

    def stats(self) -> dict:
        return {
            "index_path": self.index_dir,
            "dimension": self.dimension,
            "ntotal": int(self.index.ntotal) if self.index is not None else 0,
            "registered_students": len(self.student_ids),
        }

    # -------- Multi-face recognition on a single image --------
    def recognize_faces_in_image(self, image_path: str, threshold: float = 0.35):
        """Detect multiple faces in a single image and recognize each independently.

        Returns dict: { image: {width, height}, faces: [{bbox:[x1,y1,x2,y2], recognized:bool, student_id:str|None, similarity:float|None, confidence:float|None}] }
        """
        img = cv2.imread(image_path)
        if img is None:
            raise Exception("Image load failed")

        h, w = img.shape[:2]
        faces = self.face_app.get(img) or []

        results = []
        for f in faces:
            bbox = getattr(f, 'bbox', None)
            emb = getattr(f, 'normed_embedding', None)
            rect = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])] if bbox is not None else [0, 0, 0, 0]

            if self.index is None or self.index.ntotal == 0 or emb is None:
                results.append({
                    "bbox": rect,
                    "recognized": False,
                    "student_id": None,
                    "similarity": None,
                    "confidence": None,
                })
                continue

            emb = emb.astype("float32")
            emb = _l2_normalize(emb)
            sims, idxs = self.index.search(np.expand_dims(emb, 0), k=1)
            idx = int(idxs[0][0]) if idxs.size > 0 else -1
            sim = float(sims[0][0]) if sims.size > 0 else -1.0
            if idx >= 0 and sim >= threshold:
                sid = self.student_ids[idx]
                conf = max(0.0, min(1.0, (sim - threshold) / (1.0 - threshold)))
                results.append({
                    "bbox": rect,
                    "recognized": True,
                    "student_id": sid,
                    "similarity": sim,
                    "confidence": conf,
                })
            else:
                results.append({
                    "bbox": rect,
                    "recognized": False,
                    "student_id": None,
                    "similarity": sim if idx >= 0 else None,
                    "confidence": None,
                })

        return {"image": {"width": int(w), "height": int(h)}, "faces": results}
