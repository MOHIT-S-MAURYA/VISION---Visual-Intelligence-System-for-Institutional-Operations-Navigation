from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Subject, Teacher


class TeacherSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    
    class Meta:
        model = Teacher
        fields = ['id', 'username', 'password', 'email', 'full_name', 'department', 
                  'employee_id', 'created_at', 'updated_at']
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


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
