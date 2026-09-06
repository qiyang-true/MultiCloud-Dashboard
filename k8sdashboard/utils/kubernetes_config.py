from kubernetes import client, config
from kubernetes.client.rest import RESTClientObject
from k8sdashboard.models import Cluster
import tempfile
import os
import yaml
import urllib3
from django.shortcuts import render

K8S_TIMEOUT = 5
_rest_client_patched = False


def _patch_rest_client_timeout():
    """Monkey-patch RESTClientObject to add default timeout and disable retries."""
    global _rest_client_patched
    if _rest_client_patched:
        return

    _orig_init = RESTClientObject.__init__
    _orig_request = RESTClientObject.request

    def patched_init(self, configuration, pools_size=4, maxsize=None):
        _orig_init(self, configuration, pools_size=pools_size, maxsize=maxsize)
        # Disable retries so timeout is immediate (no 3x retry = 15s wait)
        self.pool_manager.connection_pool_kw['retries'] = 0

    def request_with_timeout(self, method, url, query_params=None, headers=None,
                             body=None, post_params=None, _preload_content=True,
                             _request_timeout=None):
        if _request_timeout is None:
            _request_timeout = K8S_TIMEOUT
        return _orig_request(self, method, url,
                             query_params=query_params,
                             headers=headers,
                             body=body,
                             post_params=post_params,
                             _preload_content=_preload_content,
                             _request_timeout=_request_timeout)

    RESTClientObject.__init__ = patched_init
    RESTClientObject.request = request_with_timeout
    _rest_client_patched = True


class NoClusterConfiguredError(Exception):
    """没有配置集群时抛出的异常"""
    pass


def get_kubeconfig_from_db(cluster_id=None, manager_id=None):
    """
    从数据库获取kubeconfig配置

    :param cluster_id: 集群ID，如果指定则获取特定集群
    :param manager_id: 管理员ID，如果指定则获取该管理员的集群
    :return: 临时kubeconfig文件路径
    """
    cluster = None
    try:
        if cluster_id:
            try:
                cluster = Cluster.objects.get(id=cluster_id)
            except Cluster.DoesNotExist:
                cluster = Cluster.objects.first()
        elif manager_id:
            cluster = Cluster.objects.filter(managerid=manager_id).first()
        else:
            cluster = Cluster.objects.first()

        if not cluster:
            raise NoClusterConfiguredError("没有找到可用的集群配置，请先在系统中添加Kubernetes集群")

        # 构建kubeconfig字典
        kubeconfig_dict = {
            'apiVersion': 'v1',
            'kind': 'Config',
            'clusters': [{
                'name': cluster.clustername,
                'cluster': {
                    'server': cluster.server
                }
            }],
            'users': [{
                'name': cluster.username,
                'user': {}
            }],
            'contexts': [{
                'name': f"{cluster.clustername}@{cluster.username}",
                'context': {
                    'cluster': cluster.clustername,
                    'user': cluster.username
                }
            }],
            'current-context': f"{cluster.clustername}@{cluster.username}"
        }

        # 添加集群证书（如果存在）
        if cluster.certificate_authority_data:
            kubeconfig_dict['clusters'][0]['cluster']['certificate-authority-data'] = cluster.certificate_authority_data

        # 添加用户认证信息
        if cluster.token:
            kubeconfig_dict['users'][0]['user']['token'] = cluster.token
        elif cluster.client_certificate_data and cluster.client_key_data:
            kubeconfig_dict['users'][0]['user']['client-certificate-data'] = cluster.client_certificate_data
            kubeconfig_dict['users'][0]['user']['client-key-data'] = cluster.client_key_data

        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(kubeconfig_dict, temp_file, default_flow_style=False)
        temp_file.close()

        return temp_file.name

    except NoClusterConfiguredError:
        raise
    except Exception as e:
        raise Exception(f"获取kubeconfig失败: {str(e)}")


def load_kubeconfig_from_db(cluster_id=None, manager_id=None):
    """
    从数据库加载kubeconfig并配置kubernetes客户端
    
    :param cluster_id: 集群ID
    :param manager_id: 管理员ID
    :return: 临时文件路径（用于后续清理）
    """
    config_path = get_kubeconfig_from_db(cluster_id, manager_id)
    _patch_rest_client_timeout()
    config.load_kube_config(config_path)
    return config_path


def cleanup_temp_config(config_path):
    """
    清理临时kubeconfig文件
    
    :param config_path: 临时文件路径
    """
    try:
        if config_path and os.path.exists(config_path):
            os.unlink(config_path)
    except Exception:
        pass


def get_current_cluster_from_session(request):
    """
    从session获取当前选中的集群ID
    
    :param request: Django请求对象
    :return: 集群ID或None
    """
    return request.session.get('currentclusterid')


def get_current_manager_from_session(request):
    """
    从session获取当前登录的管理员ID
    
    :param request: Django请求对象
    :return: 管理员ID或None
    """
    return request.session.get('userid')
