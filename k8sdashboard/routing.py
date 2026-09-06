from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/pod-logs/(?P<namespace>[\w-]+)/(?P<pod_name>[\w-]+)/(?P<container_name>[\w-]+)/$', consumers.PodLogConsumer.as_asgi()),
    # re_path(r'^room/(?P<group>\w+)/$', consumers.GroupConsumer.as_asgi()),
]
