from django.db import models

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
