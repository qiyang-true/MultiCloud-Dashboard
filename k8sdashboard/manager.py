from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from k8sdashboard.models import Manager, Role, Authority
from k8sdashboard.models import have_authority
from k8sdashboard.login import hash_password



def managerlist(request):
    manager_list = Manager.objects.all()
    role_list = Role.objects.values('id', 'name')
    rlist = {item['id']: item['name'] for item in role_list} # 显示角色
    check_updatemanager = have_authority(request, 'manager', 'updatemanager')   # 判断是否有修改权限
    check_delmanager = have_authority(request, 'manager', 'delmanager')         # 判断是否有删除权限
    return render(request, 'manager/managerlist.html', {'manager_list': manager_list, 'role_list': role_list, 'rlist': rlist, 'updatemanager': check_updatemanager, 'delmanager': check_delmanager})

def addmanager(request):
    if request.method == "GET":
        return render(request, 'manager/addmanager.html')
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role_id = request.POST.get("role_id")
        print(username, password, role_id)
        manager = Manager.objects.create(username=username, password=hash_password(password), role_id=role_id)
        print(manager)
        if manager:
            return redirect(managerlist)
        else:
            msg = "添加失败"
            return render(request, "manager/addmanager.html", {"msg": msg})

def delmanager(request, id):
    if request.method == "GET":
        ret = Manager.objects.filter(id=id).delete()
        print(ret)
        # return HttpResponse("删除成功")
        return redirect(managerlist)
    
def updatemanager(request, id):
    ret = Manager.objects.filter(id=id).get()
    role_list = Role.objects.values('id', 'name')
    return render(request, "manager/updatemanager.html", {'role_list': role_list, 'username': ret.username})

def update(request):
    id = request.POST.get("id")
    password = request.POST.get("password")
    repassword = request.POST.get("repassword")
    role_id = request.POST.get("role_id")
    if password == repassword:
        print(id, password, role_id)
        ret = Manager.objects.filter(id=id).update(password=hash_password(password), role_id=role_id)
        if ret:
            return JsonResponse({'status': 1, 'info': '修改成功'})
        else:
            return JsonResponse({'status': 0, 'info': '修改失败'})
    else:
        return JsonResponse({'status': 0, 'info': '修改失败'})
    