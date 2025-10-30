#!/usr/bin/env python3
"""
Quick test to verify roll number auto-generation
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/mohitmaurya/dev/vision/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from students.models import Student, Department

print("Testing Roll Number Auto-Generation")
print("=" * 50)

# Get or create a test department
dept, created = Department.objects.get_or_create(
    code='TEST',
    defaults={
        'name': 'Test Department',
        'degree_type': 'UG',
        'duration_years': 4
    }
)

print(f"\nDepartment: {dept.code} - {dept.name}")
print(f"{'Created new' if created else 'Using existing'} department")

# Test 1: Create student without roll number
print("\n\nTest 1: Creating student WITHOUT roll number")
try:
    student1 = Student.objects.create(
        full_name='Test Student 1',
        department=dept,
        class_year='First Year'
    )
    print(f"✓ Success! Auto-generated roll number: {student1.roll_number}")
    print(f"  Student ID: {student1.id}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2: Create another student without roll number (should increment)
print("\n\nTest 2: Creating another student WITHOUT roll number")
try:
    student2 = Student.objects.create(
        full_name='Test Student 2',
        department=dept,
        class_year='Second Year'
    )
    print(f"✓ Success! Auto-generated roll number: {student2.roll_number}")
    print(f"  Student ID: {student2.id}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3: Create student with custom roll number
print("\n\nTest 3: Creating student WITH custom roll number")
try:
    student3 = Student.objects.create(
        roll_number='CUSTOM-001',
        full_name='Test Student 3',
        department=dept,
        class_year='Third Year'
    )
    print(f"✓ Success! Used custom roll number: {student3.roll_number}")
    print(f"  Student ID: {student3.id}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Show all test students
print("\n\nAll TEST department students:")
print("-" * 50)
test_students = Student.objects.filter(department=dept).order_by('id')
for s in test_students:
    print(f"  {s.roll_number:20s} | {s.full_name:20s} | {s.class_year}")

# Cleanup
print("\n\nCleaning up test data...")
test_students.delete()
if created:
    dept.delete()
print("✓ Cleanup complete")

print("\n" + "=" * 50)
print("All tests completed!")
