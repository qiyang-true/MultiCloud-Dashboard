from django.contrib import admin
from k8sdashboard.models import Manager, Role, Authority, Template, Cluster


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'role_id', 'supermanager', 'atime', 'mtime']
    search_fields = ['username']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'atime', 'mtime']
    search_fields = ['name']


@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ['id', 'menu', 'pid', 'controller', 'method', 'path', 'level', 'top_menu_id', 'orderby']
    search_fields = ['menu', 'controller', 'method']
    list_filter = ['level']


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'managerid', 'filename', 'atime', 'mtime']
    search_fields = ['filename']


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ['id', 'managerid', 'clustername', 'server', 'username', 'atime']
    search_fields = ['clustername', 'server']
