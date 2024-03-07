from django.contrib.auth import logout
from .models import UserProfile

class OneSessionPerUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = UserProfile.objects.get(user=request.user)
            # If the session keys do not match, log out the user
            if profile.session_key != request.session.session_key:
                logout(request)
        response = self.get_response(request)
        return response
