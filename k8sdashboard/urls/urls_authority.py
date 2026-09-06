from django.urls import path, re_path
from k8sdashboard import authority

urlpatterns = [
    re_path('^authoritylist/$', authority.authoritylist, name='authoritylist'),
    re_path('^addauthority/$', authority.addauthority, name='addauthority'),
    re_path(r'^delauthority/(?P<id>\d+)/$', authority.delauthority),
    re_path(r'^updateauthority/(?P<id>\d+)/$', authority.updateauthority),
]