from .tasks import create_object
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Stream, Donation, Comment, CustomUser
from .utils import send_message_to_channel
from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    StreamSerializer,
    StreamKeySerializer,
    StreamUpdateResponseSerializer,
    DonationSerializer,
    CommentSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(TokenObtainPairView):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer


class CurrentUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RetrieveUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()


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


class CreateStreamView(generics.CreateAPIView):
    serializer_class = StreamSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Stream.objects.all()

    def post(self, request, *args, **kwargs):
        request.data["host"] = request.user.pk
        return super().create(request, *args, **kwargs)


class RetrieveStreamView(generics.RetrieveAPIView):
    serializer_class = StreamSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Stream.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class RetrieveStreamKeyView(generics.RetrieveAPIView):
    serializer_class = StreamKeySerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Stream.objects.all()

    def get_object(self):
        obj = super().get_object()
        if obj.host != self.request.user:
            raise PermissionDenied("You are not the host of this stream.")
        return obj

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class UpdateStreamView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, action):
        stream = get_object_or_404(Stream, pk=pk)

        if stream.host != request.user:
            return Response(
                {"message": "You do not have permission to modify this stream."},
                status=status.HTTP_403_FORBIDDEN,
            )

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


class StreamAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        stream_id = self.request.query_params.get("stream_id")
        if not stream_id:
            return Response(
                {"detail": "Stream query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stream = get_object_or_404(Stream, pk=stream_id)
        if stream.is_started and not stream.is_ended:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        data = request.data
        addr = data.get("addr")
        flashver = data.get("flashver")
        call = data.get("call")
        stream_key = data.get("name")

        if addr == "127.0.0.1" and flashver == "LNX.11,1,102,55":
            return Response(status=status.HTTP_200_OK)

        if not call or call != "publish" or not stream_key:
            return Response(
                {"message": "Stream authorization failed"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            stream = Stream.objects.get(stream_key=stream_key)
            if not stream:
                return Response(
                    {"message": "Stream authorization failed"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Stream.DoesNotExist:
            return Response(
                {"message": "Stream authorization failed"},
                status=status.HTTP_403_FORBIDDEN,
            )

        HttpResponseRedirect.allowed_schemes.append("rtmp")
        return HttpResponseRedirect(
            redirect_to=f"rtmp://127.0.0.1/live/{stream.id}",
            status=status.HTTP_302_FOUND,
        )


class StreamDoneView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data

        print("RTMP Stream stopped successfully.")
        print(data)
        return Response(status=status.HTTP_200_OK)


class CreateBaseView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.pk

        if self.message_type == "send_donation":
            send_message_to_channel(
                stream=request.data["stream"],
                message_type=self.message_type,
                message=request.data["message"],
                user=request.user,
                amount=request.data.get("amount"),
            )

        create_object.delay(self.message_type, request.data)
        return Response(status=status.HTTP_200_OK)


class CreateCommentView(CreateBaseView):
    serializer_class = CommentSerializer
    message_type = "send_message"


class CreateDonationView(CreateBaseView):
    serializer_class = DonationSerializer
    message_type = "send_donation"


class RetrieveDonationView(generics.RetrieveAPIView):
    serializer_class = DonationSerializer
    queryset = Donation.objects.all()


class ListCommentView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        user = self.request.user
        stream_id = self.kwargs.get("stream_id")

        queryset = Comment.objects.filter(stream__id=stream_id, stream__host=user)

        if not queryset.exists():
            raise NotFound("No comments found for the given criteria.")

        return queryset


class ListDonationView(generics.ListAPIView):
    serializer_class = DonationSerializer

    def get_queryset(self):
        user = self.request.user
        stream_id = self.request.query_params.get("stream")

        if stream_id:
            return Donation.objects.filter(stream__id=stream_id, stream__host=user)
        else:
            return Donation.objects.filter(stream__host=user)
