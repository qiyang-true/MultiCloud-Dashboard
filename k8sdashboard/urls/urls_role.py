from django.urls import path, re_path
from k8sdashboard import role

urlpatterns = [
    re_path('^rolelist/$', role.rolelist, name='rolelist'),
    re_path('^addrole$', role.addrole, name='addrole'),
    re_path(r'^assignpermissions/(?P<id>\d+)/$', role.assignpermissions, name='assignpermissions'),
    re_path('^updaterole/', role.updaterole),
    re_path(r'^delrole/(?P<id>\d+)/$', role.delrole, name='delrole'),
]