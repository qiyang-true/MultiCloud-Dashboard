from django.urls import path, re_path
from k8sdashboard import manager

urlpatterns = [
    re_path('^managerlist/$', manager.managerlist, name='managerlist'),
    re_path('^addmanager/$', manager.addmanager, name='addmanager'),
    re_path(r'^delmanager/(?P<id>\d+)/$', manager.delmanager, name='delmanager'),
    re_path(r'^updatemanager/(?P<id>\d+)/$', manager.updatemanager, name='updatemanager'),
    # re_path(r'^update/(?P<id>\d+)/$', manager.update, name='update'),
    re_path('^update/$', manager.update, name='update'),
]