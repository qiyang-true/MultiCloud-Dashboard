from django.shortcuts import render, redirect, HttpResponse
from k8sdashboard.models import Authority, have_authority
from k8sdashboard.utils.common import get_path_level_pid

def authoritylist(request):
    menu_list = Authority.objects.all().order_by('path')
    check_updateauthority = have_authority(request, 'authority', 'updateauthority')
    check_delauthority = have_authority(request, 'authority', 'delauthority')
    return render(request, 'authority/authoritylist.html', {'menu_list': menu_list, 'updateauthority': check_updateauthority, 'delauthority': check_delauthority})

def addauthority(request):
    print(request.POST)
    menu = request.POST.get("menu")
    pid = request.POST.get("pid")
    controller = request.POST.get("controller")
    if controller == None:
        controller = ''
    method = request.POST.get("method")
    if method == None:
        method = ''
    add_ret = Authority.objects.create(menu=menu, pid=pid, controller=controller, method=method)
    data = get_path_level_pid(pid, add_ret.id)
    print(data)
    if pid == '0':
        top_menu_id = add_ret.id
    else:
        top_menu_id = data['path'].split('-')[0]
    update_ret = Authority.objects.filter(id=add_ret.id).update(path=data['path'], level=data['level'], pid=data['pid'], top_menu_id=top_menu_id)
    if update_ret:
        return redirect(authoritylist)
    else:
        return render(request, 'authority/authoritylist.html', {'msg': '添加失败'})

def delauthority(request, id):
    if request.method == "GET":
        path = Authority.objects.get(id=id).path
        count = Authority.objects.filter(path__startswith=f"{path}-").count()
        if count == 0:
            ret = Authority.objects.filter(id=id).delete()
            print('delauthority ', 'id: '+id, ret)
            return redirect(authoritylist)
        else:
            print('有子菜单 path: '+path+' count: '+count)
            return redirect(authoritylist)
    
def updateauthority(request, id):
    if request.method == "GET":
        menu_list = Authority.objects.all().order_by('path')
        current_menu = Authority.objects.get(id=id)
        return render(request, 'authority/updateauthority.html', {"menu_list": menu_list, 'current_menu': current_menu, "id": id})
    elif request.method == "POST":
        menu = request.POST.get("menu")
        pid = request.POST.get("pid")
        controller = request.POST.get("controller")
        if controller == None:
            controller = ''
        method = request.POST.get("method")
        if method == None:
            method = ''
        data = get_path_level_pid(pid, id)
        print(data)
        if pid == '0':
            top_menu_id = id
        else:
            top_menu_id = data['path'].split('-')[0]
        update_ret = Authority.objects.filter(id=id).update(menu=menu, controller=controller, method=method, pid=data['pid'], path=data['path'], level=data['level'], top_menu_id=top_menu_id)
        if update_ret:
            return redirect(authoritylist)
        else:
            return render(request, 'authority/authoritylist.html', {'msg': '修改失败'})