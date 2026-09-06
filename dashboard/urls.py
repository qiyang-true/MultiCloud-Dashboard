"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include, re_path
from k8sdashboard import views, manager, authority, role, login, kubernetes, cloud

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path('^$', kubernetes.resources),
    # re_path('^login/$', login.login, name='login'),
    re_path('authority/', include('k8sdashboard.urls.urls_authority')),
    re_path('manager/', include('k8sdashboard.urls.urls_manager')),
    re_path('role/', include('k8sdashboard.urls.urls_role')),
    re_path('login/', include('k8sdashboard.urls.urls_login')),
    re_path('template/', include('k8sdashboard.urls.urls_template')),
    re_path('kubernetes/', include('k8sdashboard.urls.urls_kubernetes')),
    re_path('editkubernetes/', include('k8sdashboard.urls.urls_editkubernetes')),
    re_path('rollback/', include('k8sdashboard.urls.urls_rollback')),
    re_path('cluster/', include('k8sdashboard.urls.urls_cluster')),
]

urlpatterns += [
    re_path('^aliyun/overview/$', cloud.overview, {'provider_key': 'aliyun'}, name='aliyun_overview'),
    re_path('^aliyun/instances/$', cloud.instances, {'provider_key': 'aliyun'}, name='aliyun_instances'),
    re_path('^aliyun/instances/(?P<instance_id>[^/]+)/$', cloud.instance_detail, {'provider_key': 'aliyun'}, name='aliyun_instance_detail'),
    re_path('^aliyun/buckets/$', cloud.buckets, {'provider_key': 'aliyun'}, name='aliyun_buckets'),
    re_path('^aliyun/credentials/$', cloud.credentials, {'provider_key': 'aliyun'}, name='aliyun_credentials'),
    re_path('^aliyun/disks/$', cloud.disks, name='aliyun_disks'),
    re_path('^aliyun/security-groups/$', cloud.security_groups, name='aliyun_security_groups'),
    re_path('^aliyun/vpcs/$', cloud.vpcs, name='aliyun_vpcs'),
    re_path('^aliyun/snapshots/$', cloud.snapshots, name='aliyun_snapshots'),
    re_path('^aliyun/(?P<service_key>(ack|fc|rds|redis|mongodb|slb|nat|cdn|alarms|audit))/$', cloud.service_page, name='aliyun_service_page'),
    re_path('^tencent/overview/$', cloud.overview, {'provider_key': 'tencent'}, name='tencent_overview'),
    re_path('^tencent/instances/$', cloud.instances, {'provider_key': 'tencent'}, name='tencent_instances'),
    re_path('^tencent/instances/(?P<instance_id>[^/]+)/$', cloud.instance_detail, {'provider_key': 'tencent'}, name='tencent_instance_detail'),
    re_path('^tencent/buckets/$', cloud.buckets, {'provider_key': 'tencent'}, name='tencent_buckets'),
    re_path('^aws/overview/$', cloud.overview, {'provider_key': 'aws'}, name='aws_overview'),
    re_path('^aws/instances/$', cloud.instances, {'provider_key': 'aws'}, name='aws_instances'),
    re_path('^aws/instances/(?P<instance_id>[^/]+)/$', cloud.instance_detail, {'provider_key': 'aws'}, name='aws_instance_detail'),
    re_path('^aws/buckets/$', cloud.buckets, {'provider_key': 'aws'}, name='aws_buckets'),
    re_path('^aws/(?P<service_key>[a-z0-9-]+)/$', cloud.service_page, {'provider_key': 'aws'}, name='aws_service_page'),
]
