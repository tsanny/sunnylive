from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Stream, Donation, Comment, CustomUser

from .tasks import create_object
from .utils import send_message_to_channel
from .midtrans.client import create_transaction, validate_transaction
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


class CurrentUserView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RetrieveUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()


class LogoutView(views.APIView):
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


class UpdateStreamView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, action):
        stream = get_object_or_404(Stream, pk=pk)

        if stream.host != request.user:
            return Response(
                {"message": "You do not have permission to modify this stream."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if action == "start":
            stream.is_live = True
            message = "Stream started successfully."
        elif action == "end":
            stream.is_live = False
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


class StreamAuthView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        stream_id = self.request.query_params.get("stream_id")
        if not stream_id:
            return Response(
                {"detail": "Stream query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stream = get_object_or_404(Stream, pk=stream_id)
        if stream.is_live:
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

        auth_failed_message = "Stream authorization failed"
        if not call or call != "publish" or not stream_key:
            return Response(
                {"message": auth_failed_message},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            stream = Stream.objects.get(stream_key=stream_key)
            if not stream:
                return Response(
                    {"message": auth_failed_message},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Stream.DoesNotExist:
            return Response(
                {"message": auth_failed_message},
                status=status.HTTP_403_FORBIDDEN,
            )

        HttpResponseRedirect.allowed_schemes.append("rtmp")
        return HttpResponseRedirect(
            redirect_to=f"rtmp://127.0.0.1/live/{stream.id}",
            status=status.HTTP_302_FOUND,
        )


class StreamDoneView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print("RTMP Stream stopped successfully.")
        return Response(status=status.HTTP_200_OK)


class CreateCommentView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.pk
        create_object.delay("send_message", request.data)
        return Response("Comment received successfully", status=status.HTTP_201_CREATED)


class CreateDonationView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            stream = data["stream"]
            message = data["message"]
            order_id = data["order_id"]
            status_code = data["status_code"]
            amount = data["gross_amount"]
            signature = data["signature_key"]

            if validate_transaction(
                order_id,
                status_code,
                amount,
                signature,
            ):
                user = CustomUser.objects.get(username=data["username"])
                send_message_to_channel(
                    stream,
                    "send_donation",
                    message,
                    user,
                    amount,
                )
                create_object.delay(
                    "send_donation",
                    {
                        "stream": stream,
                        "message": message,
                        "user": str(user.pk),
                        "amount": amount,
                    },
                )
                return Response(
                    {"detail": "Donation received successfully"},
                    status=status.HTTP_201_CREATED,
                )
            return Response("Invalid transaction.", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(type(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class ChargeDonationView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            return Response(create_transaction(request))
        except Exception as e:
            return Response(
                {
                    "message": "An error has occured while creating the transaction.",
                    "error": type(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
