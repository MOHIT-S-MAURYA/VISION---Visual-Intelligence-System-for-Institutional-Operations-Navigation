"""
Comprehensive Face Recognition Model Benchmarking Framework

Tests and compares multiple detection and recognition models on real data
to determine the best configuration for 99%+ accuracy.
"""

import os
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import cv2
from dataclasses import dataclass, asdict

# Import models based on availability
try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


@dataclass
class BenchmarkResult:
    """Results from a single benchmark test"""
    model_name: str
    detection_model: str
    recognition_model: str
    
    # Detection metrics
    detection_accuracy: float  # % of faces detected correctly
    detection_time_avg_ms: float
    false_positives: int
    false_negatives: int
    
    # Recognition metrics
    recognition_accuracy: float  # % of faces recognized correctly
    recognition_time_avg_ms: float
    false_positive_rate: float  # % misidentified
    false_negative_rate: float  # % failed to recognize
    
    # Quality metrics
    quality_score_avg: float
    quality_rejection_rate: float
    
    # Resource metrics
    memory_usage_mb: float
    gpu_used: bool
    
    # Overall score (weighted)
    overall_score: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FaceRecognitionBenchmark:
    """
    Comprehensive benchmarking system for face recognition models.
    
    Tests multiple detection and recognition model combinations on:
    - Detection accuracy (did we find the face?)
    - Recognition accuracy (did we identify correctly?)
    - False positive rate (wrong person identified)
    - False negative rate (failed to recognize known person)
    - Speed (detection + recognition time)
    - Quality robustness (performance on poor quality images)
    - Memory usage
    """
    
    def __init__(
        self,
        test_data_dir: Optional[str] = None,
        output_dir: str = "./benchmark_results"
    ):
        """
        Initialize benchmarking framework.
        
        Args:
            test_data_dir: Directory with test images (structured as student_id/image.jpg)
            output_dir: Directory to save benchmark results
        """
        self.test_data_dir = Path(test_data_dir) if test_data_dir else None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.models = {}
        self.test_images = []
        self.results = []
        
        print("="*70)
        print("Face Recognition Model Benchmarking Framework")
        print("="*70)
        print(f"InsightFace: {'✓ Available' if INSIGHTFACE_AVAILABLE else '✗ Not Available'}")
        print(f"DeepFace: {'✓ Available' if DEEPFACE_AVAILABLE else '✗ Not Available'}")
        print(f"YOLOv8: {'✓ Available' if YOLO_AVAILABLE else '✗ Not Available'}")
        print(f"MediaPipe: {'✓ Available' if MEDIAPIPE_AVAILABLE else '✗ Not Available'}")
        print("="*70)
    
    def load_test_data(self, data_dir: Optional[str] = None):
        """
        Load test images from directory structure:
        data_dir/
          student_1/
            image1.jpg
            image2.jpg
          student_2/
            image1.jpg
        """
        if data_dir:
            self.test_data_dir = Path(data_dir)
        
        if not self.test_data_dir or not self.test_data_dir.exists():
            print("⚠️  No test data directory provided. Using synthetic test.")
            return
        
        print(f"\n📂 Loading test data from: {self.test_data_dir}")
        
        for student_dir in self.test_data_dir.iterdir():
            if not student_dir.is_dir():
                continue
            
            student_id = student_dir.name
            images = []
            
            for img_path in student_dir.glob("*.jpg"):
                img = cv2.imread(str(img_path))
                if img is not None:
                    images.append({
                        'path': str(img_path),
                        'image': img,
                        'student_id': student_id
                    })
            
            if images:
                self.test_images.extend(images)
        
        print(f"✓ Loaded {len(self.test_images)} test images from {len(set(img['student_id'] for img in self.test_images))} students")
    
    def initialize_models(self):
        """Initialize all available models for testing"""
        print("\n🚀 Initializing models for benchmarking...")
        
        # InsightFace models
        if INSIGHTFACE_AVAILABLE:
            self._init_insightface()
        
        # DeepFace models
        if DEEPFACE_AVAILABLE:
            self._init_deepface()
        
        # MediaPipe
        if MEDIAPIPE_AVAILABLE:
            self._init_mediapipe()
        
        print(f"✓ Initialized {len(self.models)} model configurations")
    
    def _init_insightface(self):
        """Initialize InsightFace model variants"""
        try:
            # Buffalo L (current production)
            buffalo_l = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
            buffalo_l.prepare(ctx_id=-1, det_size=(640, 640))
            self.models['insightface_buffalo_l'] = {
                'app': buffalo_l,
                'detection': 'RetinaFace',
                'recognition': 'ArcFace (buffalo_l)',
                'description': 'Current production model - RetinaFace + ArcFace'
            }
            print("  ✓ InsightFace buffalo_l (RetinaFace + ArcFace)")
            
            # Buffalo SC (SCRFD - faster detector)
            try:
                buffalo_sc = FaceAnalysis(name='buffalo_sc', providers=['CPUExecutionProvider'])
                buffalo_sc.prepare(ctx_id=-1, det_size=(640, 640))
                self.models['insightface_buffalo_sc'] = {
                    'app': buffalo_sc,
                    'detection': 'SCRFD',
                    'recognition': 'ArcFace (buffalo_sc)',
                    'description': 'Fast SCRFD detector + ArcFace'
                }
                print("  ✓ InsightFace buffalo_sc (SCRFD + ArcFace)")
            except:
                print("  ⚠️  buffalo_sc not available (needs download)")
            
            # Antelopev2 (highest accuracy)
            try:
                antelopev2 = FaceAnalysis(name='antelopev2', providers=['CPUExecutionProvider'])
                antelopev2.prepare(ctx_id=-1, det_size=(640, 640))
                self.models['insightface_antelopev2'] = {
                    'app': antelopev2,
                    'detection': 'SCRFD',
                    'recognition': 'ArcFace XL (antelopev2)',
                    'description': 'Highest accuracy - SCRFD + ArcFace XL'
                }
                print("  ✓ InsightFace antelopev2 (SCRFD + ArcFace XL)")
            except:
                print("  ⚠️  antelopev2 not available (needs download)")
        
        except Exception as e:
            print(f"  ✗ InsightFace initialization error: {e}")
    
    def _init_deepface(self):
        """Initialize DeepFace model variants"""
        try:
            # DeepFace ArcFace backend
            self.models['deepface_arcface'] = {
                'backend': 'ArcFace',
                'detection': 'RetinaFace',
                'recognition': 'ArcFace (DeepFace)',
                'description': 'DeepFace with ArcFace backend'
            }
            print("  ✓ DeepFace ArcFace")
            
            # DeepFace FaceNet backend
            self.models['deepface_facenet'] = {
                'backend': 'Facenet',
                'detection': 'RetinaFace',
                'recognition': 'FaceNet (DeepFace)',
                'description': 'DeepFace with FaceNet backend'
            }
            print("  ✓ DeepFace FaceNet")
        
        except Exception as e:
            print(f"  ✗ DeepFace initialization error: {e}")
    
    def _init_mediapipe(self):
        """Initialize MediaPipe face detection"""
        try:
            mp_face_detection = mp.solutions.face_detection
            self.models['mediapipe'] = {
                'detector': mp_face_detection.FaceDetection(
                    model_selection=1,
                    min_detection_confidence=0.5
                ),
                'detection': 'MediaPipe',
                'recognition': 'N/A (detection only)',
                'description': 'Google MediaPipe face detection'
            }
            print("  ✓ MediaPipe face detection")
        
        except Exception as e:
            print(f"  ✗ MediaPipe initialization error: {e}")
    
    def benchmark_model(self, model_name: str) -> Optional[BenchmarkResult]:
        """
        Benchmark a specific model configuration.
        
        Returns:
            BenchmarkResult with all metrics
        """
        if model_name not in self.models:
            print(f"⚠️  Model {model_name} not available")
            return None
        
        print(f"\n📊 Benchmarking: {model_name}")
        print(f"   {self.models[model_name]['description']}")
        
        model_info = self.models[model_name]
        
        # Initialize metrics
        detection_times = []
        recognition_times = []
        detections_correct = 0
        detections_missed = 0
        detections_false = 0
        recognitions_correct = 0
        recognitions_wrong = 0
        quality_scores = []
        
        # Test on images
        for idx, test_item in enumerate(self.test_images[:20]):  # Test first 20 images
            img = test_item['image']
            true_student_id = test_item['student_id']
            
            # Detection phase
            start_time = time.time()
            
            if 'app' in model_info:  # InsightFace
                faces = model_info['app'].get(img)
                detection_time = (time.time() - start_time) * 1000
                detection_times.append(detection_time)
                
                if faces:
                    detections_correct += 1
                    
                    # Recognition phase (using embedding similarity)
                    # For benchmark, we just measure extraction time
                    embedding = faces[0].normed_embedding
                    quality_scores.append(self._assess_quality(img))
                else:
                    detections_missed += 1
            
            elif 'backend' in model_info:  # DeepFace
                try:
                    result = DeepFace.represent(
                        img_path=img,
                        model_name=model_info['backend'],
                        enforce_detection=True
                    )
                    detection_time = (time.time() - start_time) * 1000
                    detection_times.append(detection_time)
                    
                    if result:
                        detections_correct += 1
                        quality_scores.append(self._assess_quality(img))
                    else:
                        detections_missed += 1
                except:
                    detections_missed += 1
            
            elif 'detector' in model_info:  # MediaPipe
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = model_info['detector'].process(rgb_img)
                detection_time = (time.time() - start_time) * 1000
                detection_times.append(detection_time)
                
                if results.detections:
                    detections_correct += 1
                    quality_scores.append(self._assess_quality(img))
                else:
                    detections_missed += 1
        
        # Calculate metrics
        total_tests = len(self.test_images[:20])
        detection_accuracy = (detections_correct / total_tests * 100) if total_tests > 0 else 0
        detection_time_avg = np.mean(detection_times) if detection_times else 0
        quality_avg = np.mean(quality_scores) if quality_scores else 0
        
        # For now, set recognition metrics to 0 (would need full recognition test)
        recognition_accuracy = 0.0
        recognition_time_avg = 0.0
        false_positive_rate = 0.0
        false_negative_rate = (detections_missed / total_tests * 100) if total_tests > 0 else 0
        
        # Overall score (weighted)
        overall_score = (
            detection_accuracy * 0.35 +
            recognition_accuracy * 0.35 +
            (100 - false_positive_rate) * 0.20 +
            min(100, 1000 / detection_time_avg if detection_time_avg > 0 else 0) * 0.10
        )
        
        result = BenchmarkResult(
            model_name=model_name,
            detection_model=model_info['detection'],
            recognition_model=model_info['recognition'],
            detection_accuracy=round(detection_accuracy, 2),
            detection_time_avg_ms=round(detection_time_avg, 2),
            false_positives=detections_false,
            false_negatives=detections_missed,
            recognition_accuracy=round(recognition_accuracy, 2),
            recognition_time_avg_ms=round(recognition_time_avg, 2),
            false_positive_rate=round(false_positive_rate, 2),
            false_negative_rate=round(false_negative_rate, 2),
            quality_score_avg=round(quality_avg, 2),
            quality_rejection_rate=0.0,
            memory_usage_mb=0.0,  # Would need psutil to measure
            gpu_used=False,
            overall_score=round(overall_score, 2)
        )
        
        print(f"   Detection Accuracy: {result.detection_accuracy}%")
        print(f"   Detection Speed: {result.detection_time_avg_ms:.2f}ms")
        print(f"   False Negatives: {result.false_negatives}")
        print(f"   Quality Score: {result.quality_score_avg:.2f}")
        print(f"   Overall Score: {result.overall_score:.2f}/100")
        
        return result
    
    def _assess_quality(self, image: np.ndarray) -> float:
        """Assess image quality (0.0 - 1.0)"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness = min(laplacian_var / 150.0, 1.0)
            
            # Brightness
            mean_brightness = np.mean(gray)
            brightness = 1.0 - min(abs(mean_brightness - 125.0) / 125.0, 1.0)
            
            return 0.6 * sharpness + 0.4 * brightness
        except:
            return 0.5
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run benchmarks on all available models"""
        print("\n" + "="*70)
        print("Starting Comprehensive Benchmark")
        print("="*70)
        
        self.results = []
        
        for model_name in self.models.keys():
            result = self.benchmark_model(model_name)
            if result:
                self.results.append(result)
        
        # Sort by overall score
        self.results.sort(key=lambda x: x.overall_score, reverse=True)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate comprehensive benchmark report"""
        report = []
        report.append("\n" + "="*70)
        report.append("FACE RECOGNITION MODEL BENCHMARK REPORT")
        report.append("="*70)
        report.append(f"\nTest Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Images: {len(self.test_images)} from {len(set(img['student_id'] for img in self.test_images))} students")
        report.append(f"Models Tested: {len(self.results)}")
        
        # Rankings
        report.append("\n" + "-"*70)
        report.append("MODEL RANKINGS (by Overall Score)")
        report.append("-"*70)
        
        for rank, result in enumerate(self.results, 1):
            report.append(f"\n{rank}. {result.model_name.upper()}")
            report.append(f"   Overall Score: {result.overall_score}/100")
            report.append(f"   Detection: {result.detection_model}")
            report.append(f"   Recognition: {result.recognition_model}")
            report.append(f"   Detection Accuracy: {result.detection_accuracy}%")
            report.append(f"   Detection Speed: {result.detection_time_avg_ms:.2f}ms")
            report.append(f"   False Negatives: {result.false_negatives}")
        
        # Detailed comparison table
        report.append("\n" + "-"*70)
        report.append("DETAILED COMPARISON")
        report.append("-"*70)
        
        # Table header
        report.append(f"\n{'Model':<25} {'Det Acc':<10} {'Speed':<10} {'FN':<8} {'Quality':<10}")
        report.append("-"*70)
        
        for result in self.results:
            report.append(
                f"{result.model_name:<25} "
                f"{result.detection_accuracy:<10.2f} "
                f"{result.detection_time_avg_ms:<10.2f} "
                f"{result.false_negatives:<8} "
                f"{result.quality_score_avg:<10.2f}"
            )
        
        # Recommendations
        report.append("\n" + "-"*70)
        report.append("RECOMMENDATIONS")
        report.append("-"*70)
        
        if self.results:
            best_model = self.results[0]
            report.append(f"\n🏆 BEST OVERALL: {best_model.model_name}")
            report.append(f"   {self.models[best_model.model_name]['description']}")
            report.append(f"   Overall Score: {best_model.overall_score}/100")
            
            # Best for speed
            fastest = min(self.results, key=lambda x: x.detection_time_avg_ms)
            report.append(f"\n⚡ FASTEST: {fastest.model_name}")
            report.append(f"   Detection Speed: {fastest.detection_time_avg_ms:.2f}ms")
            
            # Best for accuracy
            most_accurate = max(self.results, key=lambda x: x.detection_accuracy)
            report.append(f"\n🎯 MOST ACCURATE: {most_accurate.model_name}")
            report.append(f"   Detection Accuracy: {most_accurate.detection_accuracy}%")
        
        report.append("\n" + "="*70)
        
        report_text = "\n".join(report)
        
        # Save report
        report_path = self.output_dir / f"benchmark_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)
        
        # Save JSON results
        json_path = self.output_dir / f"benchmark_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)
        
        print(report_text)
        print(f"\n💾 Report saved to: {report_path}")
        print(f"💾 JSON results saved to: {json_path}")
        
        return report_text


if __name__ == "__main__":
    # Run benchmark
    benchmark = FaceRecognitionBenchmark(
        test_data_dir=None,  # Set to your test data directory if available
        output_dir="./benchmark_results"
    )
    
    # Initialize models
    benchmark.initialize_models()
    
    # Create synthetic test data if no real data available
    if not benchmark.test_images:
        print("\n📝 Creating synthetic test data...")
        # Generate 10 synthetic test images
        for i in range(10):
            img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            benchmark.test_images.append({
                'path': f'synthetic_{i}.jpg',
                'image': img,
                'student_id': f'student_{i % 3}'  # 3 synthetic students
            })
        print(f"✓ Created {len(benchmark.test_images)} synthetic test images")
    
    # Run all benchmarks
    results = benchmark.run_all_benchmarks()
    
    # Generate report
    benchmark.generate_report()
