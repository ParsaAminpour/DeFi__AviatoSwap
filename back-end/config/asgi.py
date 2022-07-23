import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from dotenv import load_dotenv
import chatroom.routing

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# application = get_asgi_application()
application = ProtocolTypeRouter({
  'http' : get_asgi_application(),

  'websocket' : URLRouter(chatroom.routing.websocket_urlpatterns),
})


