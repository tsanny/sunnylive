from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    StreamSerializer,
    StreamUpdateResponseSerializer,
    DonationSerializer,
    CommentSerializer,
)
from core.models import Stream, Donation, Comment


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(TokenObtainPairView):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateRetrieveStreamView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView
):
    serializer_class = StreamSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Stream.objects.all()

    def post(self, request, *args, **kwargs):
        request.data["host"] = request.user.pk
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
                {"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
            )
        stream.save()
        response_data = {
            "message": message,
            "stream_title": stream.title,
            "stream_id": stream.id,
        }
        serializer = StreamUpdateResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateRetrieveDonationView(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, generics.GenericAPIView
):
    serializer_class = DonationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Donation.objects.all()

    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.pk
        return super().create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ListDonationView(ListAPIView):
    serializer_class = DonationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        stream_id = self.request.query_params.get("stream")

        if stream_id:
            return Donation.objects.filter(stream__id=stream_id, stream__host=user)
        else:
            return Donation.objects.filter(stream__host=user)


class CreateRetrieveCommentView(
    mixins.CreateModelMixin, mixins.ListModelMixin, generics.GenericAPIView
):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        stream_id = self.kwargs.get("stream_id")

        queryset = Comment.objects.filter(stream__id=stream_id, stream__host=user)

        if not queryset.exists():
            raise NotFound("No comments found for the given criteria.")

        return queryset

    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.pk
        return super().create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
