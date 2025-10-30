from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Subject, Teacher, TeacherSubjectAssignment, Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class TeacherSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False)
    
    class Meta:
        model = Teacher
        fields = ['id', 'username', 'password', 'email', 'full_name', 
                  'employee_id', 'phone', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        # Extract User fields
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email', '')
        
        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        
        # Create Teacher profile
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher


class SubjectSerializer(serializers.ModelSerializer):
    department_code = serializers.CharField(source='department.code', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'department', 'department_code', 'department_name', 
                  'class_year', 'subject_name', 'subject_code', 'credits', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TeacherSubjectAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    department_code = serializers.CharField(source='subject.department.code', read_only=True)
    class_year = serializers.CharField(source='subject.class_year', read_only=True)
    
    class Meta:
        model = TeacherSubjectAssignment
        fields = ['id', 'teacher', 'teacher_name', 'subject', 'subject_name', 
                  'subject_code', 'department_code', 'class_year', 'academic_year',
                  'assigned_date', 'is_active', 'notes']
        read_only_fields = ['assigned_date']


class StudentSerializer(serializers.ModelSerializer):
    department_code = serializers.CharField(source='department.code', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'roll_number', 'full_name', 'department', 'department_code', 
                  'department_name', 'class_year', 'email', 'phone', 'face_embedding_id', 
                  'face_image', 'is_active']
