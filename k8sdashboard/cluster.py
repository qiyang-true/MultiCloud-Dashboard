from django.db.models import manager
from django.shortcuts import render, HttpResponse
from kubernetes import client, config
from datetime import datetime, timezone
from k8sdashboard.utils.common import ages
from django.http import JsonResponse
from k8sdashboard.models import have_authority, Cluster
import yaml
import base64
import time


def cluster(request):
    return render(request, 'cluster/cluster.html')

def addcluster(request):
    if request.method == "GET":
        return render(request, 'cluster/addcluster.html')
    elif request.method == "POST":
        config_data = request.POST.get('config')
        # print(config_data)
        try:
            # 解析YAML配置数据
            config_dict = yaml.safe_load(config_data)
            
            if not config_dict or 'clusters' not in config_dict or 'users' not in config_dict or 'contexts' not in config_dict:
                return JsonResponse({'status': 0, 'info': '配置文件格式不正确'})
            
            # 获取当前用户ID（从session中获取）
            manager_id = request.session.get('userid')
            
            # 获取第一个集群和用户信息
            cluster_info = config_dict['clusters'][0] if config_dict['clusters'] else {}
            user_info = config_dict['users'][0] if config_dict['users'] else {}
            context_info = config_dict['contexts'][0] if config_dict['contexts'] else {}
            
            # 提取集群信息
            cluster_name = cluster_info.get('name', '')
            server = cluster_info.get('cluster', {}).get('server', '')
            
            # 提取用户信息
            username = user_info.get('name', '')
            
            # 提取认证信息
            token = None
            certificate_authority_data = None
            client_certificate_data = None
            client_key_data = None
            
            if 'user' in user_info:
                user_auth = user_info['user']
                
                # 检查是否有token
                if 'token' in user_auth:
                    token = user_auth['token']
                
                # 检查是否有证书认证
                if 'client-certificate-data' in user_auth:
                    client_certificate_data = user_auth['client-certificate-data']
                
                if 'client-key-data' in user_auth:
                    client_key_data = user_auth['client-key-data']
                
                # 检查集群证书
                if 'certificate-authority-data' in cluster_info.get('cluster', {}):
                    certificate_authority_data = cluster_info['cluster']['certificate-authority-data']
            
            # 获取当前时间戳
            current_time = int(time.time())
            
            # 创建Cluster对象并保存到数据库
            cluster_obj = Cluster(
                managerid=manager_id,
                clustername=cluster_name,
                server=server,
                username=username,
                token=token,
                certificate_authority_data=certificate_authority_data,
                client_certificate_data=client_certificate_data,
                client_key_data=client_key_data,
                mtime=current_time,
                atime=current_time
            )
            cluster_obj.save()
            print(cluster_obj)
            return JsonResponse({'status': 1, 'info': '集群添加成功'})
            
        except yaml.YAMLError as e:
            return JsonResponse({'status': 0, 'info': f'YAML解析错误: {str(e)}'})
        except Exception as e:
            return JsonResponse({'status': 0, 'info': f'保存失败: {str(e)}'})
    
    return render(request, 'cluster/addcluster.html')

def clusterlist(request):
    clusters = Cluster.objects.all()
    renameClusterUser = have_authority(request, 'cluster', 'renameClusterUser')
    clusterDelete = have_authority(request, 'cluster', 'clusterDelete')
    copyToMamager = have_authority(request, 'cluster', 'copyToMamager')
    print(copyToMamager)
    # copyToRelease = have_authority(request, 'cluster', 'copyToRelease')
    return render(request, 'cluster/clusterlist.html', 
    {'clusters': clusters, 
    'renameClusterUser': renameClusterUser, 
    'clusterDelete': clusterDelete, 
    'copyToMamager': copyToMamager, 
    # 'copyToRelease': copyToRelease
    })

def editcluster(request):
    return render(request, 'cluster/editcluster.html')

def deletecluster(request):
    return render(request, 'cluster/deletecluster.html')

def renameclusteruser(request):
    clusterid = request.POST.get('id')
    username = request.POST.get('username')
    clustername = request.POST.get('clustername')
    cluster = Cluster.objects.get(id=clusterid)
    cluster.username = username
    cluster.clustername = clustername
    cluster.save()
    return JsonResponse({'status': 1, 'info': '修改成功'})

def clusterdelete(request):
    clusterid = request.POST.get('id')
    cluster = Cluster.objects.get(id=clusterid)
    cluster.delete()
    return JsonResponse({'status': 1, 'info': '删除成功'})

def copytomamager(request):
    return render(request, 'cluster/copyToMamager.html')

def getmanagerlist(request):
    managerlist = Cluster.objects.values('managerid', 'clustername').distinct()
    managerlist = list(managerlist)
    for item in managerlist:
        print(item['managerid'])
        print(item['clustername'])
    return JsonResponse({'status': 1, 'managerlist': managerlist})


def setcurrentcontext(request):
    clusterid = request.POST.get('clusterid')
    if clusterid:
        request.session['currentclusterid'] = clusterid
        cluster = Cluster.objects.get(id=clusterid)
        request.session['currentcontext'] = cluster.clustername+'@'+cluster.username
        return JsonResponse({'status': 1, 'info': '设置成功'})
    else:
        return JsonResponse({'status': 0, 'info': '设置失败'})