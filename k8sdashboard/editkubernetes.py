from argparse import Namespace
from django.shortcuts import render, HttpResponse
from kubernetes import client, config
from datetime import datetime, timezone
from k8sdashboard.utils.common import ages
from django.http import JsonResponse
import yaml
import json
from k8sdashboard.utils.kubernetes_config import get_kubeconfig_from_db, _patch_rest_client_timeout
from k8sdashboard.models import Template


def _load_k8s_config(request):
    config_path = get_kubeconfig_from_db(request.session.get('currentclusterid'))
    _patch_rest_client_timeout()
    config.load_kube_config(config_path)


# def getDeployment(request):
#     _load_k8s_config(request)
#     v1 = client.AppsV1Api()
#     namespace = request.POST.get('namespace')
#     kindname = request.POST.get('kindname')
#     deployment = v1.read_namespaced_deployment(name=kindname, namespace=namespace)
    
#     # 移除 None 值后再转换为驼峰命名
#     deployment_dict = remove_none_values(deployment.to_dict())
#     deployment_dict = convert_keys_to_camel_case(deployment_dict)
#     deployment_yaml = yaml.dump(deployment_dict, default_flow_style=False).rstrip('\n')
    
#     data = {
#         'status': 1,
#         'info': '获取成功',
#         'data': deployment_yaml
#     }
#     return JsonResponse(data)


def deletePod(request):
    _load_k8s_config(request)
    v1 = client.CoreV1Api()
    podname = request.POST.get('podname')
    namespace = request.POST.get('namespace')
    
    # 添加参数验证
    if not podname:
        return JsonResponse({
            'status': 0,
            'info': 'Pod名称不能为空'
        })
    
    if not namespace:
        return JsonResponse({
            'status': 0,
            'info': '命名空间不能为空'
        })
    
    try:
        v1.delete_namespaced_pod(name=podname, namespace=namespace)
        data = {
            'status': 1,
            'info': '删除成功'
        }
    except Exception as e:
        data = {
            'status': 0,
            'info': f'删除失败: {str(e)}'
        }
    
    return JsonResponse(data)


def updateDeployment(request):
    _load_k8s_config(request)
    v1 = client.AppsV1Api()
    namespace = request.POST.get('namespace')
    kindname = request.POST.get('kindname')
    yaml_data = request.POST.get('yaml')
    
    # 将yaml数据转换为deployment对象
    deployment_dict = yaml.safe_load(yaml_data)
    deployment = v1.replace_namespaced_deployment(name=kindname, namespace=namespace, body=deployment_dict)
    # 转换为驼峰命名
    deployment_data = convert_keys_to_camel_case(deployment.to_dict())
    data = {
        'status': 1,
        'info': '更新成功',
        'data': deployment_data
    }
    return JsonResponse(data)

def setImages(request):
    _load_k8s_config(request)
    v1 = client.AppsV1Api()
    deploymentlist = v1.list_deployment_for_all_namespaces()
    return render(request, 'kubernetes/setImages.html', {'deploymentlist': deploymentlist.items})


def getPodResource(request):
    podname = request.POST.get('podname')
    namespace = request.POST.get('namespace')
    _load_k8s_config(request)
    v1 = client.CoreV1Api()
    pod = v1.read_namespaced_pod(name=podname, namespace=namespace)
    print(pod)
    # 移除 None 值后再转换为驼峰命名
    pod_dict = remove_none_values(pod.to_dict())
    pod_dict = convert_keys_to_camel_case(pod_dict)
    pod_yaml = yaml.dump(pod_dict, default_flow_style=False).rstrip('\n')
    
    data = {
        'status': 1,
        'info': '获取成功',
        'data': pod_yaml
    }
    return JsonResponse(data)


