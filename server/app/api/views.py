from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
        UserSerializer,
        AuthTokenSerializer,
        StreamSerializer,
)
from core.models import Stream


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(TokenObtainPairView):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer


class CreateStreamView(generics.CreateAPIView):
    serializer_class = StreamSerializer
    permission_class = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        return super().create(request, *args, **kwargs)
