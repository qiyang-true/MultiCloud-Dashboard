from django.urls import path
from k8sdashboard import login

urlpatterns = [
    path('', login.login, name='index'),  # 默认首页
    path('login/', login.login, name='login'),
    path('logout/', login.logout, name='logout'),
    path('check/', login.check, name='check'),
    path('checkcode/', login.check_code, name='checkcode'),
]