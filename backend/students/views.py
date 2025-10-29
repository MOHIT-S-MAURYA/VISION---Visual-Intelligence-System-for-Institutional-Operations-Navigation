from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile
import requests
import base64
import io
import os
from .models import Student
from .serializers import StudentSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def register_with_face(self, request):
        """Register a new student with face capture"""
        try:
            # Extract student data
            student_data = {
                'roll_number': request.data.get('roll_number'),
                'full_name': request.data.get('full_name'),
                'department': request.data.get('department'),
                'class_year': request.data.get('class_year'),
            }
            # Basic validation
            missing = [k for k, v in student_data.items() if not v]
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
        """Register a new student using multiple frames for robust embedding."""
        try:
            # Extract student data
            student_data = {
                'roll_number': request.data.get('roll_number'),
                'full_name': request.data.get('full_name'),
                'department': request.data.get('department'),
                'class_year': request.data.get('class_year'),
            }
            missing = [k for k, v in student_data.items() if not v]
            if missing:
                return Response({'error': f"Missing required fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

            images = request.FILES.getlist('face_images')
            if not images:
                return Response({'error': 'At least one face image is required (face_images[])'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=student_data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception:
                if 'roll_number' in serializer.errors:
                    return Response({'error': 'Roll number already exists'}, status=status.HTTP_400_BAD_REQUEST)
                raise
            student = serializer.save()

            # Save first image as reference
            ref = images[0]
            student.face_image.save(f"{student.roll_number}_face.jpg", ref, save=True)

            # Send frames to AI service
            base_ai = os.environ.get('AI_SERVICE_URL', 'http://localhost:8001').rstrip('/')
            ai_service_url = f"{base_ai}/api/face/register_multi"
            files = [('files', (img.name, img, getattr(img, 'content_type', 'image/jpeg'))) for img in images]
            data = {'student_id': str(student.id)}
            try:
                resp = requests.post(ai_service_url, files=files, data=data, timeout=30)
                if resp.status_code == 200:
                    ai_response = resp.json()
                    student.face_embedding_id = ai_response.get('embedding_id', str(student.id))
                    student.save()
                else:
                    student.face_embedding_id = f"pending_{student.id}"
                    student.save()
            except requests.RequestException:
                student.face_embedding_id = f"pending_{student.id}"
                student.save()

            return Response(
                {'status': 'success', 'message': 'Student registered successfully (multi-frame)', 'student': StudentSerializer(student).data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
