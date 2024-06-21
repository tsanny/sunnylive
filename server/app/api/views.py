from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    StreamSerializer,
    StreamUpdateResponseSerializer,
)
from core.models import Stream


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(TokenObtainPairView):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateRetrieveStreamView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView
):
    serializer_class = StreamSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Stream.objects.all()

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.pk
        return super().create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class UpdateStreamView(APIView):
    def post(self, request, pk, action):
        stream = get_object_or_404(Stream, pk=pk)

        if action == "start":
            stream.is_started = True
            stream.is_ended = False
            message = "Stream started successfully."
        elif action == "end":
            stream.is_started = False
            stream.is_ended = True
            message = "Stream ended successfully."
        else:
            return Response(
                {"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
            )
        stream.save()
        response_data = {
            "message": message,
            "stream_title": stream.title,
            "stream_id": stream.id,
        }
        serializer = StreamUpdateResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