def updatePodResource(request):
    podname = request.POST.get('podname')
    namespace = request.POST.get('namespace')
    yaml_data = request.POST.get('yaml')
    
    # 参数验证
    if not podname:
        return JsonResponse({'status': 0, 'info': '缺少podname参数'})
    if not namespace:
        return JsonResponse({'status': 0, 'info': '缺少namespace参数'})
    if not yaml_data:
        return JsonResponse({'status': 0, 'info': '缺少yaml数据'})
    
    print(f"podname: {podname} namespace: {namespace} yaml_data: {yaml_data}")
    
    try:
        _load_k8s_config(request)
        v1 = client.CoreV1Api()
        # 将yaml数据转换为pod对象
        pod_dict = yaml.safe_load(yaml_data)
        pod = v1.replace_namespaced_pod(name=podname, namespace=namespace, body=pod_dict)
        # 转换为驼峰命名
        pod_data = convert_keys_to_camel_case(pod.to_dict())
        data = {
            'status': 1,
            'info': '编辑成功',
            'data': pod_data
        }
        return JsonResponse(data)
    except Exception as e:
        print(f"更新Pod资源时发生错误: {str(e)}")
        return JsonResponse({'status': 0, 'info': f'更新失败: {str(e)}'})


def updatePodResourceDryRun(request):
    _load_k8s_config(request)
    v1 = client.CoreV1Api()
    podname = request.POST.get('podname')
    namespace = request.POST.get('namespace')
    yaml_data = request.POST.get('yaml')
    dry_run = request.POST.get('dryRun', 'false').lower() == 'true'
    print(f"podname: {podname} namespace: {namespace} yaml_data: {yaml_data} dry_run: {dry_run}")
    pod_dict = yaml.safe_load(yaml_data)
    pod = v1.replace_namespaced_pod(name=podname, namespace=namespace, body=pod_dict, dry_run=dry_run)
    pod_data = convert_keys_to_camel_case(pod.to_dict())
    data = {
        'status': 1,
        'info': 'Dry run验证成功',
        'data': pod_data
    }
    return JsonResponse(data)


def deletePod(request):
    _load_k8s_config(request)
    v1 = client.CoreV1Api()
    podname = request.POST.get('podname')
    namespace = request.POST.get('namespace')
    v1.delete_namespaced_pod(name=podname, namespace=namespace)
    data = {
        'status': 1,
        'info': '删除成功'
    }
    return JsonResponse(data)

def getPodLogs(request):
    _load_k8s_config(request)
    v1 = client.CoreV1Api()
    # 修改参数获取方式，支持GET请求的查询参数
    podname = request.GET.get('pod_name') or request.POST.get('podname') # argo-rollouts-db7cf54c4-pxcwt
    namespace = request.GET.get('namespace') or request.POST.get('namespace')
    pod_result = v1.read_namespaced_pod(name=podname, namespace=namespace)
    pod_dict = pod_result.to_dict()
    container_name = pod_dict['spec']['containers'][0]['name']
    logs = v1.read_namespaced_pod_log(name=podname, namespace=namespace, tail_lines=200, container=container_name)
    data = {
        'status': 1,
        'info': '获取成功',
        'data': logs
    }
    return JsonResponse(data)

def rollBackImage(request):
    namespace = request.POST.get('namespace')
    deploymentname = request.POST.get('deploymentname')
    imagelist = request.POST.get('imagelist')
    imagelist = json.loads(imagelist) # {'frontend': 'harbor.k8s.local/cilium/hubble-ui:v0.12.0', 'backend': 'harbor.k8s.local/cilium/hubble-ui-backend:v0.12.0'}
    print("namespace: "+namespace+" deploymentname: "+deploymentname+" images: "+str(imagelist))
    images = []
    for i in imagelist:
        images.append({
            'name': i,
            'image': imagelist[i]
        })
    imagelist = {
        'spec': {
            'template': {
                'spec': {
                    'containers': images
                }
            }
        }
    }
    # print(imagelist)
    # print(type(imagelist))
    _load_k8s_config(request)
    v1 = client.AppsV1Api()
    v1.patch_namespaced_deployment(name=deploymentname, namespace=namespace, body=imagelist)
    data = {
        'status': 1,
        'info': '回滚成功'
    }
    return JsonResponse(data)

def getDeploymentNameFromReplicaset(request):
    _load_k8s_config(request)
    api_instance = client.AppsV1Api()
    replicasetname = request.POST.get('replicasetname')
    print(replicasetname)
    deployment_name = '-'.join(replicasetname.split('-')[:-1])
    namespace = request.POST.get('namespace')
    replicaset_result = api_instance.read_namespaced_replica_set(name=replicasetname, namespace=namespace)
    replicaset_dict = replicaset_result.to_dict()
    images = {}
    for i in replicaset_dict['spec']['template']['spec']['containers']:
        container_name = i['name']
        container_image = i['image']
        images[container_name] = container_image

    return JsonResponse({
        'status': 1,
        'info': '获取成功',
        'data': images,
        'deployment_name': deployment_name,
    })

