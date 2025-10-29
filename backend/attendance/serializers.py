from rest_framework import serializers
from .models import AttendanceSession, AttendanceRecord
from students.serializers import StudentSerializer

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

class AttendanceSessionSerializer(serializers.ModelSerializer):
    records = AttendanceRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = AttendanceSession
        fields = '__all__'
