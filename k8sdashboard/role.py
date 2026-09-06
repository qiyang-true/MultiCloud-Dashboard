from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from k8sdashboard.models import Manager, Role, Authority
from k8sdashboard.models import have_authority


def rolelist(request):
    role_list = Role.objects.all()
    check_assignpermissions = have_authority(request, 'role', 'assignpermissions')
    check_delrole = have_authority(request, 'role', 'delrole')
    return render(request, 'role/rolelist.html', {"role_list": role_list, 'assignpermissions': check_assignpermissions, 'delrole': check_delrole})

def addrole(request):
    name = request.POST.get("name")
    ret = Role.objects.create(name=name)
    if ret:
        return JsonResponse({'status': 1, 'info': '添加成功'})
    else:
        return JsonResponse({'status': 0, 'info': '添加失败'})
    
def updaterole(request):
    authority_id = request.POST.get('authority_id')
    role_id = request.POST.get('roleid')
    print('authority_id: '+authority_id)
    print(role_id)
    authority_id = get_auth_ids(authority_id)
    controller_method = get_controller_method(authority_id)
    print(authority_id)
    print(controller_method)
    ret = Role.objects.filter(id=role_id).update(authority_id=authority_id, controller_method=controller_method)
    print(ret)
    if ret:
        return JsonResponse({'status': 1, 'info': '修改成功'})
    else:
        return JsonResponse({'status': 0, 'info': '修改失败'})


def delrole(request, id):
    if request.method == 'GET':
        ret = Role.objects.filter(id=id).delete()
        print("delrole id: "+id, ret)
        return redirect(rolelist)

def assignpermissions(request, id):
    menu = Authority.objects.values('id', 'menu', 'level').order_by('path')
    role_info = Role.objects.values('id', 'authority_id').get(id=id)
    role_name = Role.objects.values_list('name', flat=True).get(id=id)
    print(role_info)
    if role_info['authority_id']:
        auth_id_arr = role_info['authority_id'].split(',')
        auth_id_arr = [int(x) for x in auth_id_arr]
        print(auth_id_arr)
    else:
        auth_id_arr = []
    context = {
        'auth_id_arr': auth_id_arr,
        'menu_list': menu,
        'role_name': role_name,
        "id": id,
    }
    return render(request, 'role/assignpermissions.html', context)

# 返回子菜单所有的上级菜单ids
def get_auth_ids(ids):
    id_list = ids.split(',')  # 将 ids 字符串分割成列表
    paths = Authority.objects.filter(id__in=id_list).values_list('path', flat=True)  # 查询对应 ids 的 path 列表

    auth_ids = []
    for path in paths:
        auth_ids.extend(path.split('-'))  # 将每个 path 按 '-' 分割后加入 auth_ids 列表

    auth_ids = list(set(auth_ids))  # 去重
    return ','.join(auth_ids)  # 返回逗号分隔的 auth_ids 字符串

# 返回字符串 controller-method
def get_controller_method(auth_ids):
    auth_ids_list = [int(auth_id) for auth_id in auth_ids.split(',')]
    
    auth_c_m = Authority.objects.filter(id__in=auth_ids_list).values('level', 'controller', 'method')
    
    c_m = ''
    for item in auth_c_m:
        if item['level'] < 2:
            continue
        c_m += f"{item['controller']}-{item['method']},"

    return c_m.rstrip(',')
