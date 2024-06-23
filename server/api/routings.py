from django.urls import path
from .consumers import CommentConsumer

websocket_urlpatterns = [
    path(r"ws/comment/<str:stream_id>/", CommentConsumer.as_asgi()),
]
