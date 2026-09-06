# settings.py
# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [os.path.join(BASE_DIR, 'k8sdashboard/templates')],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 ...
#                 'dashboard.context.nav', # 自定义上下文处理器，有涉及到模版则执行，没有模版则不执行
#             ],
#         },
#     },
# ]
from django.shortcuts import redirect
from k8sdashboard import cluster
from k8sdashboard.models import Authority, Role, Cluster

from urllib.parse import urlparse, parse_qs


def nav(request):
    print('Context processor: custom context processor......')
    # print(request.COOKIES.get('username')+'------------cookie')
    # print(request.COOKIES.get('password')+'------------cookie')
    current_username = request.session.get('username', None)
    if current_username is not None:
        # role_id = request.session.get('role_id')
        menu = Authority.objects.filter(level=0).all()
        data = get_menu_list(request)
        cluster_list = get_cluster_list(request)
        currentcontext = request.session.get('currentcontext')
        return {"current_username": current_username, "menu": menu, 'leftmenu': data['leftmenu'], 'topnav': data['topnav'], 'cluster_list': cluster_list, 'currentcontext': currentcontext}
    else:
        return {}

# 根据管理员id来获取集群列表
def get_cluster_list(request):
    userid = request.session.get('userid')
    cluster_list = Cluster.objects.filter(managerid=userid).values('id','clustername','username')
    
    # 转换为字典格式并打印
    # cluster_data = cluster_list
    # print("=== 集群列表数据（字典格式）===")
    # for cluster in cluster_data:
    #     print(cluster)
    
    return cluster_list



def get_menu_list(request):
    role_id = request.session.get('role_id')
    # role = Role.objects.get(id=role_id)
    # authority_ids = role.authority_id.all().values_list('id', flat=True)
    authority_ids = Role.objects.filter(id=role_id).values_list('authority_id', flat=True)
    authority_ids = [int(id) for id in authority_ids.get().split(',')]
    # print(authority_ids)
    
    wheretop = {
        'level': 0,
        'id__in': authority_ids,
    }
    listtop = Authority.objects.filter(**wheretop).values('id','menu','controller','method','pid','level').order_by('id')
    # print(listtop)

    top_menu_id = int(request.GET.get('topid', '30'))
    whereleft = {
        'top_menu_id': top_menu_id,
        'level__gt': 0,
        'level__lt': 3,
        'id__in': authority_ids,
    }
    menu = Authority.objects.filter(**whereleft).order_by('path').values('id','menu','controller','method','pid','path','level','top_menu_id')
    # print(menu)
    listleft = get_secondary_menu(menu, top_menu_id)
    # print(listleft)
    return {'topnav': listtop, 'leftmenu': listleft}


# 
#  把一维菜单搞成二维菜单列表，用于前端循环展示
#  $list array 一维的菜单列表，包含二级三级的菜单，函数会把三级菜单套在二级菜单下。
#  $top_menu_id 一级菜单的id，也就是二级三级菜单所属的顶级菜单的id
# 
# for key, value in leftmenu.items():
#     print(f"Top Menu ID: {key}")
#     print(f"Menu Name: {value['menu']}")
#     print("Child Menus:")
#     # 遍历子菜单
#     child_menus = value.get('child_menu', {})
#     for child_key, child_value in child_menus.items():
#         print(f"  Child Menu ID: {child_key}")
#         print(f"  Child Menu Name: {child_value['menu']}")
#         print(f"  Path: {child_value['path']}")
#         print(f"  Level: {child_value['level']}")
#         print("---")
# 
# [] 这个叫列表
# () 这个叫元组
# set({1,2}) set([1,2]) 这个叫集合，集合可以运算，集合是一个无序无重复元素的集合，所以在集合内增加存在的元素，操作是无效的。
# 集合在创建时可以用符号{}和set()，但是如何要创建空集合只能用set()，因为{}是来创建空字典的。 
# {} 这个叫字典
# 数组和字典可以混合着使用
def get_secondary_menu(menu_list, top_menu_id):
    menu_dict = {item['id']: item for item in menu_list}
    delnum = []
    for key in menu_dict:
        # print(menu_dict[key])
        if menu_dict[key]['pid'] != top_menu_id:
            pid_num = menu_dict[key]['pid']
            delnum.append(key)
            if 'child_menu' in menu_dict[pid_num]:
                # menu_dict[pid_num]['child_menu'].append({key: menu_dict[key]})
                menu_dict[pid_num]['child_menu'].update({key: menu_dict[key]})
            else:
                menu_dict[pid_num]['child_menu'] = {}
                menu_dict[pid_num]['child_menu'].update({key: menu_dict[key]})
    for key in delnum:
        if key in menu_dict:
            del menu_dict[key]
    # print(menu_dict)
    return menu_dict
