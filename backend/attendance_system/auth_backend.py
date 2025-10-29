"""
Custom authentication backend to allow JWT token-based login to Django admin.
This allows users who are already logged in via the React frontend (with JWT)
to access Django admin without re-entering credentials.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


class JWTAuthenticationBackend(ModelBackend):
    """
    Custom authentication backend that checks for JWT token in session.
    Falls back to normal username/password authentication.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # First try normal authentication
        if username and password:
            return super().authenticate(request, username, password, **kwargs)
        
        # If no username/password, check for JWT token in session
        if request and hasattr(request, 'session'):
            token = request.session.get('jwt_token')
            if token:
                try:
                    # Validate and decode token
                    access_token = AccessToken(token)
                    user_id = access_token['user_id']
                    
                    # Get user
                    try:
                        user = User.objects.get(pk=user_id)
                        if user.is_active:
                            return user
                    except User.DoesNotExist:
                        pass
                except (TokenError, KeyError):
                    pass
        
        return None
