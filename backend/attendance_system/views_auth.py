from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from students.models import Teacher, TeacherSubjectAssignment


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    response_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email or "",
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }
    
    # Add teacher profile info if exists
    try:
        teacher = Teacher.objects.get(user=user)
        response_data["teacher"] = {
            "id": teacher.id,
            "full_name": teacher.full_name,
            "employee_id": teacher.employee_id,
            "email": teacher.email,
            "phone": teacher.phone,
        }
        
        # Include teacher's subject assignments
        assignments = TeacherSubjectAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).select_related('subject', 'subject__department')
        
        response_data["teacher"]["assignments"] = [
            {
                "id": assignment.id,
                "subject": {
                    "id": assignment.subject.id,
                    "name": assignment.subject.subject_name,
                    "code": assignment.subject.subject_code,
                    "class_year": assignment.subject.class_year,
                },
                "department": {
                    "id": assignment.subject.department.id,
                    "code": assignment.subject.department.code,
                    "name": assignment.subject.department.name,
                    "degree_type": assignment.subject.department.degree_type,
                },
                "academic_year": assignment.academic_year,
            }
            for assignment in assignments
        ]
    except Teacher.DoesNotExist:
        response_data["teacher"] = None
    
    return Response(response_data)
