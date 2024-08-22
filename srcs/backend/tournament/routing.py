from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/pong/(?P<tournament_id>\d+)/$', consumers.PongConsumer.as_asgi()),
]

