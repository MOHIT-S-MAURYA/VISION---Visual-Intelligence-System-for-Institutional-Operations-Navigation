from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from .models import AttendanceSession, AttendanceRecord
from .serializers import AttendanceSessionSerializer, AttendanceRecordSerializer
from students.models import Student, Teacher
import requests
import os
from django.http import HttpResponse
import csv

class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer
    # Accept JSON for create/update plus multipart for recognize endpoints
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter sessions by teacher's department"""
        queryset = AttendanceSession.objects.all()
        
        # If user is authenticated and has a teacher profile, filter by department
        if self.request.user.is_authenticated:
            try:
                teacher = Teacher.objects.get(user=self.request.user)
                queryset = queryset.filter(department=teacher.department)
            except Teacher.DoesNotExist:
                # If no teacher profile, allow superusers to see all
                if not self.request.user.is_superuser:
                    queryset = queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """End an active attendance session"""
        session = self.get_object()
        session.is_active = False
        session.end_time = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        """Start (or restart) an attendance session"""
        session = self.get_object()
        session.is_active = True
        # If restarting, reset start_time to now and clear end_time
        session.start_time = timezone.now()
        session.end_time = None
        session.save()

        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_attendance(self, request, pk=None):
        """Mark attendance for a student in this session"""
        session = self.get_object()
        student_id = request.data.get('student_id')
        confidence = request.data.get('confidence', 0.0)
        
        try:
            student = Student.objects.get(id=student_id)
            record, created = AttendanceRecord.objects.get_or_create(
                session=session,
                student=student,
                defaults={'confidence': confidence}
            )
            
            if not created:
                record.confidence = max(record.confidence, confidence)
                record.save()
            
            serializer = AttendanceRecordSerializer(record)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def recognize(self, request, pk=None):
        """Recognize a face for this session and mark attendance if matched.

        Accepts a multipart form with a file field 'face_image'.
        """
        session = self.get_object()
        if not session.is_active:
            return Response({"error": "Session is not active"}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES.get('face_image')
        if not image_file:
            return Response({"error": "face_image file is required"}, status=status.HTTP_400_BAD_REQUEST)

        ai_url = os.environ.get('AI_SERVICE_URL', 'http://localhost:8001').rstrip('/')
        recognize_endpoint = f"{ai_url}/api/face/recognize"

        try:
            files = {"file": (image_file.name, image_file, image_file.content_type or 'image/jpeg')}
            resp = requests.post(recognize_endpoint, files=files, timeout=10)
        except requests.RequestException as e:
            return Response({"error": f"AI service unavailable: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if resp.status_code != 200:
            return Response({"error": f"AI service error: HTTP {resp.status_code}"}, status=status.HTTP_502_BAD_GATEWAY)

        payload = resp.json()
        if not payload.get('recognized'):
            return Response({"recognized": False, "message": payload.get('message', 'No match')}, status=status.HTTP_200_OK)

        student_id = payload.get('student_id')
        confidence = float(payload.get('confidence', 0.0))

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Recognized student not found in DB"}, status=status.HTTP_404_NOT_FOUND)

        record, created = AttendanceRecord.objects.get_or_create(
            session=session,
            student=student,
            defaults={"confidence": confidence, "status": "present"},
        )
        if not created:
            record.confidence = max(record.confidence, confidence)
            record.status = 'present'
            record.save()

        rec_serializer = AttendanceRecordSerializer(record)
        return Response({
            "recognized": True,
            "student": {
                "id": student.id,
                "roll_number": student.roll_number,
                "full_name": student.full_name,
                "department": student.department,
                "class_year": student.class_year,
            },
            "confidence": confidence,
            "attendance_record": rec_serializer.data,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def recognize_multi(self, request, pk=None):
        """Recognize using multiple frames (files as 'face_images[]')."""
        session = self.get_object()
        if not session.is_active:
            return Response({"error": "Session is not active"}, status=status.HTTP_400_BAD_REQUEST)

        images = request.FILES.getlist('face_images')
        if not images:
            return Response({"error": "face_images[] files are required"}, status=status.HTTP_400_BAD_REQUEST)

        ai_url = os.environ.get('AI_SERVICE_URL', 'http://localhost:8001').rstrip('/')
        endpoint = f"{ai_url}/api/face/recognize_multi"

        files = [('files', (img.name, img, getattr(img, 'content_type', 'image/jpeg'))) for img in images]
        try:
            resp = requests.post(endpoint, files=files, timeout=20)
        except requests.RequestException as e:
            return Response({"error": f"AI service unavailable: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if resp.status_code != 200:
            return Response({"error": f"AI service error: HTTP {resp.status_code}"}, status=status.HTTP_502_BAD_GATEWAY)

        payload = resp.json()
        if not payload.get('recognized'):
            return Response({"recognized": False, "message": payload.get('message', 'No match')}, status=status.HTTP_200_OK)

        student_id = payload.get('student_id')
        confidence = float(payload.get('confidence', 0.0))

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Recognized student not found in DB"}, status=status.HTTP_404_NOT_FOUND)

        record, created = AttendanceRecord.objects.get_or_create(
            session=session,
            student=student,
            defaults={"confidence": confidence, "status": "present"},
        )
        if not created:
            record.confidence = max(record.confidence, confidence)
            record.status = 'present'
            record.save()

        rec_serializer = AttendanceRecordSerializer(record)
        return Response({
            "recognized": True,
            "student": {
                "id": student.id,
                "roll_number": student.roll_number,
                "full_name": student.full_name,
                "department": student.department,
                "class_year": student.class_year,
            },
            "confidence": confidence,
            "attendance_record": rec_serializer.data,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def export_csv(self, request, pk=None):
        """Export session attendance as CSV: Roll No, Name, Status, Time, Confidence"""
        session = self.get_object()

        response = HttpResponse(content_type='text/csv')
        filename = f"attendance_session_{session.id}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(["Roll No", "Name", "Status", "Time", "Confidence"]) 

        for rec in session.records.select_related('student').all():
            # Convert timestamp to local timezone (IST as configured in settings)
            local_time = timezone.localtime(rec.marked_at)
            writer.writerow([
                rec.student.roll_number,
                rec.student.full_name,
                rec.status,
                local_time.strftime('%Y-%m-%d %H:%M:%S'),
                f"{rec.confidence:.4f}",
            ])

        return response

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def recognize_frame(self, request, pk=None):
        """Detect multiple faces in a single frame and mark attendance for all recognized.

        Accepts multipart form with 'frame' file field.
        Returns: { image: {width,height}, faces: [{bbox, recognized, student, similarity, confidence}] }
        """
        session = self.get_object()
        if not session.is_active:
            return Response({"error": "Session is not active"}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES.get('frame') or request.FILES.get('file')
        if not image_file:
            return Response({"error": "frame image is required"}, status=status.HTTP_400_BAD_REQUEST)

        ai_url = os.environ.get('AI_SERVICE_URL', 'http://localhost:8001').rstrip('/')
        endpoint = f"{ai_url}/api/face/recognize_frame"
        try:
            files = {"file": (image_file.name, image_file, getattr(image_file, 'content_type', 'image/jpeg'))}
            resp = requests.post(endpoint, files=files, timeout=20)
        except requests.RequestException as e:
            return Response({"error": f"AI service unavailable: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if resp.status_code != 200:
            return Response({"error": f"AI service error: HTTP {resp.status_code}"}, status=status.HTTP_502_BAD_GATEWAY)

        payload = resp.json()
        faces = payload.get('faces', [])
        image_meta = payload.get('image', {})

        enriched = []
        for f in faces:
            if f.get('recognized') and f.get('student_id'):
                try:
                    student = Student.objects.get(id=f['student_id'])
                except Student.DoesNotExist:
                    student = None
                if student:
                    # Use similarity (raw cosine score) not confidence (rescaled)
                    # similarity >= 0.7 means 70%+ match
                    similarity = float(f.get('similarity') or 0.0)
                    rec, created = AttendanceRecord.objects.get_or_create(
                        session=session,
                        student=student,
                        defaults={"confidence": similarity, "status": "present"}
                    )
                    if not created:
                        # update confidence if current similarity is higher
                        if similarity > (rec.confidence or 0.0):
                            rec.confidence = similarity
                        rec.status = 'present'
                        rec.save()
                    enriched.append({
                        "bbox": f.get('bbox'),
                        "recognized": True,
                        "student": {
                            "id": student.id,
                            "roll_number": student.roll_number,
                            "full_name": student.full_name,
                            "department": student.department,
                            "class_year": student.class_year,
                        },
                        "similarity": f.get('similarity'),
                        "confidence": f.get('confidence'),
                    })
                else:
                    enriched.append({
                        "bbox": f.get('bbox'),
                        "recognized": False,
                        "student": None,
                        "similarity": f.get('similarity'),
                        "confidence": f.get('confidence'),
                    })
            else:
                enriched.append({
                    "bbox": f.get('bbox'),
                    "recognized": False,
                    "student": None,
                    "similarity": f.get('similarity'),
                    "confidence": f.get('confidence'),
                })

        return Response({"image": image_meta, "faces": enriched})
