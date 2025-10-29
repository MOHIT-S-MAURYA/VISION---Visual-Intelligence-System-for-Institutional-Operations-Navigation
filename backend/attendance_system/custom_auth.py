"""
Custom TokenObtainPairView that accepts username OR employee_id for login.
"""
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from students.models import Teacher

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer that allows login with username OR employee_id.
    """
    
    def validate(self, attrs):
        # Get the username (which could be username or employee_id)
        username_or_empid = attrs.get('username')
        password = attrs.get('password')
        
        # Try to find user by username first
        user = None
        try:
            user = User.objects.get(username=username_or_empid)
        except User.DoesNotExist:
            # If not found by username, try by employee_id
            try:
                teacher = Teacher.objects.get(employee_id=username_or_empid)
                user = teacher.user
            except Teacher.DoesNotExist:
                pass
        
        if user is None:
            # Let the parent class handle the error
            return super().validate(attrs)
        
        # Now validate the password with the found user
        if user.check_password(password):
            # Temporarily set the username in attrs to the actual username
            attrs['username'] = user.username
            return super().validate(attrs)
        else:
            # Let the parent class handle the error
            return super().validate(attrs)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that uses CustomTokenObtainPairSerializer.
    """
    serializer_class = CustomTokenObtainPairSerializer
