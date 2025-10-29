"""
Views for handling JWT-based admin login.
"""
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


@csrf_exempt
@require_http_methods(["POST"])
def jwt_admin_login(request):
    """
    Accept JWT token via POST and log the user into Django admin.
    """
    token = request.POST.get('token')
    
    if not token:
        return redirect('/admin/login/?error=no_token')
    
    try:
        # Validate and decode token
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        
        # Get user
        try:
            user = User.objects.get(pk=user_id)
            if user.is_active and (user.is_staff or user.is_superuser):
                # Log the user in
                login(request, user, backend='attendance_system.auth_backend.JWTAuthenticationBackend')
                # Store token in session for future requests
                request.session['jwt_token'] = token
                return redirect('/admin/')
            else:
                return redirect('/admin/login/?error=not_admin')
        except User.DoesNotExist:
            return redirect('/admin/login/?error=user_not_found')
    except (TokenError, KeyError):
        return redirect('/admin/login/?error=invalid_token')
