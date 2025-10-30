"""
Real-World Face Recognition Model Test

Tests models on actual student face images from the registration database.
"""

import os
import sys
import time
import json
import pickle
from pathlib import Path
import numpy as np
import cv2
from typing import Dict, List, Tuple

# Import InsightFace models
from insightface.app import FaceAnalysis

# Import benchmarking
from model_benchmark import FaceRecognitionBenchmark, BenchmarkResult


def extract_test_images_from_storage(storage_dir: str = "./face_storage", output_dir: str = "./test_data"):
    """
    Extract test images from face storage directory to create proper test dataset.
    
    Storage structure:
      face_storage/
        student_1/
          face_0.jpg
          face_1.jpg
    """
    storage_path = Path(storage_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    if not storage_path.exists():
        print(f"❌ Storage directory not found: {storage_dir}")
        return None
    
    print(f"\n📂 Extracting test images from: {storage_dir}")
    
    student_count = 0
    image_count = 0
    
    for student_dir in storage_path.iterdir():
        if not student_dir.is_dir():
            continue
        
        student_id = student_dir.name
        test_student_dir = output_path / student_id
        test_student_dir.mkdir(exist_ok=True)
        
        # Copy first 3 images as test set
        for idx, img_path in enumerate(student_dir.glob("*.jpg")):
            if idx >= 3:  # Only use first 3 images per student
                break
            
            # Copy to test directory
            test_img_path = test_student_dir / f"test_{idx}.jpg"
            import shutil
            shutil.copy(str(img_path), str(test_img_path))
            image_count += 1
        
        if image_count > 0:
            student_count += 1
    
    print(f"✓ Extracted {image_count} test images from {student_count} students")
    print(f"✓ Test data saved to: {output_path}")
    
    return str(output_path)


def run_production_test():
    """
    Run comprehensive test on real production data.
    """
    print("="*70)
    print("REAL-WORLD FACE RECOGNITION MODEL TEST")
    print("="*70)
    
    # Step 1: Extract test images from storage
    test_data_dir = extract_test_images_from_storage()
    
    if not test_data_dir or not os.path.exists(test_data_dir):
        print("\n⚠️  No test data available. Please register some students first.")
        print("   Run the registration system and register at least 2-3 students.")
        return
    
    # Step 2: Initialize benchmark
    benchmark = FaceRecognitionBenchmark(
        test_data_dir=test_data_dir,
        output_dir="./benchmark_results"
    )
    
    # Step 3: Load test data
    benchmark.load_test_data()
    
    if len(benchmark.test_images) < 5:
        print(f"\n⚠️  Only {len(benchmark.test_images)} test images available.")
        print("   For accurate benchmarking, please register more students.")
        print("   Continuing with available data...")
    
    # Step 4: Initialize models
    benchmark.initialize_models()
    
    # Step 5: Run benchmarks
    results = benchmark.run_all_benchmarks()
    
    # Step 6: Generate report
    benchmark.generate_report()
    
    # Step 7: Show recommendations
    print("\n" + "="*70)
    print("PRODUCTION DEPLOYMENT RECOMMENDATIONS")
    print("="*70)
    
    if results:
        best_model = results[0]
        print(f"\n✅ RECOMMENDED MODEL: {best_model.model_name.upper()}")
        print(f"   {benchmark.models[best_model.model_name]['description']}")
        print(f"   Overall Score: {best_model.overall_score}/100")
        print(f"   Detection Accuracy: {best_model.detection_accuracy}%")
        print(f"   Speed: {best_model.detection_time_avg_ms:.2f}ms per face")
        
        # Compare with current production
        current_prod = next((r for r in results if r.model_name == 'insightface_buffalo_l'), None)
        
        if current_prod and best_model.model_name != 'insightface_buffalo_l':
            print(f"\n📊 COMPARISON WITH CURRENT PRODUCTION:")
            print(f"   Current (buffalo_l): {current_prod.overall_score}/100, {current_prod.detection_time_avg_ms:.2f}ms")
            print(f"   Recommended ({best_model.model_name}): {best_model.overall_score}/100, {best_model.detection_time_avg_ms:.2f}ms")
            
            improvement = best_model.overall_score - current_prod.overall_score
            if improvement > 5:
                print(f"\n   🎯 SIGNIFICANT IMPROVEMENT: +{improvement:.1f} points!")
                print(f"   ✅ Consider upgrading to {best_model.model_name}")
            else:
                print(f"\n   ℹ️  Minor difference: +{improvement:.1f} points")
                print(f"   ✅ Current model (buffalo_l) is performing well")
        else:
            print(f"\n✅ Current production model is optimal!")
    
    print("\n" + "="*70)


def quick_model_comparison():
    """
    Quick comparison of InsightFace model variants on a single test image.
    """
    print("\n" + "="*70)
    print("QUICK MODEL COMPARISON")
    print("="*70)
    
    # Load a test image from storage
    storage_dir = Path("./face_storage")
    test_image = None
    
    if storage_dir.exists():
        for student_dir in storage_dir.iterdir():
            if student_dir.is_dir():
                for img_path in student_dir.glob("*.jpg"):
                    test_image = cv2.imread(str(img_path))
                    if test_image is not None:
                        print(f"\n✓ Loaded test image: {img_path}")
                        break
                if test_image is not None:
                    break
    
    if test_image is None:
        print("\n⚠️  No test images available. Creating synthetic face...")
        # Create a simple synthetic face (better than pure noise)
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 200
        # Draw a face-like oval
        cv2.ellipse(test_image, (320, 240), (120, 160), 0, 0, 360, (180, 150, 120), -1)
        # Draw eyes
        cv2.circle(test_image, (270, 200), 15, (50, 50, 50), -1)
        cv2.circle(test_image, (370, 200), 15, (50, 50, 50), -1)
    
    models = {
        'buffalo_l': 'Current Production (RetinaFace + ArcFace)',
        'buffalo_sc': 'Fast SCRFD + ArcFace',
    }
    
    print("\n" + "-"*70)
    print("Testing models on sample image...")
    print("-"*70)
    
    for model_name, description in models.items():
        try:
            start_time = time.time()
            app = FaceAnalysis(name=model_name, providers=['CPUExecutionProvider'])
            app.prepare(ctx_id=-1, det_size=(640, 640))
            load_time = (time.time() - start_time) * 1000
            
            start_time = time.time()
            faces = app.get(test_image)
            detection_time = (time.time() - start_time) * 1000
            
            print(f"\n{model_name.upper()}: {description}")
            print(f"  Load Time: {load_time:.2f}ms")
            print(f"  Detection Time: {detection_time:.2f}ms")
            print(f"  Faces Detected: {len(faces)}")
            
            if faces:
                face = faces[0]
                print(f"  Face Confidence: {face.det_score:.3f}")
                print(f"  Embedding Norm: {np.linalg.norm(face.normed_embedding):.3f}")
        
        except Exception as e:
            print(f"\n{model_name.upper()}: ❌ Error - {e}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Face Recognition Model Testing')
    parser.add_argument('--mode', choices=['full', 'quick'], default='full',
                       help='Test mode: full benchmark or quick comparison')
    
    args = parser.parse_args()
    
    if args.mode == 'full':
        run_production_test()
    else:
        quick_model_comparison()
