from .serializers import CommentSerializer, DonationSerializer
from celery import shared_task


@shared_task
def create_object(message_type, data):
    if message_type == "send_message":
        serializer = CommentSerializer(data=data)
    elif message_type == "send_donation":
        serializer = DonationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return serializer.data
