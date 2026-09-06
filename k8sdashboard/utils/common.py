from django.urls import resolve
# from django.shortcuts import redirect
from k8sdashboard.models import Authority
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

def hello():
    print('hello')

# 检查是否有权限
# def have_authority(request):
#     resolver_match = resolve(request.path_info)
#     controller = resolver_match.func.__module__.split('.')[1]
#     method = resolver_match.func.__name__
#     return controller+'-'+method

# /**
# * 返回分类表的path,level和pid字段
# *
# * @param $table String 数据表名称或数据表对象
# * @param $pid int 此分类的父级id
# * @param $category_id int 添加此条数据还回的id
# * @return array( path=>'',level=>'')
# */
def get_path_level_pid(pid, category_id):
    if pid == '0' or pid == 0:
        data = {
            'path': str(category_id),
            'level': 0,
        }
    else:
        parent_instance = Authority.objects.get(id=pid)  # 获取父级实例
        parent_path = parent_instance.path  # 假设模型中有一个名为path的字段表示路径
        data = {
            'path': f'{parent_path}-{category_id}',
            'level': parent_path.count('-') + 1,
        }

    data['pid'] = pid
    data['id'] = category_id
    return data

# 人性化显示时间
def ages(dt):
    now = datetime.now(timezone.utc)
    delta = relativedelta(now, dt)
    
    # 计算总秒数差异
    total_seconds = (now - dt).total_seconds()
    
    if total_seconds < 60:
        # 小于1分钟，显示秒数
        return f"{int(total_seconds)} seconds ago"
    elif total_seconds < 3600:
        # 小于1小时，显示分钟数
        return f"{int(total_seconds // 60)} minutes ago"
    elif total_seconds < 86400:
        # 小于1天，显示小时数
        return f"{int(total_seconds // 3600)} hours ago"
    elif total_seconds < 2592000:
        # 小于1个月，显示天数
        return f"{int(total_seconds // 86400)} days ago"
    elif total_seconds < 31536000:
        # 小于1年，显示月份数
        return f"{delta.months + delta.years * 12} months ago"
    else:
        # 大于1年，显示年份数
        return f"{delta.years} years ago"