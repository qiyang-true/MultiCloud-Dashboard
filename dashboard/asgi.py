"""
ASGI config for dashboard project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')

# 确保Django已初始化
django.setup()

# 在Django设置完成后导入其他模块
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from k8sdashboard.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

if settings.DEBUG:
    application = ASGIStaticFilesHandler(application)
