from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (StudentViewSet, SubjectViewSet, TeacherViewSet, 
                    TeacherSubjectAssignmentViewSet, DepartmentViewSet)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'teacher-assignments', TeacherSubjectAssignmentViewSet)
router.register(r'students', StudentViewSet)
router.register(r'subjects', SubjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
