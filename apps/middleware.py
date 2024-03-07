from django.contrib.auth import logout

class OneSessionPerUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            stored_session_key = request.user.userprofile.session_key
            if stored_session_key and stored_session_key != request.session.session_key:
                logout(request)
        
        response = self.get_response(request)
        return response
