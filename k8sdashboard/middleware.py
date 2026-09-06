# 在 settings.py 里设置如下：
# MIDDLEWARE = [
#     ......
#     'k8sdashboard.middleware.MyMiddleware',
# ]

from k8sdashboard.models import Manager
from django.http import JsonResponse
from django.shortcuts import redirect, render
from kubernetes.client.rest import ApiException
from urllib3.exceptions import MaxRetryError


class MyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 将请求路径转为小写，解决 Authority 表中 controller/method 大小写不一致问题
        request.path_info = request.path_info.lower()
        if request.session.get('username') is None:
            public_paths = ('/login/', '/static/', '/favicon.ico')
            if not request.path_info.startswith(public_paths):
                return redirect('/login/')
        try:
            response = self.get_response(request)
            return response
        except (ApiException, MaxRetryError, OSError, TypeError):
            return self._connection_error(request)

    def process_exception(self, request, exception):
        if isinstance(exception, (ApiException, MaxRetryError, OSError, TypeError)):
            return self._connection_error(request)
        return None

    def _connection_error(self, request):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'status': 0, 'info': '集群连接失败，请稍后重试'})
        return render(request, 'common/connection_error.html', status=200)
