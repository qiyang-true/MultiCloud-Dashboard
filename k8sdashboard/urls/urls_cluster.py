from django.urls import path, re_path
from k8sdashboard import cluster

urlpatterns = [
    re_path('^cluster/$', cluster.cluster, name='cluster'),
    re_path('^addcluster/$', cluster.addcluster, name='addcluster'),
    re_path('^clusterlist/$', cluster.clusterlist, name='clusterlist'),
    re_path('^editcluster/(?P<id>\d+)/$', cluster.editcluster, name='editcluster'),
    re_path('^deletecluster/$', cluster.deletecluster, name='deletecluster'),
    re_path('^renameclusteruser/$', cluster.renameclusteruser, name='renameclusteruser'),
    re_path('^clusterdelete/$', cluster.clusterdelete, name='clusterdelete'),
    re_path('^copytomamager/$', cluster.copytomamager, name='copytomamager'),
    re_path('^getmanagerlist/$', cluster.getmanagerlist, name='getmanagerlist'),
    re_path('^setcurrentcontext/$', cluster.setcurrentcontext, name='setcurrentcontext'),
]