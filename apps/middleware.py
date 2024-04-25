from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.contrib.auth import logout
from .models import UserProfile
from django.http import JsonResponse

class SingleSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        response = self.get_response(request)
        # Only proceed if user is authenticated
        if request.user.is_authenticated:
            # Initialize JWT Authentication to get the token and decode it
            jwt_auth = JWTAuthentication()
            header = jwt_auth.get_header(request)
            if header is not None:
                raw_token = jwt_auth.get_raw_token(header)
                if raw_token is not None:
                    validated_token = jwt_auth.get_validated_token(raw_token)

                    # Extract session_id claim from token
                    session_id_from_token = validated_token.get('session_id')

                    # Compare with the session_id stored in UserProfile
                    try:
                        user_profile = UserProfile.objects.get(user=request.user)
                        if user_profile.session_key != session_id_from_token:
                            # If mismatch, logout the user and raise AuthenticationFailed
                            logout(request)
                            return JsonResponse(
                                {'error': 'Session mismatch, other session active.'},
                                status=307  # temporarily redirect
                            )
                    except UserProfile.DoesNotExist:
                        pass  # Handle case if UserProfile does not exist

        return response
