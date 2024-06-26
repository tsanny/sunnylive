from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_message_to_channel(stream, message_type, message, user, amount=None):
    channel_layer = get_channel_layer()
    data = {
        "type": message_type,
        "message": message,
        "user": {
            "username": user.username,
            "id": str(user.id),
        },
    }
    if amount is not None:
        data["amount"] = amount
    async_to_sync(channel_layer.group_send)(stream, data)
