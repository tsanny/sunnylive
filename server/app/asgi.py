import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from api import routings
from api.middlewares import jwt_auth_middleware_stack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            jwt_auth_middleware_stack(URLRouter(routings.websocket_urlpatterns)),
        ),
    }
)
