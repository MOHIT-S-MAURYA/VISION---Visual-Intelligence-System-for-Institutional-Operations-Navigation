from django.db import models
from students.models import Student

class AttendanceSession(models.Model):
    """Attendance session for a specific class and subject"""
    department = models.CharField(max_length=100)
    class_year = models.CharField(max_length=50)
    subject = models.CharField(max_length=200)
    session_date = models.DateField(auto_now_add=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.department} - {self.class_year} - {self.subject} - {self.session_date}"

class AttendanceRecord(models.Model):
    """Individual attendance record for a student in a session"""
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marked_at = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, default='present')

    class Meta:
        unique_together = ['session', 'student']
        ordering = ['marked_at']

    def __str__(self):
        return f"{self.student.roll_number} - {self.session} - {self.status}"
