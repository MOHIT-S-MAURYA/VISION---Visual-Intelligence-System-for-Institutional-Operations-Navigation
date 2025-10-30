from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.files.base import ContentFile
from django.db.models import Q
import requests
import base64
import io
import os
from .models import Student, Subject, Teacher, TeacherSubjectAssignment, Department
from .serializers import (StudentSerializer, SubjectSerializer, TeacherSerializer, 
                          TeacherSubjectAssignmentSerializer, DepartmentSerializer)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing departments"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Department.objects.filter(is_active=True)
        
        # Filter by degree type if specified
        degree_type = self.request.query_params.get('degree_type', None)
        if degree_type:
            queryset = queryset.filter(degree_type=degree_type)
        
        return queryset


class TeacherViewSet(viewsets.ModelViewSet):
    """ViewSet for teacher registration and management"""
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    
    def get_permissions(self):
        # Allow registration without authentication
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current teacher's profile with subject assignments"""
        try:
            teacher = Teacher.objects.get(user=request.user)
            serializer = self.get_serializer(teacher)
            
            # Get teacher's subject assignments
            assignments = TeacherSubjectAssignment.objects.filter(
                teacher=teacher, 
                is_active=True
            ).select_related('subject')
            
            assignment_data = TeacherSubjectAssignmentSerializer(assignments, many=True).data
            
            response_data = serializer.data
            response_data['assignments'] = assignment_data
            
            return Response(response_data)
        except Teacher.DoesNotExist:
            return Response(
                {'error': 'Teacher profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class TeacherSubjectAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing teacher-subject assignments"""
    queryset = TeacherSubjectAssignment.objects.all()
    serializer_class = TeacherSubjectAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter assignments - teachers see only their own"""
        queryset = TeacherSubjectAssignment.objects.all()
        
        if self.request.user.is_authenticated:
            try:
                teacher = Teacher.objects.get(user=self.request.user)
                if not self.request.user.is_superuser:
                    queryset = queryset.filter(teacher=teacher, is_active=True)
            except Teacher.DoesNotExist:
                if not self.request.user.is_superuser:
                    queryset = queryset.none()
        
        return queryset.select_related('teacher', 'subject', 'subject__department')
    
    @action(detail=False, methods=['get'])
    def my_teaching_options(self, request):
        """Get unique departments and class years for the logged-in teacher"""
        try:
            teacher = Teacher.objects.get(user=request.user)
            
            # Get all active assignments for this teacher
            assignments = TeacherSubjectAssignment.objects.filter(
                teacher=teacher,
                is_active=True
            ).select_related('subject__department')
            
            # Extract unique department-year combinations
            dept_year_map = {}
            for assignment in assignments:
                dept = assignment.subject.department
                year = assignment.subject.class_year
                
                if dept.id not in dept_year_map:
                    dept_year_map[dept.id] = {
                        'id': dept.id,
                        'code': dept.code,
                        'name': dept.name,
                        'years': set()
                    }
                dept_year_map[dept.id]['years'].add(year)
            
            # Convert to list format
            departments = []
            for dept_data in dept_year_map.values():
                departments.append({
                    'id': dept_data['id'],
                    'code': dept_data['code'],
                    'name': dept_data['name'],
                    'years': sorted(list(dept_data['years']))
                })
            
            return Response({
                'departments': departments,
                'teacher_id': teacher.id,
                'teacher_name': teacher.full_name
            })
            
        except Teacher.DoesNotExist:
            return Response(
                {'error': 'Teacher profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter students by teacher's assigned classes"""
        queryset = Student.objects.all()
        
        # If user is authenticated and has a teacher profile, filter by assignments
        if self.request.user.is_authenticated:
            try:
                teacher = Teacher.objects.get(user=self.request.user)
                if not self.request.user.is_superuser:
                    # Get all department-year combinations this teacher teaches
                    assignments = TeacherSubjectAssignment.objects.filter(
                        teacher=teacher,
                        is_active=True
                    ).values_list('subject__department', 'subject__class_year').distinct()
                    
                    if not assignments:
                        return queryset.none()
                    
                    # Build Q objects for OR filtering
                    q_objects = Q()
                    for dept, year in assignments:
                        q_objects |= Q(department=dept, class_year=year)
                    
                    queryset = queryset.filter(q_objects)
            except Teacher.DoesNotExist:
                if not self.request.user.is_superuser:
                    queryset = queryset.none()
        
        return queryset
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def register_with_face(self, request):
        """Register a new student with face capture (roll_number is optional - auto-generated if not provided)"""
        try:
            # Extract student data
            student_data = {
                'roll_number': request.data.get('roll_number', ''),  # Optional now
                'full_name': request.data.get('full_name'),
                'department': request.data.get('department'),
                'class_year': request.data.get('class_year'),
            }
            # Basic validation - roll_number is now optional
            required_fields = ['full_name', 'department', 'class_year']
            missing = [k for k in required_fields if not student_data.get(k)]
            if missing:
                return Response(
                    {'error': f"Missing required fields: {', '.join(missing)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get face image
            face_image = request.FILES.get('face_image')
            
            if not face_image:
                return Response(
                    {'error': 'Face image is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create student first (handle duplicate roll_number)
            serializer = self.get_serializer(data=student_data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                # Provide clearer message if duplicate roll number constraint fails
                if 'roll_number' in serializer.errors:
                    return Response(
                        {'error': 'Roll number already exists'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                raise
            student = serializer.save()
            
            # Save face image
            student.face_image.save(
                f"{student.roll_number}_face.jpg",
                face_image,
                save=True
            )
            
            # Send to AI service for face registration
            try:
                base_ai = os.environ.get('AI_SERVICE_URL', 'http://localhost:8001').rstrip('/')
                ai_service_url = f"{base_ai}/api/face/register"
                
                # Prepare file for AI service
                face_image.seek(0)
                files = {'file': (face_image.name, face_image, face_image.content_type)}
                data = {'student_id': str(student.id)}
                
                # Try with a small retry loop
                last_exc = None
                for attempt in range(2):
                    try:
                        response = requests.post(ai_service_url, files=files, data=data, timeout=10)
                        break
                    except requests.exceptions.RequestException as ex:
                        last_exc = ex
                        if attempt == 0:
                            continue
                        raise
                
                if response.status_code == 200:
                    ai_response = response.json()
                    student.face_embedding_id = ai_response.get('embedding_id', str(student.id))
                    student.save()
                else:
                    # If AI service fails, still keep the student but log the error
                    student.face_embedding_id = f"pending_{student.id}"
                    student.save()
                    
            except requests.exceptions.RequestException as e:
                # AI service not available, save with pending status
                student.face_embedding_id = f"pending_{student.id}"
                student.save()
            
            return Response(
                {
                    'status': 'success',
                    'message': 'Student registered successfully',
                    'student': StudentSerializer(student).data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def register_with_face_multi(self, request):
        """Register a new student using multiple frames for robust embedding (roll_number is optional - auto-generated if not provided)."""
        try:
            # Extract student data
            student_data = {
                'roll_number': request.data.get('roll_number', ''),  # Optional now
                'full_name': request.data.get('full_name'),
                'department': request.data.get('department'),
                'class_year': request.data.get('class_year'),
            }
            
            # Validate required fields - roll_number is now optional
            required_fields = ['full_name', 'department', 'class_year']
            missing = [k for k in required_fields if not student_data.get(k)]
            if missing:
                return Response(
                    {'error': f"Missing required fields: {', '.join(missing)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get face images
            images = request.FILES.getlist('face_images')
            if not images or len(images) < 3:
                return Response(
                    {'error': f'At least 3 face images required for robust registration. Received: {len(images)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(images) > 15:
                return Response(
                    {'error': 'Maximum 15 images allowed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate serializer
            serializer = self.get_serializer(data=student_data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                if 'roll_number' in serializer.errors:
                    return Response(
                        {'error': 'Roll number already exists'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create student record
            student = serializer.save()

            # Save best quality image as reference
            best_image = images[len(images) // 2]  # Pick middle frame as reference
            student.face_image.save(f"{student.roll_number}_face.jpg", best_image, save=True)

            # Send frames to AI service for FAISS registration
            base_ai = os.environ.get('AI_SERVICE_URL', 'http://localhost:8001').rstrip('/')
            ai_service_url = f"{base_ai}/api/face/register_multi"
            
            # Prepare files for upload (reset file pointers)
            files = []
            for idx, img in enumerate(images):
                img.seek(0)
                files.append(('files', (f'frame_{idx}.jpg', img, getattr(img, 'content_type', 'image/jpeg'))))
            
            data = {'student_id': str(student.id)}
            
            try:
                resp = requests.post(ai_service_url, files=files, data=data, timeout=30)
                
                if resp.status_code == 200:
                    ai_response = resp.json()
                    student.face_embedding_id = ai_response.get('embedding_id', str(student.id))
                    student.save()
                    
                    return Response(
                        {
                            'status': 'success', 
                            'message': f'Student registered successfully with {len(images)} frames',
                            'student': StudentSerializer(student).data,
                            'frames_processed': ai_response.get('frames', len(images)),
                            'embedding_id': student.face_embedding_id
                        },
                        status=status.HTTP_201_CREATED
                    )
                else:
                    # AI service returned error
                    error_detail = resp.json() if resp.headers.get('content-type') == 'application/json' else resp.text
                    student.delete()  # Rollback student creation
                    return Response(
                        {
                            'error': f'Face registration failed: {error_detail}',
                            'detail': 'AI service could not process face images. Please ensure face is clearly visible.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except requests.RequestException as e:
                # AI service not reachable
                student.delete()  # Rollback student creation
                return Response(
                    {
                        'error': 'AI service unavailable',
                        'detail': f'Could not connect to face recognition service: {str(e)}'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        except Exception as e:
            return Response(
                {'error': f'Registration failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """Get students by department and class"""
        department = request.query_params.get('department')
        class_year = request.query_params.get('class_year')
        
        queryset = self.queryset
        if department:
            queryset = queryset.filter(department=department)
        if class_year:
            queryset = queryset.filter(class_year=class_year)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subjects"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
    def get_queryset(self):
        """Filter subjects by teacher's assignments"""
        queryset = Subject.objects.select_related('department').filter(is_active=True)
        
        # If user is authenticated and has a teacher profile, filter by their assignments
        if self.request.user.is_authenticated:
            try:
                teacher = Teacher.objects.get(user=self.request.user)
                if not self.request.user.is_superuser:
                    # Get subjects teacher is assigned to
                    assigned_subject_ids = TeacherSubjectAssignment.objects.filter(
                        teacher=teacher,
                        is_active=True
                    ).values_list('subject_id', flat=True)
                    
                    queryset = queryset.filter(id__in=assigned_subject_ids)
            except Teacher.DoesNotExist:
                if not self.request.user.is_superuser:
                    queryset = queryset.none()
        
        # Additional filtering by query parameters
        department_id = self.request.query_params.get('department', None)
        class_year = self.request.query_params.get('class_year', None)
        
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if class_year:
            queryset = queryset.filter(class_year=class_year)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create subjects from a list"""
        subjects_data = request.data.get('subjects', [])
        if not subjects_data:
            return Response(
                {'error': 'No subjects provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created = []
        errors = []
        
        for subject_data in subjects_data:
            serializer = self.get_serializer(data=subject_data)
            if serializer.is_valid():
                try:
                    serializer.save()
                    created.append(serializer.data)
                except Exception as e:
                    errors.append({
                        'data': subject_data,
                        'error': str(e)
                    })
            else:
                errors.append({
                    'data': subject_data,
                    'error': serializer.errors
                })
        
        return Response({
            'created': len(created),
            'failed': len(errors),
            'created_subjects': created,
            'errors': errors
        })
