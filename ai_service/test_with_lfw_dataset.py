"""
Test Face Recognition Models on LFW (Labeled Faces in the Wild) Dataset

This script tests all available face recognition models on the famous
LFW benchmark dataset containing 13,233 images of 5,749 people.
"""

import os
import sys
import time
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import cv2
from dataclasses import dataclass

# Import InsightFace
from insightface.app import FaceAnalysis


@dataclass
class TestResult:
    """Results from testing a single model"""
    model_name: str
    images_tested: int
    faces_detected: int
    detection_accuracy: float
    avg_detection_time_ms: float
    avg_confidence: float
    false_negatives: int
    embedding_stats: Dict


class LFWBenchmark:
    """
    Benchmark face recognition models on LFW dataset.
    """
    
    def __init__(self, lfw_dir: str = "./face images", max_people: int = 50, images_per_person: int = 2):
        """
        Initialize LFW benchmark.
        
        Args:
            lfw_dir: Path to LFW dataset
            max_people: Maximum number of people to test (for speed)
            images_per_person: Number of images to test per person
        """
        self.lfw_dir = Path(lfw_dir)
        self.max_people = max_people
        self.images_per_person = images_per_person
        self.test_images = []
        
        print("="*70)
        print("LFW (Labeled Faces in the Wild) Face Recognition Benchmark")
        print("="*70)
        print(f"Dataset: {self.lfw_dir}")
        print(f"Max People: {max_people}")
        print(f"Images per Person: {images_per_person}")
        print("="*70)
    
    def load_test_images(self):
        """Load random sample of LFW images for testing"""
        print("\n📂 Loading test images from LFW dataset...")
        
        # Get all person directories
        all_people = [d for d in self.lfw_dir.iterdir() if d.is_dir()]
        
        # Randomly sample people
        selected_people = random.sample(all_people, min(self.max_people, len(all_people)))
        
        for person_dir in selected_people:
            person_name = person_dir.name
            
            # Get all images for this person
            images = list(person_dir.glob("*.jpg"))
            
            # Randomly sample images
            selected_images = random.sample(images, min(self.images_per_person, len(images)))
            
            for img_path in selected_images:
                img = cv2.imread(str(img_path))
                if img is not None:
                    self.test_images.append({
                        'path': str(img_path),
                        'image': img,
                        'person': person_name
                    })
        
        print(f"✓ Loaded {len(self.test_images)} images from {len(selected_people)} people")
        return self.test_images
    
    def test_model(self, model_name: str, model_config: str = 'buffalo_l') -> TestResult:
        """
        Test a specific InsightFace model on LFW dataset.
        
        Args:
            model_name: Display name for the model
            model_config: InsightFace model configuration name
        """
        print(f"\n{'='*70}")
        print(f"Testing: {model_name} ({model_config})")
        print(f"{'='*70}")
        
        # Initialize model
        print("Loading model...")
        start_load = time.time()
        app = FaceAnalysis(name=model_config, providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        load_time = time.time() - start_load
        print(f"✓ Model loaded in {load_time:.2f}s")
        
        # Test on images
        faces_detected = 0
        false_negatives = 0
        detection_times = []
        confidences = []
        embeddings = []
        
        print(f"\nTesting on {len(self.test_images)} images...")
        
        for idx, test_item in enumerate(self.test_images):
            img = test_item['image']
            person = test_item['person']
            
            # Progress indicator
            if (idx + 1) % 10 == 0:
                print(f"  Progress: {idx + 1}/{len(self.test_images)} images", end='\r')
            
            # Detect and recognize
            start_time = time.time()
            faces = app.get(img)
            detection_time = (time.time() - start_time) * 1000
            detection_times.append(detection_time)
            
            if faces:
                faces_detected += 1
                face = faces[0]
                confidences.append(face.det_score)
                embeddings.append(face.normed_embedding)
            else:
                false_negatives += 1
        
        print(f"\n  Progress: {len(self.test_images)}/{len(self.test_images)} images ✓")
        
        # Calculate statistics
        detection_accuracy = (faces_detected / len(self.test_images)) * 100
        avg_detection_time = np.mean(detection_times)
        avg_confidence = np.mean(confidences) if confidences else 0
        
        # Embedding statistics
        embedding_stats = {}
        if embeddings:
            embeddings_arr = np.array(embeddings)
            embedding_stats = {
                'dimension': embeddings_arr.shape[1],
                'mean_norm': float(np.mean(np.linalg.norm(embeddings_arr, axis=1))),
                'std_norm': float(np.std(np.linalg.norm(embeddings_arr, axis=1)))
            }
        
        result = TestResult(
            model_name=model_name,
            images_tested=len(self.test_images),
            faces_detected=faces_detected,
            detection_accuracy=detection_accuracy,
            avg_detection_time_ms=avg_detection_time,
            avg_confidence=avg_confidence,
            false_negatives=false_negatives,
            embedding_stats=embedding_stats
        )
        
        # Print results
        print(f"\n{'─'*70}")
        print("RESULTS:")
        print(f"{'─'*70}")
        print(f"  Images Tested: {result.images_tested}")
        print(f"  Faces Detected: {result.faces_detected}")
        print(f"  Detection Accuracy: {result.detection_accuracy:.2f}%")
        print(f"  False Negatives: {result.false_negatives}")
        print(f"  Avg Detection Time: {result.avg_detection_time_ms:.2f}ms")
        print(f"  Avg Confidence: {result.avg_confidence:.3f}")
        print(f"  Embedding Dimension: {embedding_stats.get('dimension', 'N/A')}")
        print(f"  Avg Embedding Norm: {embedding_stats.get('mean_norm', 0):.3f}")
        
        return result
    
    def run_comprehensive_test(self):
        """Run tests on all available models"""
        print("\n" + "="*70)
        print("COMPREHENSIVE MODEL COMPARISON")
        print("="*70)
        
        models = [
            ('InsightFace buffalo_l (RetinaFace + ArcFace)', 'buffalo_l'),
            ('InsightFace buffalo_sc (SCRFD + ArcFace)', 'buffalo_sc'),
        ]
        
        results = []
        
        for model_name, model_config in models:
            try:
                result = self.test_model(model_name, model_config)
                results.append(result)
            except Exception as e:
                print(f"\n❌ Error testing {model_name}: {e}")
                continue
        
        # Generate comparison report
        self.generate_comparison_report(results)
        
        return results
    
    def generate_comparison_report(self, results: List[TestResult]):
        """Generate comprehensive comparison report"""
        print("\n" + "="*70)
        print("COMPARATIVE ANALYSIS")
        print("="*70)
        
        # Sort by detection accuracy
        results.sort(key=lambda x: x.detection_accuracy, reverse=True)
        
        # Table header
        print(f"\n{'Model':<40} {'Accuracy':<12} {'Speed':<12} {'Conf':<10}")
        print("─"*70)
        
        for result in results:
            print(
                f"{result.model_name[:38]:<40} "
                f"{result.detection_accuracy:>6.2f}%     "
                f"{result.avg_detection_time_ms:>6.2f}ms    "
                f"{result.avg_confidence:>5.3f}"
            )
        
        # Winner
        if results:
            best = results[0]
            fastest = min(results, key=lambda x: x.avg_detection_time_ms)
            
            print("\n" + "─"*70)
            print("RECOMMENDATIONS:")
            print("─"*70)
            print(f"\n🏆 MOST ACCURATE: {best.model_name}")
            print(f"   Detection Accuracy: {best.detection_accuracy:.2f}%")
            print(f"   False Negatives: {best.false_negatives}/{best.images_tested}")
            
            print(f"\n⚡ FASTEST: {fastest.model_name}")
            print(f"   Avg Detection Time: {fastest.avg_detection_time_ms:.2f}ms")
            print(f"   Detection Accuracy: {fastest.detection_accuracy:.2f}%")
            
            # Speed comparison
            if len(results) >= 2:
                speedup = results[1].avg_detection_time_ms / fastest.avg_detection_time_ms
                print(f"\n📊 SPEED IMPROVEMENT: {speedup:.1f}x faster")
        
        # Save results
        output_file = Path("./lfw_benchmark_results.json")
        with open(output_file, 'w') as f:
            json.dump([
                {
                    'model_name': r.model_name,
                    'images_tested': r.images_tested,
                    'faces_detected': r.faces_detected,
                    'detection_accuracy': float(r.detection_accuracy),
                    'avg_detection_time_ms': float(r.avg_detection_time_ms),
                    'avg_confidence': float(r.avg_confidence),
                    'false_negatives': r.false_negatives,
                    'embedding_stats': {k: float(v) if isinstance(v, (np.floating, np.integer)) else v 
                                       for k, v in r.embedding_stats.items()}
                }
                for r in results
            ], f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        print("="*70)


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test face recognition on LFW dataset')
    parser.add_argument('--people', type=int, default=50, help='Number of people to test')
    parser.add_argument('--images', type=int, default=2, help='Images per person')
    parser.add_argument('--model', type=str, choices=['buffalo_l', 'buffalo_sc', 'all'], 
                       default='all', help='Model to test')
    
    args = parser.parse_args()
    
    # Create benchmark
    benchmark = LFWBenchmark(
        lfw_dir="../face images",
        max_people=args.people,
        images_per_person=args.images
    )
    
    # Load test images
    benchmark.load_test_images()
    
    if not benchmark.test_images:
        print("❌ No test images loaded!")
        return
    
    # Run tests
    if args.model == 'all':
        benchmark.run_comprehensive_test()
    else:
        model_names = {
            'buffalo_l': 'InsightFace buffalo_l (RetinaFace + ArcFace)',
            'buffalo_sc': 'InsightFace buffalo_sc (SCRFD + ArcFace)'
        }
        benchmark.test_model(model_names[args.model], args.model)


if __name__ == "__main__":
    main()