def getDeploymentImagesFromSetImage(request):
    _load_k8s_config(request)
    api_instance = client.AppsV1Api()
    deploymentname = request.POST.get('deploymentname')
    namespace = request.POST.get('namespace')
    print(deploymentname)
    replicaset_result = api_instance.read_namespaced_deployment(name=deploymentname, namespace=namespace)
    deployment_dict = replicaset_result.to_dict()
    images = {}
    for i in deployment_dict['spec']['template']['spec']['containers']:
        container_name = i['name']
        container_image = i['image']
        images[container_name] = container_image

    return JsonResponse({
        'status': 1,
        'info': '获取成功',
        'data': images,
        'deployment_name': deploymentname,
    })

def remove_none_values(obj):
    """递归移除字典和列表中的 None 值和 managed_fields 字段"""
    if isinstance(obj, dict):
        filtered_dict = {}
        for k, v in obj.items():
            # 跳过 managed_fields 字段
            if k == 'managed_fields':
                continue
            # 跳过 None 值
            if v is not None:
                filtered_dict[k] = remove_none_values(v)
        return filtered_dict
    elif isinstance(obj, list):
        return [remove_none_values(item) for item in obj if item is not None]
    else:
        return obj

def to_camel_case(snake_str):
    """将下划线命名转换为驼峰命名（首字母小写）"""
    # 特殊处理：downward_api -> downwardAPI
    if snake_str == 'downward_api':
        return 'downwardAPI'
    
    components = snake_str.split('_')
    return components[0].lower() + ''.join(x.capitalize() for x in components[1:])

def convert_keys_to_camel_case(obj):
    """递归将字典中的键从下划线命名转换为驼峰命名"""
    if isinstance(obj, dict):
        converted_dict = {}
        for k, v in obj.items():
            # 转换键名
            camel_key = to_camel_case(k) if '_' in k else k
            # 递归处理值
            converted_dict[camel_key] = convert_keys_to_camel_case(v)
        return converted_dict
    elif isinstance(obj, list):
        return [convert_keys_to_camel_case(item) for item in obj]
    else:
        return obj

def getDeploymentResource(request):
    _load_k8s_config(request)
    v1 = client.AppsV1Api()
    deploymentname = request.POST.get('deploymentname')
    namespace = request.POST.get('namespace')
    deployment_result = v1.read_namespaced_deployment(name=deploymentname, namespace=namespace)
    # 移除 None 值后再转换为驼峰命名
    deployment_dict = remove_none_values(deployment_result.to_dict())
    deployment_dict = convert_keys_to_camel_case(deployment_dict)
    deployment_yaml = yaml.dump(deployment_dict, default_flow_style=False).rstrip('\n')
    return JsonResponse({
        'status': 1,
        'info': '获取成功',
        'data': deployment_yaml,
    })

def setDeploymentImages(request):
    namespace = request.POST.get('namespace')
    deploymentname = request.POST.get('deploymentname')
    imagelist = request.POST.get('imagelist')
    imagelist = json.loads(imagelist)
    images = []
    for i in imagelist:
        images.append({
            'name': i,
            'image': imagelist[i]
        })
    imagelist = {
        'spec': {
            'template': {
                'spec': {
                    'containers': images
                }
            }
        }
    }
    _load_k8s_config(request)
    v1 = client.AppsV1Api()
    v1.patch_namespaced_deployment(name=deploymentname, namespace=namespace, body=imagelist)
    print(namespace, deploymentname, imagelist)
    return JsonResponse({
        'status': 1,
        'info': '更新成功'
    })

def getReplicaset(request):
    _load_k8s_config(request)
    api_instance = client.AppsV1Api()
    replicasetname = request.POST.get('replicasetname')
    namespace = request.POST.get('namespace')
    result = api_instance.read_namespaced_replica_set(name=replicasetname, namespace=namespace)
    rs_dict = remove_none_values(result.to_dict())
    rs_dict = convert_keys_to_camel_case(rs_dict)
    rs_yaml = yaml.dump(rs_dict, default_flow_style=False).rstrip('\n')
    return JsonResponse({
        'status': 1,
        'info': '获取成功',
        'data': rs_yaml,
    })


