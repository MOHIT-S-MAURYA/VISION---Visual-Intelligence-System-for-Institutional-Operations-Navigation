from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    """Department model for managing academic departments"""
    code = models.CharField(max_length=20, unique=True)  # e.g., 'CSE', 'ECE', 'MCA'
    name = models.CharField(max_length=200)  # e.g., 'Computer Science Engineering'
    degree_type = models.CharField(max_length=20, choices=[
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
    ])
    duration_years = models.IntegerField(default=4)  # 4 for UG, 2 for PG
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        
    def __str__(self):
        return f"{self.code} - {self.name}"


class Teacher(models.Model):
    """Teacher profile model linked to Django User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    full_name = models.CharField(max_length=200)
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name}"


class Subject(models.Model):
    """Subject model for storing subjects by department and year"""
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects', null=True)
    class_year = models.CharField(max_length=50)  # e.g., 'First Year', 'Second Year'
    subject_name = models.CharField(max_length=200)
    subject_code = models.CharField(max_length=50, blank=True, null=True)
    credits = models.IntegerField(default=3, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department', 'class_year', 'subject_name']
        unique_together = ['department', 'class_year', 'subject_name']

    def __str__(self):
        return f"{self.department.code} - {self.class_year} - {self.subject_name}"


class TeacherSubjectAssignment(models.Model):
    """Assignment of teachers to specific subjects and classes"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='subject_assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_assignments')
    academic_year = models.CharField(max_length=20, blank=True, null=True)  # e.g., '2024-25'
    assigned_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)  # Any additional notes
    
    class Meta:
        ordering = ['teacher', 'subject']
        unique_together = ['teacher', 'subject', 'academic_year']
    
    def __str__(self):
        return f"{self.teacher.full_name} → {self.subject.subject_name} ({self.subject.department.code} {self.subject.class_year})"


class Student(models.Model):
    """Student model"""
    roll_number = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='students', null=True)
    class_year = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    face_embedding_id = models.CharField(max_length=100, null=True, blank=True)
    face_image = models.ImageField(upload_to='student_faces/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
