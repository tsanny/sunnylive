import uuid
import hashlib
import midtransclient
from django.conf import settings


def create_transaction(request):
    snap = midtransclient.Snap(
        is_production=False, server_key=settings.MIDTRANS_SERVER_KEY
    )
    param = {
        "transaction_details": {
            "order_id": str(uuid.uuid4()).replace("-", "")[:16],
            "gross_amount": request.data["amount"],
        },
        "credit_card": {"secure": True},
        "customer_details": {
            "id": str(request.user.id),
            "email": request.user.email,
        },
        "metadata": {
            "username": request.user.username,
            "stream": request.data["stream"],
            "message": request.data["message"],
        },
    }

    return snap.create_transaction(param)


def validate_transaction(order_id, status_code, gross_amount, signature_key):
    hash = hashlib.sha512(
        (order_id + status_code + gross_amount + settings.MIDTRANS_SERVER_KEY).encode(
            "utf-8"
        )
    ).hexdigest()
    return hash == signature_key
