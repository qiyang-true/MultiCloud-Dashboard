import re
import json
from django.shortcuts import render, HttpResponse
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from datetime import datetime, timezone
from k8sdashboard.utils.common import ages
from django.http import JsonResponse
from k8sdashboard.models import Cluster, have_authority
from k8sdashboard.utils.kubernetes_config import (
    cleanup_temp_config,
    get_kubeconfig_from_db,
    NoClusterConfiguredError,
    _patch_rest_client_timeout,
)
from django.core.paginator import Paginator
from k8sdashboard.cloud import (
    get_instances,
    home_cloud_pies,
    home_cluster_previews,
    provider_summaries,
)


def _safe_list_namespaces():
    """安全获取 namespace 列表，超时时返回空列表"""
    try:
        v1 = client.CoreV1Api()
        return v1.list_namespace()
    except Exception:
        return type('NamespaceList', (), {'items': []})()


def _load_kubeconfig_or_error(request):
    """加载kubeconfig并设置5秒超时，如果无可用集群则返回错误页面"""
    try:
        config_path = get_kubeconfig_from_db(request.session.get('currentclusterid'))
        _patch_rest_client_timeout()
        config.load_kube_config(config_path)
        return None
    except NoClusterConfiguredError:
        return render(request, 'common/no_cluster.html', {
            'cluster_id': request.session.get('currentclusterid')
        })


def _parse_cpu_to_millicores(cpu_str):
    """Convert K8s CPU quantity to millicores: 500m, 2, 50000000n"""
    if not cpu_str:
        return 0
    cpu_str = str(cpu_str).strip().lower()
    try:
        if cpu_str.endswith('n'):
            return round(float(cpu_str[:-1]) / 1000000.0, 6)
        if cpu_str.endswith('u'):
            return round(float(cpu_str[:-1]) / 1000.0, 6)
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1])
        return float(cpu_str) * 1000.0
    except ValueError:
        return 0


def _parse_memory_to_bytes(mem_str):
    """Convert K8s memory quantity to bytes: '1024Ki' -> 1048576, '1Gi' -> 1073741824"""
    if not mem_str:
        return 0
    mem_str = str(mem_str).strip()
    match = re.match(r'^(\d+(?:\.\d+)?)([a-zA-Z]*)$', mem_str)
    if not match:
        return 0
    value = float(match.group(1))
    unit = match.group(2)
    multipliers = {
        'Ki': 1024, 'Mi': 1024 ** 2, 'Gi': 1024 ** 3, 'Ti': 1024 ** 4,
        'Pi': 1024 ** 5, 'Ei': 1024 ** 6,
        'k': 1000, 'M': 1000 ** 2, 'G': 1000 ** 3, 'T': 1000 ** 4,
        'P': 1000 ** 5, 'E': 1000 ** 6,
        '': 1,
    }
    return int(value * multipliers.get(unit, 1))


def _format_cpu_core_str(millicores):
    """Format millicores to human string: 1500 -> '1.500'"""
    if millicores is None:
        return None
    return f"{millicores / 1000:.3f}"


def _format_bytes_human(bytes_val):
    """Format bytes to human string: 1073741824 -> '1 GiB'"""
    if bytes_val is None:
        return None
    if bytes_val == 0:
        return "0 B"
    value = float(bytes_val)
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if abs(value) < 1024.0 or unit == 'TiB':
            return f"{round(value)} {unit}"
        value /= 1024.0
    return f"{round(value)} TiB"


def _bar_color(percent):
    """Return CSS color for usage bar: green <50%, yellow 50-80%, red >80%"""
    if percent is None:
        return '#ccc'
    if percent > 80:
        return '#FF5722'
    elif percent > 50:
        return '#FFB800'
    else:
        return '#5FB878'


