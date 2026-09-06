from django.shortcuts import render, HttpResponse
from kubernetes import client, config
from django.http import JsonResponse
from k8sdashboard.utils.kubernetes_config import get_kubeconfig_from_db, NoClusterConfiguredError, _patch_rest_client_timeout
from k8sdashboard.models import have_authority
from django.core.paginator import Paginator
import json


def rollbacklist(request):
    try:
        _patch_rest_client_timeout()
        config.load_kube_config(get_kubeconfig_from_db(request.session.get('currentclusterid')))
    except NoClusterConfiguredError:
        return render(request, 'common/no_cluster.html', {
            'cluster_id': request.session.get('currentclusterid')
        })
    api_instance = client.AppsV1Api()
    selected_namespace = request.GET.get('namespace') or ''
    try:
        if selected_namespace:
            result = api_instance.list_namespaced_replica_set(namespace=selected_namespace)
        else:
            result = api_instance.list_replica_set_for_all_namespaces()
        items = result.items
    except Exception:
        items = []

    # 过滤出有owner是Deployment的ReplicaSet
    rollback_items = []
    for rs in items:
        if rs.metadata.owner_references:
            for owner in rs.metadata.owner_references:
                if owner.kind == 'Deployment':
                    rollback_items.append({
                        'name': rs.metadata.name,
                        'namespace': rs.metadata.namespace,
                        'deployment': owner.name,
                        'images': [{'name': c.name, 'image': c.image}
                                   for c in rs.spec.template.spec.containers],
                        'replicas': rs.spec.replicas,
                        'creation_time': rs.metadata.creation_timestamp,
                    })
                    break

    paginator = Paginator(rollback_items, 15)
    page_number = request.GET.get('page')
    try:
        page = paginator.get_page(page_number)
    except:
        page = paginator.get_page(1)

    core_v1_api = client.CoreV1Api()
    namespaces = core_v1_api.list_namespace()
    return render(request, 'rollback/rollbacklist.html', {
        'rollbacklist': page,
        'namespaces': namespaces.items,
        'selected_namespace': selected_namespace,
    })