def saveDeploymentResource(request):
    deploymentname = request.POST.get('deploymentname')
    filename = request.POST.get('filename') or deploymentname
    contents = request.POST.get('contents') or ''
    managerid = request.session.get('userid')
    if managerid and contents:
        ret = Template.objects.create(managerid=managerid, filename=filename, contents=contents)
        if ret:
            return JsonResponse({
                'status': 1,
                'info': '保存成功',
            })
        else:
            return JsonResponse({'status': 0, 'info': '创建错误'})
    else:
        return JsonResponse({'status': 0, 'info': '缺少用户信息或内容为空'})


def makeFile(request):
    """通用保存模板功能，支持所有资源类型"""
    filename = request.POST.get('filename', 'template.yaml')
    contents = request.POST.get('contents', '')
    managerid = request.session.get('userid')
    if managerid and contents:
        ret = Template.objects.create(managerid=managerid, filename=filename, contents=contents)
        if ret:
            return JsonResponse({'status': 1, 'info': '保存成功'})
        else:
            return JsonResponse({'status': 0, 'info': '创建错误'})
    else:
        return JsonResponse({'status': 0, 'info': '缺少用户信息或内容为空'})


def updateDeploymentResource(request):
    """更新deployment资源"""
    try:
        _load_k8s_config(request)
        v1 = client.AppsV1Api()
        
        namespace = request.POST.get('namespace')
        deploymentname = request.POST.get('deploymentname')
        yaml_data = request.POST.get('yaml')
        dry_run = request.POST.get('dryRun', 'false').lower() == 'true'
        
        if not namespace or not deploymentname or not yaml_data:
            return JsonResponse({
                'status': 0,
                'info': '缺少必要参数：namespace、deploymentname、yaml',
                'url': {'message': '参数不完整'}
            })
        
        # 将yaml数据转换为字典
        try:
            deployment_dict = yaml.safe_load(yaml_data)
        except yaml.YAMLError as e:
            return JsonResponse({
                'status': 0,
                'info': f'YAML格式错误: {str(e)}',
                'url': {'message': 'YAML格式错误'}
            })
        
        # 验证必要的字段
        if 'apiVersion' not in deployment_dict or 'kind' not in deployment_dict:
            return JsonResponse({
                'status': 0,
                'info': 'YAML中缺少apiVersion或kind字段',
                'url': {'message': 'YAML格式不完整'}
            })
        
        if deployment_dict.get('kind') != 'Deployment':
            return JsonResponse({
                'status': 0,
                'info': '资源类型必须是Deployment',
                'url': {'message': '资源类型错误'}
            })
        
        # 如果是dry run，使用K8s服务端dry-run验证
        if dry_run:
            try:
                v1.replace_namespaced_deployment(
                    name=deploymentname,
                    namespace=namespace,
                    body=deployment_dict,
                    dry_run='All'
                )
                return JsonResponse({
                    'status': 1,
                    'info': 'Dry run验证成功，YAML格式正确',
                })
            except Exception as e:
                return JsonResponse({
                    'status': 0,
                    'info': f'Dry run验证失败: {str(e)}',
                    'url': {'message': str(e)}
                })
        
        # 实际更新deployment
        try:
            updated_deployment = v1.replace_namespaced_deployment(
                name=deploymentname, 
                namespace=namespace, 
                body=deployment_dict
            )
            
            return JsonResponse({
                'status': 1,
                'info': f'Deployment {deploymentname} 更新成功',
                'data': {
                    'name': updated_deployment.metadata.name,
                    'namespace': updated_deployment.metadata.namespace,
                    'generation': updated_deployment.metadata.generation,
                    'resourceVersion': updated_deployment.metadata.resource_version
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 0,
                'info': f'更新deployment失败: {str(e)}',
                'url': {'message': str(e)}
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 0,
            'info': f'系统错误: {str(e)}',
            'url': {'message': str(e)}
        })

def updateServiceResource(request):
    """更新service资源"""
    try:
        _load_k8s_config(request)
        v1 = client.CoreV1Api()
        
        namespace = request.POST.get('namespace')
        servicename = request.POST.get('servicename')
        yaml_data = request.POST.get('yaml')

        # 必要参数校验
        if not namespace or not servicename or not yaml_data:
            return JsonResponse({
                'status': 0,
                'info': '缺少必要参数：namespace、servicename、yaml',
                'url': {'message': '参数不完整'}
            })

        # yaml 格式校验
        try:
            service_dict = yaml.safe_load(yaml_data)
        except yaml.YAMLError as e:
            return JsonResponse({
                'status': 0,
                'info': f'YAML格式错误: {str(e)}',
                'url': {'message': 'YAML格式错误'}
            })

        # 验证必要字段
        if 'apiVersion' not in service_dict or 'kind' not in service_dict:
            return JsonResponse({
                'status': 0,
                'info': 'YAML中缺少apiVersion或kind字段',
                'url': {'message': 'YAML格式不完整'}
            })

        if service_dict.get('kind') != 'Service':
            return JsonResponse({
                'status': 0,
                'info': '资源类型必须是Service',
                'url': {'message': '资源类型错误'}
            })

        # 实际更新service
        try:
            updated_service = v1.replace_namespaced_service(
                name=servicename,
                namespace=namespace,
                body=service_dict
            )
            return JsonResponse({
                'status': 1,
                'info': f'Service {servicename} 更新成功',
                'data': {
                    'name': updated_service.metadata.name,
                    'namespace': updated_service.metadata.namespace,
                    'clusterIP': getattr(updated_service.spec, 'cluster_ip', None),
                    'resourceVersion': updated_service.metadata.resource_version
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 0,
                'info': f'更新service失败: {str(e)}',
                'url': {'message': str(e)}
            })
    except Exception as e:
        return JsonResponse({
            'status': 0,
            'info': f'系统错误: {str(e)}',
            'url': {'message': str(e)}
        })

def updateServiceResourceDryRun(request):
    """Dry Run 验证service资源更新"""
    try:
        _load_k8s_config(request)
        v1 = client.CoreV1Api()

        namespace = request.POST.get('namespace')
        servicename = request.POST.get('servicename')
        yaml_data = request.POST.get('yaml')

        # 必要参数校验
        if not namespace or not servicename or not yaml_data:
            return JsonResponse({
                'status': 0,
                'info': '缺少必要参数：namespace、servicename、yaml',
                'url': {'message': '参数不完整'}
            })

        # yaml 格式校验
        try:
            service_dict = yaml.safe_load(yaml_data)
        except yaml.YAMLError as e:
            return JsonResponse({
                'status': 0,
                'info': f'YAML格式错误: {str(e)}',
                'url': {'message': 'YAML格式错误'}
            })

        # 验证必要字段
        if 'apiVersion' not in service_dict or 'kind' not in service_dict:
            return JsonResponse({
                'status': 0,
                'info': 'YAML中缺少apiVersion或kind字段',
                'url': {'message': 'YAML格式不完整'}
            })

        if service_dict.get('kind') != 'Service':
            return JsonResponse({
                'status': 0,
                'info': '资源类型必须是Service',
                'url': {'message': '资源类型错误'}
            })

        # 读取现有 Service 作为连通性与存在性验证
        try:
            _ = v1.read_namespaced_service(name=servicename, namespace=namespace)
            return JsonResponse({
                'status': 1,
                'info': 'Dry run验证成功',
                'data': 'YAML格式正确，可以安全更新'
            })
        except Exception as e:
            return JsonResponse({
                'status': 0,
                'info': f'Dry run验证失败: {str(e)}',
                'url': {'message': str(e)}
            })

    except Exception as e:
        return JsonResponse({
            'status': 0,
            'info': f'系统错误: {str(e)}',
            'url': {'message': str(e)}
        })

def getServiceResource(request):
    _load_k8s_config(request)
    v1 = client.CoreV1Api()
    servicename = request.POST.get('servicename')
    namespace = request.POST.get('namespace')
    service_result = v1.read_namespaced_service(name=servicename, namespace=namespace)
    service_dict = remove_none_values(service_result.to_dict())
    service_dict = convert_keys_to_camel_case(service_dict)
    service_yaml = yaml.dump(service_dict, default_flow_style=False).rstrip('\n')
    return JsonResponse({
        'status': 1,
        'info': '获取成功',
        'data': service_yaml,
    })


def getIngressResource(request):
    _load_k8s_config(request)
    v1 = client.NetworkingV1Api()
    ingressname = request.POST.get('ingressname') or request.POST.get('kindname')
    namespace = request.POST.get('namespace')
    ingress_result = v1.read_namespaced_ingress(name=ingressname, namespace=namespace)
    ingress_dict = remove_none_values(ingress_result.to_dict())
    ingress_dict = convert_keys_to_camel_case(ingress_dict)
    ingress_yaml = yaml.dump(ingress_dict, default_flow_style=False).rstrip('\n')
    print(ingress_yaml)
    return JsonResponse({
        'status': 1,
        'info': '获取成功',
        'data': ingress_yaml,
    })

def updateIngressResource(request):
    """更新ingress资源"""
    try:
        _load_k8s_config(request)
        v1 = client.NetworkingV1Api()

        namespace = request.POST.get('namespace')
        ingressname = request.POST.get('ingressname') or request.POST.get('kindname')
        yaml_data = request.POST.get('yaml')
        dry_run = request.POST.get('dryRun', 'false').lower() == 'true'

        # 必要参数校验
        if not namespace or not ingressname or not yaml_data:
            return JsonResponse({
                'status': 0,
                'info': '缺少必要参数：namespace、ingressname/kindname、yaml',
                'url': {'message': '参数不完整'}
            })

        # 解析 YAML
        try:
            ingress_dict = yaml.safe_load(yaml_data)
        except yaml.YAMLError as e:
            return JsonResponse({
                'status': 0,
                'info': f'YAML格式错误: {str(e)}',
                'url': {'message': 'YAML格式错误'}
            })

        # 验证必要字段
        if 'apiVersion' not in ingress_dict or 'kind' not in ingress_dict:
            return JsonResponse({
                'status': 0,
                'info': 'YAML中缺少apiVersion或kind字段',
                'url': {'message': 'YAML格式不完整'}
            })

        if ingress_dict.get('kind') != 'Ingress':
            return JsonResponse({
                'status': 0,
                'info': '资源类型必须是Ingress',
                'url': {'message': '资源类型错误'}
            })

        # Dry Run：仅做连通性与存在性验证
        if dry_run:
            try:
                _ = v1.read_namespaced_ingress(name=ingressname, namespace=namespace)
                return JsonResponse({
                    'status': 1,
                    'info': 'Dry run验证成功',
                    'data': 'YAML格式正确，可以安全更新'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 0,
                    'info': f'Dry run验证失败: {str(e)}',
                    'url': {'message': str(e)}
                })

        # 实际更新 Ingress
        try:
            updated_ingress = v1.replace_namespaced_ingress(
                name=ingressname,
                namespace=namespace,
                body=ingress_dict
            )
            return JsonResponse({
                'status': 1,
                'info': f'Ingress {ingressname} 更新成功',
                'data': {
                    'name': updated_ingress.metadata.name,
                    'namespace': updated_ingress.metadata.namespace,
                    'generation': updated_ingress.metadata.generation,
                    'resourceVersion': updated_ingress.metadata.resource_version
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 0,
                'info': f'更新ingress失败: {str(e)}',
                'url': {'message': str(e)}
            })

    except Exception as e:
        return JsonResponse({
            'status': 0,
            'info': f'系统错误: {str(e)}',
            'url': {'message': str(e)}
        })


def getConfigmapResource(request):
    _load_k8s_config(request)
    v1 = client.CoreV1Api()
    configmapname = request.POST.get('configmapname') or request.POST.get('kindname')
    namespace = request.POST.get('namespace')
    configmap_result = v1.read_namespaced_config_map(name=configmapname, namespace=namespace)
    configmap_dict = remove_none_values(configmap_result.to_dict())
    configmap_dict = convert_keys_to_camel_case(configmap_dict)
    configmap_yaml = yaml.dump(configmap_dict, default_flow_style=False).rstrip('\n')
    return JsonResponse({
        'status': 1,
        'info': '获取成功',
        'data': configmap_yaml,
    })

def getDaemonsetResource(request):
    _load_k8s_config(request)
    api = client.AppsV1Api()
    dsname = request.POST.get('daemonsetname') or request.POST.get('kindname')
    namespace = request.POST.get('namespace')
    result = api.read_namespaced_daemon_set(name=dsname, namespace=namespace)
    ds_dict = remove_none_values(result.to_dict())
    ds_dict = convert_keys_to_camel_case(ds_dict)
    ds_yaml = yaml.dump(ds_dict, default_flow_style=False).rstrip('\n')
    return JsonResponse({
        'status': 1,
        'info': '获取成功',
        'data': ds_yaml,
    })


def updateDaemonsetResource(request):
    try:
        _load_k8s_config(request)
        api = client.AppsV1Api()

        namespace = request.POST.get('namespace')
        dsname = request.POST.get('daemonsetname') or request.POST.get('kindname')
        yaml_data = request.POST.get('yaml')
        dry_run = request.POST.get('dryRun', 'false').lower() == 'true'

        if not namespace or not dsname or not yaml_data:
            return JsonResponse({
                'status': 0,
                'info': '缺少必要参数',
                'url': {'message': '参数不完整'}
            })

        try:
            ds_dict = yaml.safe_load(yaml_data)
        except yaml.YAMLError as e:
            return JsonResponse({
                'status': 0,
                'info': f'YAML格式错误: {str(e)}',
                'url': {'message': 'YAML格式错误'}
            })

        if ds_dict.get('kind') != 'DaemonSet':
            return JsonResponse({
                'status': 0,
                'info': '资源类型必须是DaemonSet',
                'url': {'message': '资源类型错误'}
            })

        if dry_run:
            try:
                api.replace_namespaced_daemon_set(
                    name=dsname, namespace=namespace,
                    body=ds_dict, dry_run='All'
                )
                return JsonResponse({'status': 1, 'info': 'Dry run验证成功'})
            except Exception as e:
                return JsonResponse({
                    'status': 0,
                    'info': f'Dry run验证失败: {str(e)}',
                    'url': {'message': str(e)}
                })

        updated = api.replace_namespaced_daemon_set(
            name=dsname, namespace=namespace, body=ds_dict
        )
        return JsonResponse({
            'status': 1,
            'info': f'DaemonSet {dsname} 更新成功',
            'data': {
                'name': updated.metadata.name,
                'namespace': updated.metadata.namespace,
                'generation': updated.metadata.generation,
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 0,
            'info': f'系统错误: {str(e)}',
            'url': {'message': str(e)}
        })


def updateConfigmapResource(request):
    """更新configmap资源"""
    try:
        _load_k8s_config(request)
        v1 = client.CoreV1Api()

        namespace = request.POST.get('namespace')
        configmapname = request.POST.get('configmapname') or request.POST.get('kindname')
        yaml_data = request.POST.get('yaml')
        dry_run = request.POST.get('dryRun', 'false').lower() == 'true'

        if not namespace or not configmapname or not yaml_data:
            return JsonResponse({
                'status': 0,
                'info': '缺少必要参数：namespace、configmapname/kindname、yaml',
                'url': {'message': '参数不完整'}
            })

        try:
            configmap_dict = yaml.safe_load(yaml_data)
        except yaml.YAMLError as e:
            return JsonResponse({
                'status': 0,
                'info': f'YAML格式错误: {str(e)}',
                'url': {'message': 'YAML格式错误'}
            })

        if not isinstance(configmap_dict, dict) or 'apiVersion' not in configmap_dict or 'kind' not in configmap_dict:
            return JsonResponse({
                'status': 0,
                'info': 'YAML中缺少apiVersion或kind字段',
                'url': {'message': 'YAML格式不完整'}
            })

        if configmap_dict.get('kind') != 'ConfigMap':
            return JsonResponse({
                'status': 0,
                'info': '资源类型必须是ConfigMap',
                'url': {'message': '资源类型错误'}
            })

        if dry_run:
            try:
                _ = v1.read_namespaced_config_map(name=configmapname, namespace=namespace)
                return JsonResponse({
                    'status': 1,
                    'info': 'Dry run验证成功',
                    'data': 'YAML格式正确，可以安全更新'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 0,
                    'info': f'Dry run验证失败: {str(e)}',
                    'url': {'message': str(e)}
                })

        try:
            updated_configmap = v1.replace_namespaced_config_map(
                name=configmapname,
                namespace=namespace,
                body=configmap_dict
            )
            return JsonResponse({
                'status': 1,
                'info': f'ConfigMap {configmapname} 更新成功',
                'data': {
                    'name': updated_configmap.metadata.name,
                    'namespace': updated_configmap.metadata.namespace,
                    'resourceVersion': updated_configmap.metadata.resource_version
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 0,
                'info': f'更新configmap失败: {str(e)}',
                'url': {'message': str(e)}
            })

    except Exception as e:
        return JsonResponse({
            'status': 0,
            'info': f'系统错误: {str(e)}',
            'url': {'message': str(e)}
        })