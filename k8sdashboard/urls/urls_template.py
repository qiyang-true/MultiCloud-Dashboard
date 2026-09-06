from django.urls import path, re_path
from k8sdashboard import template

urlpatterns = [
    re_path('^templatelist/$', template.templatelist, name='templatelist'),
    re_path('^addtemplate/$', template.addtemplate, name='addtemplate'),
    re_path('^updatetemplate/$', template.updatetemplate, name='updatetemplate'),
    re_path('^deltemplate/$', template.deltemplate, name='deltemplate'),
    re_path('^savetemplatecontent/$', template.saveTemplateContent, name='saveTemplateContent'),
    re_path('^renametemplate/$', template.renameTemplate, name='renameTemplate'),
    # re_path('^addrole$', role.addrole, name='addrole'),
    # re_path(r'^assignpermissions/(?P<id>\d+)/$', role.assignpermissions, name='assignpermissions'),
    # re_path('^updaterole/', role.updaterole),
]