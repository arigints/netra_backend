from rest_framework_simplejwt.views import TokenObtainPairView
from apps.api.v1.token.serializers import MyTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

