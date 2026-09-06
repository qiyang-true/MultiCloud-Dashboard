from django.urls import path, re_path
from k8sdashboard.rollback import rollbacklist

urlpatterns = [
    re_path('^rollbacklist/$', rollbacklist, name='rollbacklist'),
]