def pods(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    v1 = client.CoreV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    pod_name = request.GET.get('podname') or ''
    try:
        if selected_namespace:
            podlist = v1.list_namespaced_pod(namespace=selected_namespace)
        else:
            podlist = v1.list_pod_for_all_namespaces(watch=False)
        pod_items = podlist.items
    except Exception:
        pod_items = []

    # 按名称过滤（模糊匹配，不区分大小写）
    if pod_name:
        pod_items = [item for item in pod_items
                    if pod_name.lower() in item.metadata.name.lower()]

    # 按创建时间排序（最新在前）
    try:
        pod_items.sort(key=lambda x: x.metadata.creation_timestamp, reverse=True)
    except Exception:
        pass

    print("Listing pods with their IPs:")
    x = 0

    # Try to fetch pod metrics from metrics-server
    pod_metrics_available = True
    pod_metrics_map = {}
    try:
        custom_api = client.CustomObjectsApi()
        pod_metrics_result = custom_api.list_cluster_custom_object(
            group="metrics.k8s.io", version="v1beta1", plural="pods"
        )
        for item in pod_metrics_result.get('items', []):
            ns = item['metadata']['namespace']
            pname = item['metadata']['name']
            total_cpu = 0
            total_mem = 0
            for container in item.get('containers', []):
                usage = container.get('usage', {})
                total_cpu += _parse_cpu_to_millicores(usage.get('cpu', '0'))
                total_mem += _parse_memory_to_bytes(usage.get('memory', '0Ki'))
            pod_metrics_map[(ns, pname)] = {
                'cpu_millicores': total_cpu,
                'memory_bytes': total_mem,
            }
    except Exception:
        pod_metrics_available = False

    listall = []
    # 将权限检查移到循环外部，确保变量始终被定义
    check_deletePod = have_authority(request, 'kubernetes', 'deletePod')
    check_editPods = have_authority(request, 'kubernetes', 'editPods')
    check_shortLogs = have_authority(request, 'kubernetes', 'shortLogs')
    for i in pod_items:
        list = {}
        list['name'] = i.metadata.name
        list['namespace'] = i.metadata.namespace
        list['node_name'] = i.spec.node_name
        list['pod_ip'] = i.status.pod_ip
        list['phase'] = i.status.phase
        # list['create_time'] = i.metadata.creation_timestamp
        list['create_time'] = ages(i.metadata.creation_timestamp)
        # print(list['create_time'])
        ready = 0
        container_statuses = i.status.container_statuses or []
        for x in container_statuses:
            if x.ready == True:
                ready = ready + 1
        list['ready'] = ready
        list['pod_total'] = len(container_statuses)
        # 添加容器信息
        list['containers'] = []
        if i.spec.containers:
            for container in i.spec.containers:
                list['containers'].append({'name': container.name})

        # 计算 pod 级别的 CPU/内存 limits 总和
        pod_cpu_limits = 0
        pod_mem_limits = 0
        pod_cpu_requests = 0
        pod_mem_requests = 0
        if i.spec.containers:
            for container in i.spec.containers:
                res = container.resources
                limits = res.limits if res and res.limits else {}
                requests = res.requests if res and res.requests else {}
                pod_cpu_limits += _parse_cpu_to_millicores(limits.get('cpu', '0')) if limits else 0
                pod_mem_limits += _parse_memory_to_bytes(limits.get('memory', '0')) if limits else 0
                pod_cpu_requests += _parse_cpu_to_millicores(requests.get('cpu', '0')) if requests else 0
                pod_mem_requests += _parse_memory_to_bytes(requests.get('memory', '0')) if requests else 0

        # 查找 metrics 数据
        metrics = pod_metrics_map.get((i.metadata.namespace, i.metadata.name), {})
        cpu_usage = metrics.get('cpu_millicores')
        mem_usage = metrics.get('memory_bytes')
        has_running_container = any(
            x.state and x.state.running is not None
            for x in container_statuses
        )
        if cpu_usage is None and mem_usage is None and not has_running_container:
            cpu_usage = 0
            mem_usage = 0

        list['cpu_usage'] = _format_cpu_core_str(cpu_usage) if cpu_usage is not None else None
        list['mem_usage'] = _format_bytes_human(mem_usage) if mem_usage is not None else None
        cpu_percent_base = pod_cpu_limits if pod_cpu_limits > 0 else pod_cpu_requests
        mem_percent_base = pod_mem_limits if pod_mem_limits > 0 else pod_mem_requests
        list['cpu_limits'] = _format_cpu_core_str(cpu_percent_base) if cpu_percent_base > 0 else None
        list['mem_limits'] = _format_bytes_human(mem_percent_base) if mem_percent_base > 0 else None

        # 计算使用比例（仅在 limits 存在且有 metrics 数据时计算）
        if cpu_percent_base > 0 and cpu_usage is not None:
            list['cpu_pct'] = round(cpu_usage / cpu_percent_base * 100, 1)
            list['cpu_bar_color'] = _bar_color(list['cpu_pct'])
        else:
            list['cpu_pct'] = None
            list['cpu_bar_color'] = None

        if mem_percent_base > 0 and mem_usage is not None:
            list['mem_pct'] = round(mem_usage / mem_percent_base * 100, 1)
            list['mem_bar_color'] = _bar_color(list['mem_pct'])
        else:
            list['mem_pct'] = None
            list['mem_bar_color'] = None

        listall.append(list)

    # 搜索时不分页；无搜索时分页
    if pod_name:
        pod_page = listall
    else:
        paginator = Paginator(listall, 15)
        page_number = request.GET.get('page')
        try:
            pod_page = paginator.get_page(page_number)
        except:
            pod_page = paginator.get_page(1)

    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/pods.html', {
        'podlist': pod_page,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
        'pod_name': pod_name,
        'deletePod': check_deletePod,
        'editPods': check_editPods,
        'shortLogs': check_shortLogs,
        'pod_metrics_available': pod_metrics_available,
    })


