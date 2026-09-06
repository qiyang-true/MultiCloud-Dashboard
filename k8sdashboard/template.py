from k8sdashboard.models import Template
from django.shortcuts import render
from django.http import JsonResponse


def templatelist(request):
    template_list = Template.objects.values('id','managerid','filename','mtime','atime')
    print(template_list)
    return render(request, 'template/templatelist.html', {'template_list': template_list})

def addtemplate(request):
    managerid = request.session['userid']
    filename = request.POST.get('filename')
    if managerid and filename:
        ret = Template.objects.create(managerid=managerid, filename=filename)
    else:
        return JsonResponse({'status': 0, 'info': '创建错误'})

    if ret:
        return JsonResponse({'status': 1, 'info': '创建成功'})
    else:
        return JsonResponse({'status': 0, 'info': '创建失败'})

def deltemplate(request):
    id = request.POST.get('id')
    ret = Template.objects.filter(id=id).delete()
    if ret:
        return JsonResponse({'status': 1, 'info': '删除成功'})
    else:
        return JsonResponse({'status': 0, 'info': '删除失败'})

def updatetemplate(request):
    id = request.POST.get('id')
    content = Template.objects.filter(id=id).values('contents').get()
    if content['contents'] == None:
        return JsonResponse({'status': 1, 'info': ''})
    else:
        return JsonResponse({'status': 1, 'info': content['contents']})
    
def saveTemplateContent(request):
    id = request.POST.get('id')
    contents = request.POST.get('contents')
    ret = Template.objects.filter(id=id).update(contents=contents)
    if ret:
        return JsonResponse({'status': 1, 'info': '保存成功'})
    else:
        return JsonResponse({'status': 0, 'info': '保存失败'})
    
def renameTemplate(request):
    id = request.POST.get('id')
    filename = request.POST.get('filename')
    ret = Template.objects.filter(id=id).update(filename=filename)
    if ret:
        return JsonResponse({'status': 1, 'info': '重命名成功'})
    else:
        return JsonResponse({'status': 0, 'info': '重命名失败'})
