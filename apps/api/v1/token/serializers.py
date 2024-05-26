from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.sessions.models import Session
import uuid
from apps.models import UserProfile

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # First, call the superclass method that validates the user and returns the token
        data = super().validate(attrs)
        
        # Get the user object
        user = self.user

        # Generate a new session identifier
        new_session_id = str(uuid.uuid4())
        
        # Retrieve or create the user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Invalidate the previous session if it exists
        if profile.session_key:
            Session.objects.filter(session_key=profile.session_key).delete()

        # Update the user profile with the new session identifier
        profile.session_key = new_session_id
        profile.save()

        # Add custom claims to the token
        token = self.get_token(user)  # This retrieves the already generated token
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['session_id'] = new_session_id  # Include the new session identifier in the token
        token['level'] = profile.level  # Include the user profile level in the token

        # Return the token and additional data
        return {
            'access': str(token.access_token),
            'refresh': str(token),
            'session_id': new_session_id,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
            'level': profile.level 
        }