def deployments(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    # 创建 AppsV1Api 实例
    api_instance = client.AppsV1Api()
    # 根据前端传入的命名空间筛选
    selected_namespace = request.GET.get('namespace') or ''
    deployment_name = request.GET.get('deploymentname') or ''
    try:
        if selected_namespace:
            deployment_result = api_instance.list_namespaced_deployment(namespace=selected_namespace)
        else:
            deployment_result = api_instance.list_deployment_for_all_namespaces()
        deployment_items = deployment_result.items
    except Exception:
        deployment_items = []

    # 按名称过滤（模糊匹配，不区分大小写）
    if deployment_name:
        deployment_items = [item for item in deployment_items
                            if deployment_name.lower() in item.metadata.name.lower()]

    # 按创建时间排序（最新在前）
    try:
        deployment_items.sort(key=lambda x: x.metadata.creation_timestamp, reverse=True)
    except Exception:
        pass

    # 搜索时不分页；无搜索时分页
    if deployment_name:
        deployment_page = deployment_items
    else:
        paginator = Paginator(deployment_items, 15)
        page_number = request.GET.get('page')
        try:
            deployment_page = paginator.get_page(page_number)
        except:
            deployment_page = paginator.get_page(1)
    # 获取命名空间列表用于前端筛选展示
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    check_editDeployment = have_authority(request, 'kubernetes', 'editDeployment')
    check_setImages = have_authority(request, 'kubernetes', 'setImages')
    return render(request, 'kubernetes/deployments.html', {
        'deploymentlist': deployment_page,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
        'deployment_name': deployment_name,
        'editDeployment': check_editDeployment,
        'setImages': check_setImages
    })


def replicasets(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.AppsV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    replicaset_name = request.GET.get('replicasetname') or ''

    try:
        if selected_namespace:
            replicaset_result = api_instance.list_namespaced_replica_set(namespace=selected_namespace)
        else:
            replicaset_result = api_instance.list_replica_set_for_all_namespaces()
        replicaset_items = replicaset_result.items
    except Exception:
        replicaset_items = []

    # 按名称过滤
    if replicaset_name:
        replicaset_items = [item for item in replicaset_items
                          if replicaset_name.lower() in item.metadata.name.lower()]

    # 按创建时间排序（最新的在前）
    replicaset_items.sort(key=lambda x: x.metadata.creation_timestamp, reverse=True)

    # 如果有搜索条件，不分页；否则分页
    if replicaset_name:
        # 搜索时不分页，显示所有结果
        replicaset_page = replicaset_items
    else:
        # 没有搜索时使用分页
        paginator = Paginator(replicaset_items, 15)  # 每页显示15条记录
        page_number = request.GET.get('page')
        try:
            replicaset_page = paginator.get_page(page_number)
        except:
            replicaset_page = paginator.get_page(1)

    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    check_rollBack = have_authority(request, 'kubernetes', 'rollbackimage')
    return render(request, 'kubernetes/replicasets.html', {
        'replicasetlist': replicaset_page,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
        'replicaset_name': replicaset_name,
        'rollBackImage': check_rollBack
    })


def daemonsets(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.AppsV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            daemonset_result = api_instance.list_namespaced_daemon_set(namespace=selected_namespace)
        else:
            daemonset_result = api_instance.list_daemon_set_for_all_namespaces()
        daemonset_items = daemonset_result.items
    except Exception:
        daemonset_items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    check_editDaemonset = have_authority(request, 'kubernetes', 'editDaemonset')
    return render(request, 'kubernetes/daemonsets.html', {
        'daemonsetlist': daemonset_items,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
        'editDaemonset': check_editDaemonset,
    })

def statefulsets(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.AppsV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            statefulset_result = api_instance.list_namespaced_stateful_set(namespace=selected_namespace)
        else:
            statefulset_result = api_instance.list_stateful_set_for_all_namespaces()
        statefulset_items = statefulset_result.items
    except Exception:
        statefulset_items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/statefulsets.html', {'statefulsetlist': statefulset_items, 'namespaces': namespaces.items, 'selected_namespace': selected_namespace})

def cronjob(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.BatchV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api_instance.list_namespaced_cron_job(namespace=selected_namespace)
        else:
            result = api_instance.list_cron_job_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/cronjob.html', {'cronjoblist': items, 'namespaces': namespaces.items, 'selected_namespace': selected_namespace})


def job(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.BatchV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api_instance.list_namespaced_job(namespace=selected_namespace)
        else:
            result = api_instance.list_job_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/job.html', {'joblist': items, 'namespaces': namespaces.items, 'selected_namespace': selected_namespace})

def services(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.CoreV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            service_result = api_instance.list_namespaced_service(namespace=selected_namespace)
        else:
            service_result = api_instance.list_service_for_all_namespaces()
        service_items = service_result.items
    except Exception:
        service_items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/services.html', {'servicelist': service_items, 'namespaces': namespaces.items, 'selected_namespace': selected_namespace})

def endpoints(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.CoreV1Api()
    endpointlist = api_instance.list_endpoints_for_all_namespaces()
    return render(request, 'kubernetes/endpoints.html', {'endpointlist': endpointlist.items})

def endpointslice(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.DiscoveryV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api_instance.list_namespaced_endpoint_slice(namespace=selected_namespace)
        else:
            result = api_instance.list_endpoint_slice_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/endpointslice.html', {'endpointslicelist': items, 'namespaces': namespaces.items, 'selected_namespace': selected_namespace})

def ingress(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.NetworkingV1Api()
    ingresslist = api_instance.list_ingress_for_all_namespaces()
    editIngress = have_authority(request, 'kubernetes', 'editIngress')
    setServiceWeightIngress = have_authority(request, 'kubernetes', 'setServiceWeightIngress')
    return render(request, 'kubernetes/ingress.html', {'ingresslist': ingresslist.items, 'editIngress': editIngress, 'setServiceWeightIngress': setServiceWeightIngress})

def ingressclass(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.NetworkingV1Api()
    ingressclasslist = api_instance.list_ingress_class()
    return render(request, 'kubernetes/ingressclass.html', {'ingressclasslist': ingressclasslist.items})

def secrets(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.CoreV1Api()
    secretlist = api_instance.list_secret_for_all_namespaces()
    return render(request, 'kubernetes/secrets.html', {'secretlist': secretlist.items})

def configmaps(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.CoreV1Api()
    configmaplist = api_instance.list_config_map_for_all_namespaces()
    editConfigmap = have_authority(request, 'kubernetes', 'editConfigmap')
    return render(request, 'kubernetes/configmaps.html', {'configmaplist': configmaplist.items, 'editConfigmap': editConfigmap})

def persistentVolumes(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.CoreV1Api()
    try:
        result = api_instance.list_persistent_volume()
        items = result.items
    except Exception:
        items = []
    return render(request, 'kubernetes/persistentvolumes.html', {'pvlist': items})

def persistentvolumeclaims(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.CoreV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api_instance.list_namespaced_persistent_volume_claim(namespace=selected_namespace)
        else:
            result = api_instance.list_persistent_volume_claim_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/persistentvolumeclaims.html', {'pvclist': items, 'namespaces': namespaces.items, 'selected_namespace': selected_namespace})

def storageclasses(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.StorageV1Api()
    try:
        result = api_instance.list_storage_class()
        items = result.items
    except Exception:
        items = []
    return render(request, 'kubernetes/storageclasses.html', {'sclist': items})

def csinodes(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api_instance = client.StorageV1Api()
    try:
        result = api_instance.list_csi_node()
        items = result.items
    except Exception:
        items = []
    return render(request, 'kubernetes/csinodes.html', {'csinodelist': items})

def podlogs(request, namespace, pod_name, container_name):
    """Pod日志查看页面"""
    return render(request, 'kubernetes/podlogs.html', {
        'namespace': namespace,
        'pod_name': pod_name,
        'container_name': container_name,
        'cluster_id': request.session.get('currentclusterid')
    })


def _probe_cluster(cluster):
    config_path = None
    card = {
        'name': cluster.clustername or 'Kubernetes',
        'version': '-',
        'server': cluster.server or '-',
        'node_total': 0,
        'node_ready': 0,
        'pod_count': 0,
        'cpu_percent': None,
        'memory_percent': None,
        'status': '连接不上',
        'badge': 'layui-badge layui-bg-red',
        'source': '真实集群',
        'is_real': True,
        'offline': True,
        'nodes': [],
    }
    try:
        config_path = get_kubeconfig_from_db(cluster.id)
        _patch_rest_client_timeout()
        config.load_kube_config(config_path)
        v1 = client.CoreV1Api()
        nodes = v1.list_node(_request_timeout=5)
        node_items = nodes.items or []
        ready_count = 0
        for node in node_items:
            for condition in node.status.conditions or []:
                if condition.type == 'Ready' and condition.status == 'True':
                    ready_count += 1
        version = node_items[0].status.node_info.kubelet_version if node_items and node_items[0].status.node_info else '-'

        pod_count = 0
        try:
            pod_list = v1.list_pod_for_all_namespaces(watch=False, _request_timeout=5)
            pod_count = len(pod_list.items or [])
        except Exception:
            pod_count = '-'

        node_previews = []
        for node in node_items:
            node_ready = any(
                condition.type == 'Ready' and condition.status == 'True'
                for condition in (node.status.conditions or [])
            )
            addresses = node.status.addresses or []
            node_ip = next(
                (address.address for address in addresses if address.type == 'InternalIP'),
                next(
                    (address.address for address in addresses if address.type == 'ExternalIP'),
                    '-',
                ),
            )
            node_previews.append({
                'name': node.metadata.name,
                'ip': node_ip,
                'status': 'Ready' if node_ready else 'NotReady',
                'cpu': '-',
                'memory': '-',
            })

        cpu_percent = None
        memory_percent = None
        try:
            metrics = client.CustomObjectsApi().list_cluster_custom_object(
                group='metrics.k8s.io', version='v1beta1', plural='nodes',
            )
            usage_values = []
            cpu_alloc_total = 0
            for node in node_items:
                cpu_alloc_total += _parse_cpu_to_millicores((node.status.allocatable or {}).get('cpu', '0'))
            for item in (metrics.get('items') or []):
                usage = item.get('usage', {})
                usage_values.append(_parse_cpu_to_millicores(usage.get('cpu', '0')))
            if usage_values and cpu_alloc_total:
                cpu_percent = round(sum(usage_values) / cpu_alloc_total * 100, 1)
        except Exception:
            pass

        card.update({
            'version': version,
            'node_total': len(node_items),
            'node_ready': ready_count,
            'nodes': node_previews,
            'pod_count': pod_count,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'status': '已连接',
            'badge': 'layui-badge layui-bg-green',
            'offline': False,
        })
    except Exception:
        card['status'] = '连接不上'
        card['badge'] = 'layui-badge layui-bg-red'
        card['offline'] = True
    finally:
        cleanup_temp_config(config_path)
    return card


def _real_home_clusters():
    return [_probe_cluster(cluster) for cluster in Cluster.objects.all()[:4]]


def _simulated_node_previews(cluster_name, total, ready_count):
    nodes = []
    cpu_values = [34.2, 22.8, 51.5, 18.7, 67.3, 42.1, 29.6, 55.9, 36.4, 48.8, 24.2, 60.7]
    memory_values = [51.3, 43.8, 66.2, 38.1, 79.4, 58.7, 46.5, 71.8, 52.9, 63.4, 41.2, 74.6]
    for index in range(total):
        octet = (index // 250) + 10
        host = (index % 250) + 1
        nodes.append({
            'name': '%s-node-%02d' % (cluster_name, index + 1),
            'ip': '10.0.%s.%s' % (octet, host),
            'status': 'Ready' if index < ready_count else 'NotReady',
            'cpu': cpu_values[index % len(cpu_values)],
            'memory': memory_values[index % len(memory_values)],
        })
    return nodes


def resources(request):
    if request.path_info == '/':
        real_clusters = _real_home_clusters()
        simulated = home_cluster_previews()
        for cluster in simulated:
            if not cluster.get('nodes'):
                cluster['nodes'] = _simulated_node_previews(
                    cluster['name'], cluster['node_total'], cluster['node_ready']
                )
        return render(request, 'home_overview.html', {
            'cloud_pie_items': [
                {
                    'provider_name': item['provider_name'],
                    'color': item['color'],
                    'data_json': json.dumps(item['data'], ensure_ascii=False),
                }
                for item in home_cloud_pies()
            ],
            'clusters': simulated + real_clusters,
        })

    error = _load_kubeconfig_or_error(request)
    if error:
        return error

    v1 = client.CoreV1Api()
    custom_api = client.CustomObjectsApi()
    cluster_error = None

    # --- Node data ---
    try:
        node_list = v1.list_node()
        node_items = node_list.items
    except Exception:
        node_items = []
        cluster_error = "Kubernetes 集群连接失败，当前页面显示为空数据。"

    # Try node metrics (metrics-server may not be installed)
    node_metrics_available = True
    node_metrics_map = {}
    try:
        node_metrics_result = custom_api.list_cluster_custom_object(
            group="metrics.k8s.io", version="v1beta1", plural="nodes"
        )
        for item in node_metrics_result.get('items', []):
            name = item['metadata']['name']
            usage = item.get('usage', {})
            node_metrics_map[name] = {
                'cpu': _parse_cpu_to_millicores(usage.get('cpu', '0')),
                'memory': _parse_memory_to_bytes(usage.get('memory', '0Ki')),
            }
    except Exception:
        node_metrics_available = False

    # Try pod metrics
    pod_metrics_available = True
    pod_metrics_list = []
    try:
        pod_metrics_result = custom_api.list_cluster_custom_object(
            group="metrics.k8s.io", version="v1beta1", plural="pods"
        )
        for item in pod_metrics_result.get('items', []):
            ns = item['metadata']['namespace']
            pname = item['metadata']['name']
            total_cpu = 0
            total_mem = 0
            for container in item.get('containers', []):
                usage = container.get('usage', {})
                total_cpu += _parse_cpu_to_millicores(usage.get('cpu', '0'))
                total_mem += _parse_memory_to_bytes(usage.get('memory', '0Ki'))
            pod_metrics_list.append({
                'namespace': ns,
                'name': pname,
                'cpu_millicores': total_cpu,
                'memory_bytes': total_mem,
            })
    except Exception:
        pod_metrics_available = False

    # Get all pods for per-node count and namespace aggregation
    try:
        pod_list = v1.list_pod_for_all_namespaces(watch=False)
        pod_items = pod_list.items
    except Exception:
        pod_items = []

    # Count pods per node
    pod_count_per_node = {}
    for pod in pod_items:
        node = pod.spec.node_name or ''
        if node:
            pod_count_per_node[node] = pod_count_per_node.get(node, 0) + 1

    # Build node data
    node_data = []
    for node in node_items:
        name = node.metadata.name
        capacity = node.status.capacity or {}
        allocatable = node.status.allocatable or {}

        cpu_cap = _parse_cpu_to_millicores(capacity.get('cpu', '0'))
        cpu_alloc = _parse_cpu_to_millicores(allocatable.get('cpu', '0'))
        mem_cap = _parse_memory_to_bytes(capacity.get('memory', '0Ki'))
        mem_alloc = _parse_memory_to_bytes(allocatable.get('memory', '0Ki'))
        pods_max = int(allocatable.get('pods', '0'))

        metrics = node_metrics_map.get(name, {})
        cpu_used = metrics.get('cpu')
        mem_used = metrics.get('memory')

        cpu_pct = round((cpu_used / cpu_alloc * 100), 1) if cpu_used is not None and cpu_alloc > 0 else None
        mem_pct = round((mem_used / mem_alloc * 100), 1) if mem_used is not None and mem_alloc > 0 else None

        node_data.append({
            'name': name,
            'cpu_used': _format_cpu_core_str(cpu_used),
            'cpu_total': _format_cpu_core_str(cpu_alloc),
            'cpu_percent': cpu_pct,
            'cpu_bar_color': _bar_color(cpu_pct),
            'memory_used': _format_bytes_human(mem_used) if mem_used is not None else None,
            'memory_total': _format_bytes_human(mem_alloc),
            'memory_percent': mem_pct,
            'memory_bar_color': _bar_color(mem_pct),
            'pods_running': pod_count_per_node.get(name, 0),
            'pods_max': pods_max,
        })

    # --- Namespace data ---
    try:
        ns_list = v1.list_namespace()
        ns_items = ns_list.items
    except Exception:
        ns_items = []

    # Aggregate pod requests/limits per namespace
    namespace_aggregates = {}
    for pod in pod_items:
        ns = pod.metadata.namespace
        if ns not in namespace_aggregates:
            namespace_aggregates[ns] = {
                'pod_count': 0, 'cpu_requests': 0, 'cpu_limits': 0,
                'mem_requests': 0, 'mem_limits': 0,
            }
        namespace_aggregates[ns]['pod_count'] += 1
        if pod.spec.containers:
            for container in pod.spec.containers:
                requests = container.resources.requests or {} if container.resources else {}
                limits = container.resources.limits or {} if container.resources else {}
                namespace_aggregates[ns]['cpu_requests'] += _parse_cpu_to_millicores(requests.get('cpu', '0'))
                namespace_aggregates[ns]['cpu_limits'] += _parse_cpu_to_millicores(limits.get('cpu', '0'))
                namespace_aggregates[ns]['mem_requests'] += _parse_memory_to_bytes(requests.get('memory', '0'))
                namespace_aggregates[ns]['mem_limits'] += _parse_memory_to_bytes(limits.get('memory', '0'))

    # Aggregate pod metrics per namespace
    ns_metrics_map = {}
    if pod_metrics_available:
        for pm in pod_metrics_list:
            ns = pm['namespace']
            if ns not in ns_metrics_map:
                ns_metrics_map[ns] = {'cpu': 0, 'memory': 0}
            ns_metrics_map[ns]['cpu'] += pm['cpu_millicores']
            ns_metrics_map[ns]['memory'] += pm['memory_bytes']

    # Build namespace data
    selected_namespace = request.GET.get('namespace') or ''
    ns_data = []
    for ns_obj in ns_items:
        ns_name = ns_obj.metadata.name
        if selected_namespace and ns_name != selected_namespace:
            continue
        agg = namespace_aggregates.get(ns_name, {
            'pod_count': 0, 'cpu_requests': 0, 'cpu_limits': 0,
            'mem_requests': 0, 'mem_limits': 0,
        })
        metrics = ns_metrics_map.get(ns_name, {})

        ns_data.append({
            'name': ns_name,
            'pod_count': agg['pod_count'],
            'cpu_requests': _format_cpu_core_str(agg['cpu_requests']),
            'cpu_limits': _format_cpu_core_str(agg['cpu_limits']),
            'mem_requests': _format_bytes_human(agg['mem_requests']),
            'mem_limits': _format_bytes_human(agg['mem_limits']),
            'cpu_usage': _format_cpu_core_str(metrics.get('cpu')),
            'mem_usage': _format_bytes_human(metrics.get('memory')),
        })

    return render(request, 'kubernetes/resources.html', {
        'node_data': node_data,
        'ns_data': ns_data,
        'node_metrics_available': node_metrics_available,
        'pod_metrics_available': pod_metrics_available,
        'namespaces': ns_items,
        'selected_namespace': selected_namespace,
        'cluster_error': cluster_error,
        'cloud_providers': provider_summaries(),
        'cloud_instances': get_instances('aliyun')[:4],
        'home_mode': request.path_info == '/',
        'home_cloud_pie_items': [
            {
                'provider_name': item['provider_name'],
                'color': item['color'],
                'data_json': json.dumps(item['data'], ensure_ascii=False),
            }
            for item in home_cloud_pies()
        ],
        'home_k8s_clusters': home_cluster_previews(),
    })


def nodes(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    v1 = client.CoreV1Api()
    try:
        node_list = v1.list_node()
        node_items = node_list.items
    except Exception:
        node_items = []
    # Build node summary data
    node_data = []
    for node in node_items:
        info = {
            'name': node.metadata.name,
            'status': 'Unknown',
            'roles': [],
            'version': node.status.node_info.kubelet_version if node.status.node_info else '',
            'os': node.status.node_info.os_image if node.status.node_info else '',
            'kernel': node.status.node_info.kernel_version if node.status.node_info else '',
            'container_runtime': node.status.node_info.container_runtime_version if node.status.node_info else '',
            'create_time': ages(node.metadata.creation_timestamp),
            'labels': [],
            'taints': [],
            'conditions': [],
            'capacity_cpu': node.status.capacity.get('cpu', '') if node.status.capacity else '',
            'capacity_memory': _format_bytes_human(_parse_memory_to_bytes(node.status.capacity.get('memory', '0Ki'))) if node.status.capacity else '',
            'capacity_pods': node.status.capacity.get('pods', '') if node.status.capacity else '',
            'addresses': [],
        }
        # Roles
        for label in node.metadata.labels or {}:
            if label.startswith('node-role.kubernetes.io/'):
                info['roles'].append(label.replace('node-role.kubernetes.io/', ''))
        if not info['roles']:
            info['roles'].append('worker')
        # Conditions
        for cond in node.status.conditions or []:
            info['conditions'].append({'type': cond.type, 'status': cond.status, 'reason': cond.reason or ''})
            if cond.type == 'Ready' and cond.status == 'True':
                info['status'] = 'Ready'
            elif cond.type == 'Ready' and cond.status != 'True':
                info['status'] = 'NotReady'
        # Labels
        for k, v in (node.metadata.labels or {}).items():
            info['labels'].append({'key': k, 'value': v})
        # Taints
        for t in node.spec.taints or []:
            info['taints'].append({'key': t.key, 'value': t.value or '', 'effect': t.effect})
        # Addresses
        for addr in node.status.addresses or []:
            info['addresses'].append({'type': addr.type, 'address': addr.address})
        node_data.append(info)
    return render(request, 'kubernetes/nodes.html', {'nodelist': node_data})


def namespaces(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    v1 = client.CoreV1Api()
    try:
        ns_list = v1.list_namespace()
        ns_items = ns_list.items
    except Exception:
        ns_items = []
    ns_name = request.GET.get('nsname') or ''
    if ns_name:
        ns_items = [ns for ns in ns_items if ns_name.lower() in ns.metadata.name.lower()]
    ns_data = []
    for ns in ns_items:
        ns_data.append({
            'name': ns.metadata.name,
            'status': ns.status.phase,
            'create_time': ages(ns.metadata.creation_timestamp),
            'labels': [{'key': k, 'value': v} for k, v in (ns.metadata.labels or {}).items()],
        })
    return render(request, 'kubernetes/namespaces.html', {
        'nslist': ns_data,
        'ns_name': ns_name,
    })


def events(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    v1 = client.CoreV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    event_type = request.GET.get('type') or ''
    event_name = request.GET.get('eventname') or ''
    try:
        if selected_namespace:
            event_list = v1.list_namespaced_event(namespace=selected_namespace)
        else:
            event_list = v1.list_event_for_all_namespaces()
        event_items = event_list.items
    except Exception:
        event_items = []
    # Filter
    if event_type:
        event_items = [e for e in event_items if e.type.lower() == event_type.lower()]
    if event_name:
        event_items = [e for e in event_items if event_name.lower() in (e.involved_object.name or '').lower()]
    # Sort by last timestamp desc
    try:
        event_items.sort(key=lambda x: x.last_timestamp or x.metadata.creation_timestamp, reverse=True)
    except Exception:
        pass
    # Build event data
    event_data = []
    for e in event_items[:200]:
        event_data.append({
            'type': e.type,
            'reason': e.reason,
            'message': e.message,
            'object_kind': e.involved_object.kind,
            'object_name': e.involved_object.name,
            'namespace': e.metadata.namespace,
            'count': e.count,
            'first_time': ages(e.first_timestamp) if e.first_timestamp else '',
            'last_time': ages(e.last_timestamp) if e.last_timestamp else '',
            'source': f"{e.source.component}/{e.source.host}" if e.source and e.source.component else '',
        })
    paginator = Paginator(event_data, 20)
    page_number = request.GET.get('page')
    try:
        event_page = paginator.get_page(page_number)
    except:
        event_page = paginator.get_page(1)
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/events.html', {
        'eventlist': event_page,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
        'event_type': event_type,
        'event_name': event_name,
    })


def serviceaccounts(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    v1 = client.CoreV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    sa_name = request.GET.get('saname') or ''
    try:
        if selected_namespace:
            result = v1.list_namespaced_service_account(namespace=selected_namespace)
        else:
            result = v1.list_service_account_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    if sa_name:
        items = [i for i in items if sa_name.lower() in i.metadata.name.lower()]
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/serviceaccounts.html', {
        'salist': items,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
        'sa_name': sa_name,
    })


def hpa(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api = client.AutoscalingV2Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api.list_namespaced_horizontal_pod_autoscaler(namespace=selected_namespace)
        else:
            result = api.list_horizontal_pod_autoscaler_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/hpa.html', {
        'hpalist': items,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
    })


def roles(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api = client.RbacAuthorizationV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api.list_namespaced_role(namespace=selected_namespace)
        else:
            result = api.list_role_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/roles.html', {
        'rolelist': items,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
    })


def rolebindings(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api = client.RbacAuthorizationV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api.list_namespaced_role_binding(namespace=selected_namespace)
        else:
            result = api.list_role_binding_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/rolebindings.html', {
        'rblist': items,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
    })


def resourcequotas(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    v1 = client.CoreV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = v1.list_namespaced_resource_quota(namespace=selected_namespace)
        else:
            result = v1.list_resource_quota_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/resourcequotas.html', {
        'quotalist': items,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
    })


def limitranges(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    v1 = client.CoreV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = v1.list_namespaced_limit_range(namespace=selected_namespace)
        else:
            result = v1.list_limit_range_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/limitranges.html', {
        'lrlist': items,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
    })


def networkpolicies(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api = client.NetworkingV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api.list_namespaced_network_policy(namespace=selected_namespace)
        else:
            result = api.list_network_policy_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/networkpolicies.html', {
        'nplist': items,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
    })


def pdb(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api = client.PolicyV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api.list_namespaced_pod_disruption_budget(namespace=selected_namespace)
        else:
            result = api.list_pod_disruption_budget_for_all_namespaces()
        items = result.items
    except Exception:
        items = []
    core_v1_api = client.CoreV1Api()
    namespaces = _safe_list_namespaces()
    return render(request, 'kubernetes/pdb.html', {
        'pdblist': items,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
    })


def crds(request):
    error = _load_kubeconfig_or_error(request)
    if error:
        return error
    api = client.ApiextensionsV1Api()
    try:
        result = api.list_custom_resource_definition()
        items = result.items
    except Exception:
        items = []
    crd_name = request.GET.get('crdname') or ''
    if crd_name:
        items = [i for i in items if crd_name.lower() in i.metadata.name.lower()]
    return render(request, 'kubernetes/crds.html', {'crdlist': items, 'crd_name': crd_name})
