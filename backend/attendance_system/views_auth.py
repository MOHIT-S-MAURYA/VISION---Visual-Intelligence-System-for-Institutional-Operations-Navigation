from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from students.models import Teacher


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
            "department": teacher.department,
            "employee_id": teacher.employee_id,
        }
    except Teacher.DoesNotExist:
        response_data["teacher"] = None
    
    return Response(response_data)
