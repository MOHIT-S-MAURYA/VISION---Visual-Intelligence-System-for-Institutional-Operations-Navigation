from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    """Teacher profile model linked to Django User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.department})"


class Student(models.Model):
    """Student model for storing student information"""
    roll_number = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    class_year = models.CharField(max_length=50)
    face_embedding_id = models.CharField(max_length=100, blank=True, null=True)
    face_image = models.ImageField(upload_to='student_faces/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['roll_number']

    def __str__(self):
        return f"{self.roll_number} - {self.full_name}"


class Subject(models.Model):
    """Subject model for storing subjects by department and year"""
    department = models.CharField(max_length=100)
    class_year = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=200)
    subject_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department', 'class_year', 'subject_name']
        unique_together = ['department', 'class_year', 'subject_name']

    def __str__(self):
        return f"{self.department} - {self.class_year} - {self.subject_name}"
