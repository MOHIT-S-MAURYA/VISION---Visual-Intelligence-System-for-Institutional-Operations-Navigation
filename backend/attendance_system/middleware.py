"""
Middleware to transfer JWT token from Authorization header or cookie to session.
This allows Django admin to automatically authenticate users who are logged in via React.
"""


class JWTToSessionMiddleware:
    """
    Middleware that extracts JWT token from request and stores it in session.
    This enables Django admin to use JWT authentication.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if accessing admin
        if request.path.startswith('/admin'):
            # Try to get token from Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                request.session['jwt_token'] = token
            
            # Or from cookie (if React stores it there)
            elif 'teacher_token' in request.COOKIES:
                token = request.COOKIES.get('teacher_token')
                request.session['jwt_token'] = token
        
        response = self.get_response(request)
        return response
