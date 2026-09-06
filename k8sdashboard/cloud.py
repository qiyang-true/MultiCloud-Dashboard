import json

from django.http import Http404, JsonResponse
from django.shortcuts import render
from k8sdashboard.models import CloudCredential
from k8sdashboard.aliyun_client import (
    get_aliyun_data,
    get_aliyun_disks,
    get_aliyun_security_groups,
    get_aliyun_snapshots,
    get_aliyun_vpcs,
    invalidate_cache,
)
from k8sdashboard.cloud_fake_data import FAKE_RESOURCES, SERVICE_PAGES
from k8sdashboard.cloud_aws_fake_data import AWS_OVERVIEW_RESOURCES, AWS_SERVICE_PAGES

SERVICE_PAGES.update(AWS_SERVICE_PAGES)


def home_cloud_pies():
    return [
        {
            'provider_name': '阿里云',
            'color': '#FF6A00',
            'data': [
                {'name': 'ECS', 'value': 620, 'color': '#FF6A00'},
                {'name': '云盘', 'value': 1280, 'color': '#2F9D62'},
                {'name': 'RDS', 'value': 96, 'color': '#0E7EEB'},
                {'name': 'Redis', 'value': 128, 'color': '#5B6AF0'},
                {'name': 'OSS', 'value': 260, 'color': '#F0A020'},
            ],
        },
        {
            'provider_name': '腾讯云',
            'color': '#0052D9',
            'data': [
                {'name': 'CVM', 'value': 350, 'color': '#0052D9'},
                {'name': 'CBS', 'value': 980, 'color': '#3AAFA9'},
                {'name': 'CDB', 'value': 82, 'color': '#6C8EF5'},
                {'name': 'Redis', 'value': 64, 'color': '#8A6DDE'},
                {'name': 'COS', 'value': 180, 'color': '#F0A020'},
            ],
        },
        {
            'provider_name': 'AWS',
            'color': '#232F3E',
            'data': [
                {'name': 'EC2', 'value': 280, 'color': '#E47911'},
                {'name': 'EBS', 'value': 1120, 'color': '#0E7EEB'},
                {'name': 'RDS', 'value': 84, 'color': '#2F9D62'},
                {'name': 'Lambda', 'value': 126, 'color': '#5B6AF0'},
                {'name': 'S3', 'value': 150, 'color': '#F0A020'},
            ],
        },
    ]


def home_cluster_previews():
    return [
        {
            'name': 'prod-k8s-mall',
            'version': 'v1.30.1',
            'node_total': 12,
            'node_ready': 12,
            'cpu_percent': 36.8,
            'memory_percent': 58.4,
            'pod_count': 426,
            'status': '运行正常',
            'badge': 'layui-badge layui-bg-green',
        },
        {
            'name': 'prod-k8s-ai',
            'version': 'v1.29.5',
            'node_total': 8,
            'node_ready': 7,
            'cpu_percent': 62.1,
            'memory_percent': 74.5,
            'pod_count': 231,
            'status': '部分节点异常',
            'badge': 'layui-badge layui-bg-orange',
        },
        {
            'name': 'staging-k8s-ops',
            'version': 'v1.30.1',
            'node_total': 5,
            'node_ready': 5,
            'cpu_percent': 21.4,
            'memory_percent': 44.2,
            'pod_count': 118,
            'status': '运行正常',
            'badge': 'layui-badge layui-bg-green',
        },
        {
            'name': 'dev-k8s-practice',
            'version': 'v1.28.2',
            'node_total': 3,
            'node_ready': 2,
            'cpu_percent': 12.6,
            'memory_percent': 33.8,
            'pod_count': 42,
            'status': '部分节点异常',
            'badge': 'layui-badge layui-bg-orange',
        },
    ]


def home_cluster_previews():
    return [
        {
            'name': 'aliyun-prod',
            'cloud': '阿里云',
            'source': '阿里云',
            'version': 'v1.24.2',
            'node_total': 12,
            'node_ready': 12,
            'cpu_percent': 36.8,
            'memory_percent': 58.4,
            'pod_count': 426,
            'status': '运行正常',
            'badge': 'layui-badge layui-bg-green',
        },
        {
            'name': 'aliyun-uat',
            'cloud': '阿里云',
            'source': '阿里云',
            'version': 'v1.26.5',
            'node_total': 8,
            'node_ready': 8,
            'cpu_percent': 62.1,
            'memory_percent': 74.5,
            'pod_count': 231,
            'status': '运行正常',
            'badge': 'layui-badge layui-bg-green',
        },
        {
            'name': 'aws-prod',
            'cloud': 'AWS',
            'source': 'AWS EKS',
            'version': '1.25.1',
            'node_total': 10,
            'node_ready': 10,
            'cpu_percent': 41.5,
            'memory_percent': 63.2,
            'pod_count': 318,
            'status': '运行正常',
            'badge': 'layui-badge layui-bg-green',
        },
        {
            'name': 'aws-uat',
            'cloud': 'AWS',
            'source': 'AWS EKS',
            'version': '1.27.3',
            'node_total': 6,
            'node_ready': 5,
            'cpu_percent': 57.8,
            'memory_percent': 71.9,
            'pod_count': 154,
            'status': '部分节点异常',
            'badge': 'layui-badge layui-bg-orange',
        },
    ]


def _region_filter(request, items):
    selected_region = request.GET.get('region', '').strip()
    regions = sorted({item.get('region') for item in items if item.get('region')})
    if selected_region:
        items = [item for item in items if item.get('region') == selected_region]
    return items, selected_region, regions


def _fake_fallback(items, selected_region, errors, key):
    if not selected_region and not items and not errors:
        return FAKE_RESOURCES.get(key, [])
    return items


def _pie_segments(items):
    segments = []
    start = 0.0
    for item in items:
        percent = float(item.get('percent') or 0)
        segments.append({
            'label': item.get('label') or item.get('region') or '',
            'count': item.get('count', 0),
            'percent': percent,
            'color': item.get('color', '#009688'),
            'start': round(start * 3.6, 2),
            'end': round((start + percent) * 3.6, 2),
        })
        start += percent
    return segments


def _overview_preview_instances(instance_list, provider_key):
    templates = [
        ('data-etl-09', 'cn-guangzhou', 'ecs.g7.2xlarge', '8 vCPU / 32 GiB', '47.111.92.21', 36.4, 61.2),
        ('order-worker-10', 'cn-nanjing', 'ecs.c7.2xlarge', '8 vCPU / 16 GiB', '47.99.105.32', 28.7, 55.3),
        ('search-node-11', 'ap-southeast-1', 'ecs.g6.4xlarge', '16 vCPU / 64 GiB', '47.88.22.77', 52.1, 78.5),
        ('video-encoder-12', 'cn-zhangjiakou', 'ecs.gn7i-c8g1.2xlarge', '8 vCPU / 32 GiB', '39.105.66.18', 67.3, 82.4),
        ('web-stage-13', 'cn-chengdu', 'ecs.c7.xlarge', '4 vCPU / 8 GiB', '106.52.36.14', 8.8, 34.1),
        ('backup-node-14', 'cn-huhehaote', 'ecs.g7.xlarge', '4 vCPU / 16 GiB', '47.100.45.88', 4.2, 26.7),
    ]
    if provider_key == 'aws':
        templates = [
            ('web-prod-09', 'us-east-2', 'm6i.2xlarge', '8 vCPU / 32 GiB', '3.145.20.34', 33.5, 59.2),
            ('worker-batch-10', 'ap-northeast-1', 'c6i.2xlarge', '8 vCPU / 16 GiB', '13.112.55.21', 44.6, 64.8),
            ('analytics-node-11', 'ca-central-1', 'r6i.xlarge', '4 vCPU / 32 GiB', '35.182.82.44', 51.2, 71.3),
            ('ml-trainer-12', 'sa-east-1', 'g4dn.2xlarge', '8 vCPU / 32 GiB', '18.228.14.70', 76.4, 85.1),
            ('dev-web-13', 'ap-northeast-2', 't3.large', '2 vCPU / 8 GiB', '3.35.211.5', 12.1, 40.4),
            ('archive-node-14', 'eu-central-1', 'm5.large', '2 vCPU / 8 GiB', '18.156.61.9', 6.3, 31.5),
        ]

    extras = []
    for index, (name, region, spec, resource, public_ip, cpu, memory) in enumerate(templates, start=len(instance_list) + 1):
        item = {
            'instance_id': 'i-preview-%04d' % index,
            'name': name,
            'region': region,
            'spec': spec,
            'resource': resource,
            'public_ip': public_ip,
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': '包年包月',
            'cpu_percent': cpu,
            'cpu_color': '#5FB878',
            'memory_percent': memory,
            'memory_color': '#0E7EEB',
        }
        if provider_key == 'aws':
            item['instance_id'] = 'i-preview-%04d' % (index + 500)
            item['charge'] = 'On-Demand'
        extras.append(item)
    return instance_list + extras


PROVIDERS = {
    'aliyun': {
        'key': 'aliyun',
        'name': '阿里云',
        'color': '#FF6A00',
        'instance_label': 'ECS',
        'storage_label': 'OSS',
        'default_region': 'cn-hangzhou',
        'top_menu_id': '20',
        'parent_menu_id': '110',
        'child_menu_id': '111',
    },
    'tencent': {
        'key': 'tencent',
        'name': '腾讯云',
        'color': '#0052D9',
        'instance_label': 'CVM',
        'storage_label': 'COS',
        'default_region': 'ap-shanghai',
        'top_menu_id': '21',
        'parent_menu_id': '114',
        'child_menu_id': '115',
    },
    'aws': {
        'key': 'aws',
        'name': 'AWS',
        'color': '#232F3E',
        'instance_label': 'EC2',
        'storage_label': 'S3',
        'default_region': 'ap-southeast-1',
        'top_menu_id': '22',
        'parent_menu_id': '118',
        'child_menu_id': '119',
    },
}


INSTANCES = {
    'aliyun': [
        {
            'instance_id': 'i-bp1h2x3a7k9m0n5q',
            'name': 'web-prod-01',
            'region': '华东1（杭州）',
            'spec': 'ecs.g7.xlarge',
            'resource': '4 vCPU / 16 GiB',
            'public_ip': '47.98.120.11',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': '包年包月',
        },
        {
            'instance_id': 'i-bp1h2x3a7k9m0n5r',
            'name': 'app-test-02',
            'region': '华北2（北京）',
            'spec': 'ecs.c7.large',
            'resource': '2 vCPU / 8 GiB',
            'public_ip': '120.92.19.32',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': '按量付费',
        },
        {
            'instance_id': 'i-bp1h2x3a7k9m0n5s',
            'name': 'cache-build-01',
            'region': '华东1（杭州）',
            'spec': 'ecs.g6.4xlarge',
            'resource': '16 vCPU / 64 GiB',
            'public_ip': '47.98.121.76',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': '包年包月',
        },
        {
            'instance_id': 'i-bp1h2x3a7k9m0n5t',
            'name': 'old-dev-host',
            'region': '华南1（深圳）',
            'spec': 'ecs.t5-c1m1.large',
            'resource': '2 vCPU / 4 GiB',
            'public_ip': '139.199.54.18',
            'status': '已停止',
            'badge': 'layui-badge layui-bg-gray',
            'charge': '包年包月',
        },
        {
            'instance_id': 'i-bp1h2x3a7k9m0n5u',
            'name': 'data-etl-01',
            'region': '华北2（北京）',
            'spec': 'ecs.r7.2xlarge',
            'resource': '8 vCPU / 64 GiB',
            'public_ip': '120.92.20.88',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': '按量付费',
        },
    ],
    'tencent': [
        {
            'instance_id': 'ins-2h4k8p0x',
            'name': 'mall-gateway-01',
            'region': '上海',
            'spec': 'S5.MEDIUM4',
            'resource': '4 vCPU / 16 GiB',
            'public_ip': '129.211.98.21',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': '包年包月',
        },
        {
            'instance_id': 'ins-3m5n9q1y',
            'name': 'mall-order-02',
            'region': '广州',
            'spec': 'SA2.LARGE8',
            'resource': '8 vCPU / 32 GiB',
            'public_ip': '119.29.115.44',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': '包年包月',
        },
        {
            'instance_id': 'ins-4n6p0r2z',
            'name': 'ci-runner-01',
            'region': '北京',
            'spec': 'S5.SMALL1',
            'resource': '2 vCPU / 8 GiB',
            'public_ip': '115.159.26.73',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': '按量付费',
        },
        {
            'instance_id': 'ins-5o7q1s3a',
            'name': 'legacy-report',
            'region': '上海',
            'spec': 'S2.SMALL2',
            'resource': '2 vCPU / 4 GiB',
            'public_ip': '129.204.56.91',
            'status': '已停止',
            'badge': 'layui-badge layui-bg-gray',
            'charge': '包年包月',
        },
    ],
    'aws': [
        {
            'instance_id': 'i-0a1b2c3d4e5f67890',
            'name': 'eks-worker-eu-01',
            'region': 'ap-southeast-1',
            'spec': 'm6i.xlarge',
            'resource': '4 vCPU / 16 GiB',
            'public_ip': '13.250.44.18',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': 'On-Demand',
        },
        {
            'instance_id': 'i-0f1a2b3c4d5e6f789',
            'name': 'lambda-builder-01',
            'region': 'us-east-1',
            'spec': 'c6i.2xlarge',
            'resource': '8 vCPU / 16 GiB',
            'public_ip': '18.209.211.32',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': 'Spot',
        },
        {
            'instance_id': 'i-0a9b8c7d6e5f43210',
            'name': 'postgres-standby',
            'region': 'ap-southeast-1',
            'spec': 'r6i.xlarge',
            'resource': '4 vCPU / 32 GiB',
            'public_ip': '13.251.18.77',
            'status': '运行中',
            'badge': 'layui-badge layui-bg-green',
            'charge': 'On-Demand',
        },
        {
            'instance_id': 'i-0c1d2e3f4a5b67890',
            'name': 'dev-box-retired',
            'region': 'us-west-2',
            'spec': 't3.medium',
            'resource': '2 vCPU / 4 GiB',
            'public_ip': '34.217.72.19',
            'status': '已停止',
            'badge': 'layui-badge layui-bg-gray',
            'charge': 'Reserved',
        },
    ],
}


BUCKETS = {
    'aliyun': [
        {
            'bucket_name': 'prod-mall-static',
            'region': 'oss-cn-hangzhou',
            'object_count': '128,462',
            'storage_size': '316.7 GiB',
            'acl': '公共读',
            'badge': 'layui-badge layui-bg-green',
        },
        {
            'bucket_name': 'data-backup-daily',
            'region': 'oss-cn-beijing',
            'object_count': '9,810',
            'storage_size': '1.28 TiB',
            'acl': '私有',
            'badge': 'layui-badge layui-bg-gray',
        },
    ],
    'tencent': [
        {
            'bucket_name': 'mall-media-1250000000',
            'region': 'ap-shanghai',
            'object_count': '86,120',
            'storage_size': '204.3 GiB',
            'acl': '公有读私有写',
            'badge': 'layui-badge layui-bg-green',
        },
        {
            'bucket_name': 'log-archive-1250000000',
            'region': 'ap-guangzhou',
            'object_count': '41,906',
            'storage_size': '820.5 GiB',
            'acl': '私有读写',
            'badge': 'layui-badge layui-bg-gray',
        },
    ],
    'aws': [
        {
            'bucket_name': 'app-user-uploads',
            'region': 'ap-southeast-1',
            'object_count': '54,221',
            'storage_size': '188.2 GiB',
            'acl': 'Public Read',
            'badge': 'layui-badge layui-bg-green',
        },
        {
            'bucket_name': 'cloudwatch-archive',
            'region': 'us-east-1',
            'object_count': '3,114',
            'storage_size': '640.9 GiB',
            'acl': 'Private',
            'badge': 'layui-badge layui-bg-gray',
        },
    ],
}


def _get_provider(provider_key):
    provider = PROVIDERS.get(provider_key)
    if not provider:
        raise Http404('Cloud provider not found')
    return provider


def get_instances(provider_key):
    return INSTANCES.get(provider_key, [])


def provider_summaries():
    summaries = []
    for key, provider in PROVIDERS.items():
        instance_list = INSTANCES.get(key, [])
        running = len([item for item in instance_list if item.get('status') == '运行中'])
        summaries.append({
            'provider': provider,
            'instances': len(instance_list),
            'running': running,
            'stopped': len(instance_list) - running,
            'buckets': len(BUCKETS.get(key, [])),
            'instance_label': provider['instance_label'],
            'storage_label': provider['storage_label'],
        })
    return summaries


def overview(request, provider_key):
    provider = _get_provider(provider_key)
    instance_list = INSTANCES.get(provider_key, [])
    bucket_list = BUCKETS.get(provider_key, [])
    running = len([item for item in instance_list if item.get('status') == '运行中'])
    stopped = len(instance_list) - running
    return render(request, 'cloud/overview.html', {
        'provider': provider,
        'instances': instance_list[:3],
        'buckets': bucket_list,
        'summary': {
            'instances': len(instance_list),
            'running': running,
            'stopped': stopped,
            'buckets': len(bucket_list),
        },
    })


def instances(request, provider_key):
    provider = _get_provider(provider_key)
    return render(request, 'cloud/instances.html', {
        'provider': provider,
        'instances': INSTANCES.get(provider_key, []),
        'summary': provider_summaries(),
    })


def buckets(request, provider_key):
    provider = _get_provider(provider_key)
    return render(request, 'cloud/buckets.html', {
        'provider': provider,
        'buckets': BUCKETS.get(provider_key, []),
    })


def credentials(request, provider_key='aliyun'):
    provider = _get_provider(provider_key)
    saved = False

    if request.method == 'POST':
        access_key = request.POST.get('access_key', '').strip()
        secret_key = request.POST.get('secret_key', '').strip()
        region = request.POST.get('default_region', '').strip()

        account = CloudCredential.objects.filter(provider=provider_key).first()
        if not account and not access_key and not secret_key:
            if request.is_ajax():
                return JsonResponse({'status': 0, 'info': '请填写 AccessKey 信息'})
        if not account:
            account = CloudCredential(provider=provider_key)
        if access_key:
            account.access_key = access_key
        if secret_key:
            account.secret_key = secret_key
        if region:
            account.default_region = region
        account.save()
        invalidate_cache()
        if request.is_ajax():
            return JsonResponse({'status': 1, 'info': '保存成功'})
        saved = True

    account = CloudCredential.objects.filter(provider=provider_key).first()
    return render(request, 'cloud/credentials.html', {
        'provider': provider,
        'saved': saved,
        'configured': bool(account and (account.access_key or account.secret_key)),
        'current_access_key': account.access_key if account else '',
        'has_secret': bool(account and account.secret_key),
        'current_region': account.default_region if account else '',
    })


def _live_provider_data(provider_key):
    if provider_key == 'aliyun':
        data = get_aliyun_data()
        return data.get('instances', []), data.get('buckets', []), data.get('errors', [])
    return INSTANCES.get(provider_key, []), BUCKETS.get(provider_key, []), []


def _running_count(instance_list):
    return len([item for item in instance_list if item.get('status') == '运行中'])


def get_instances(provider_key):
    return _live_provider_data(provider_key)[0]


def get_buckets(provider_key):
    return _live_provider_data(provider_key)[1]


def provider_summaries():
    summaries = []
    for key, provider in PROVIDERS.items():
        instance_list, bucket_list, _ = _live_provider_data(key)
        running = _running_count(instance_list)
        summaries.append({
            'provider': provider,
            'instances': len(instance_list),
            'running': running,
            'stopped': len(instance_list) - running,
            'buckets': len(bucket_list),
            'instance_label': provider['instance_label'],
            'storage_label': provider['storage_label'],
        })
    return summaries


def overview(request, provider_key):
    provider = _get_provider(provider_key)
    all_errors = []
    if provider_key == 'aliyun':
        instance_list = FAKE_RESOURCES.get('instances', [])
        bucket_list = FAKE_RESOURCES.get('buckets', [])
        disk_list = FAKE_RESOURCES.get('disks', [])
        group_list = FAKE_RESOURCES.get('security_groups', [])
        vpc_list = FAKE_RESOURCES.get('vpcs', [])
        snapshot_list = FAKE_RESOURCES.get('snapshots', [])
    elif provider_key == 'aws':
        instance_list = AWS_OVERVIEW_RESOURCES.get('instances', [])
        bucket_list = AWS_OVERVIEW_RESOURCES.get('buckets', [])
        disk_list = AWS_OVERVIEW_RESOURCES.get('disks', [])
        group_list = AWS_OVERVIEW_RESOURCES.get('security_groups', [])
        vpc_list = AWS_OVERVIEW_RESOURCES.get('vpcs', [])
        snapshot_list = AWS_OVERVIEW_RESOURCES.get('snapshots', [])
    else:
        instance_list, bucket_list, _ = _live_provider_data(provider_key)
        disk_list = _fake_fallback([], '', [], 'disks')
        group_list = _fake_fallback([], '', [], 'security_groups')
        vpc_list = _fake_fallback([], '', [], 'vpcs')
        snapshot_list = _fake_fallback([], '', [], 'snapshots')

    if provider_key == 'aliyun':
        overview_counts = {
            'ecs': 620, 'running': 586, 'disks': 1280, 'security_groups': 320,
            'vpcs': 96, 'buckets': 260, 'snapshots': 680,
        }
    elif provider_key == 'aws':
        overview_counts = {
            'ecs': 280, 'running': 264, 'disks': 1120, 'security_groups': 240,
            'vpcs': 70, 'buckets': 150, 'snapshots': 760,
        }
    else:
        overview_counts = {
            'ecs': len(instance_list), 'running': _running_count(instance_list),
            'disks': len(disk_list), 'security_groups': len(group_list),
            'vpcs': len(vpc_list), 'buckets': len(bucket_list),
            'snapshots': len(snapshot_list),
        }

    for item in instance_list:
        if item.get('cpu_percent') is not None and item.get('memory_percent') is None:
            memory_percent = round(min(95.0, max(22.0, item['cpu_percent'] * 1.8 + 24.0)), 1)
            item['memory_percent'] = memory_percent
            item['memory_color'] = '#0E7EEB'

    if provider_key in ('aliyun', 'aws'):
        instance_list = _overview_preview_instances(instance_list, provider_key)

    running = overview_counts.get('running', _running_count(instance_list))
    stopped = overview_counts.get('ecs', len(instance_list)) - running
    resource_counts = [
        {'key': 'ecs', 'label': 'ECS 实例', 'count': len(instance_list), 'color': '#FF6A00'},
        {'key': 'disks', 'label': '云盘', 'count': len(disk_list), 'color': '#2F9D62'},
        {'key': 'security_groups', 'label': '安全组', 'count': len(group_list), 'color': '#0E7EEB'},
        {'key': 'vpcs', 'label': 'VPC', 'count': len(vpc_list), 'color': '#5B6AF0'},
        {'key': 'buckets', 'label': 'OSS 存储桶', 'count': len(bucket_list), 'color': '#F0A020'},
        {'key': 'snapshots', 'label': '快照', 'count': len(snapshot_list), 'color': '#8A6DDE'},
    ]
    for item in resource_counts:
        if item['key'] == 'ecs':
            item['label'] = '%s 实例' % provider['instance_label']
        elif item['key'] == 'disks':
            item['label'] = 'EBS 存储卷' if provider_key == 'aws' else '云盘'
        elif item['key'] == 'buckets':
            item['label'] = '%s 存储桶' % provider['storage_label']
    for item in resource_counts:
        item['count'] = overview_counts.get(item['key'], item['count'])
    total_resources = sum([item['count'] for item in resource_counts])
    resource_bars = [
        {
            'label': item['label'],
            'count': item['count'],
            'color': item['color'],
            'percent': round(item['count'] * 100 / total_resources, 1) if total_resources else 0,
        }
        for item in resource_counts
    ]

    all_items = instance_list + bucket_list + disk_list + group_list + vpc_list + snapshot_list
    region_counts = {}
    for item in all_items:
        region = item.get('region') or ''
        if region.startswith('oss-'):
            region = region[4:]
        if not region:
            continue
        region_counts[region] = region_counts.get(region, 0) + 1
    raw_region_total = sum(region_counts.values())
    if raw_region_total:
        scale_ratio = total_resources / raw_region_total
        region_counts = {
            region: max(1, round(count * scale_ratio))
            for region, count in region_counts.items()
        }
    if provider_key == 'aliyun':
        shanghai_count = int(total_resources * 0.76)
        hangzhou_count = int(total_resources * 0.11)
        beijing_count = int(total_resources * 0.08)
        region_counts = {
            'cn-shanghai': shanghai_count,
            'cn-hangzhou': hangzhou_count,
            'cn-beijing': beijing_count,
            'cn-shenzhen': max(1, total_resources - shanghai_count - hangzhou_count - beijing_count),
        }
    region_bars = []
    display_region_total = 0
    if region_counts:
        region_colors = ['#0E7EEB', '#2F9D62', '#FF6A00', '#8A6DDE', '#F0A020', '#E04F5F', '#16A6A6']
        sorted_regions = sorted(region_counts, key=region_counts.get, reverse=True)[:4]
        for index, region in enumerate(sorted_regions):
            region_bars.append({
                'region': region,
                'count': region_counts[region],
                'color': region_colors[index % len(region_colors)],
            })
        display_region_total = sum(item['count'] for item in region_bars)
        previous_percent = 0.0
        for index, item in enumerate(region_bars):
            if index == len(region_bars) - 1:
                item['percent'] = round(100.0 - previous_percent, 1)
            else:
                item['percent'] = round(item['count'] * 100 / display_region_total, 1)
                previous_percent += item['percent']
    resource_pie = _pie_segments(resource_bars)
    region_pie = _pie_segments(region_bars)
    resource_pie_json = json.dumps([
        {
            'name': segment['label'],
            'value': segment['count'],
            'itemStyle': {'color': segment['color']},
        }
        for segment in resource_pie
    ], ensure_ascii=False)
    region_pie_json = json.dumps([
        {
            'name': segment['label'],
            'value': segment['count'],
            'itemStyle': {'color': segment['color']},
        }
        for segment in region_pie
    ], ensure_ascii=False)

    cpu_values = [item.get('cpu_percent') for item in instance_list if item.get('cpu_percent') is not None]
    cpu_avg = round(sum(cpu_values) / len(cpu_values), 1) if cpu_values else 0
    cpu_sample = next((item for item in instance_list if item.get('cpu_percent') is not None), None)
    memory_values = [item.get('memory_percent') for item in instance_list if item.get('memory_percent') is not None]
    memory_avg = round(sum(memory_values) / len(memory_values), 1) if memory_values else 0
    memory_sample = next((item for item in instance_list if item.get('memory_percent') is not None), None)

    latest = []
    for resource_type, source in [
        ('ECS', instance_list), ('云盘', disk_list), ('安全组', group_list),
        ('VPC', vpc_list), ('OSS', bucket_list), ('快照', snapshot_list),
    ]:
        for item in source[:1]:
            latest.append({
                'type': resource_type,
                'name': item.get('name') or item.get('disk_name') or item.get('group_name') or item.get('vpc_name') or item.get('bucket_name') or item.get('snapshot_name'),
                'resource_id': item.get('instance_id') or item.get('disk_id') or item.get('group_id') or item.get('vpc_id') or item.get('bucket_name') or item.get('snapshot_id'),
                'region': item.get('region', ''),
                'status': item.get('status') or item.get('acl') or '-',
                'badge': item.get('badge', 'layui-badge layui-bg-gray'),
            })

    return render(request, 'cloud/overview.html', {
        'provider': provider,
        'instances': instance_list[:10],
        'buckets': bucket_list,
        'cloud_error': all_errors,
        'summary': {
            'instances': overview_counts.get('ecs', len(instance_list)),
            'running': running,
            'stopped': stopped,
            'buckets': overview_counts.get('buckets', len(bucket_list)),
            'disks': overview_counts.get('disks', len(disk_list)),
            'security_groups': overview_counts.get('security_groups', len(group_list)),
            'vpcs': overview_counts.get('vpcs', len(vpc_list)),
            'snapshots': overview_counts.get('snapshots', len(snapshot_list)),
        },
        'resource_bars': resource_bars,
        'region_bars': region_bars,
        'resource_pie': resource_pie,
        'region_pie': region_pie,
        'resource_pie_json': resource_pie_json,
        'region_pie_json': region_pie_json,
        'total_resource_count': total_resources,
        'total_region_count': display_region_total,
        'cpu_avg': cpu_avg,
        'cpu_sample': cpu_sample,
        'memory_avg': memory_avg,
        'memory_sample': memory_sample,
        'latest': latest,
    })


def instances(request, provider_key):
    provider = _get_provider(provider_key)
    instance_list, _, errors = _live_provider_data(provider_key)
    instance_list, selected_region, regions = _region_filter(request, instance_list)
    instance_list = _fake_fallback(instance_list, selected_region, errors, 'instances')
    return render(request, 'cloud/instances.html', {
        'provider': provider,
        'instances': instance_list,
        'regions': regions,
        'selected_region': selected_region,
        'cloud_error': errors,
        'summary': provider_summaries(),
    })


def buckets(request, provider_key):
    provider = _get_provider(provider_key)
    _, bucket_list, errors = _live_provider_data(provider_key)
    bucket_list, selected_region, regions = _region_filter(request, bucket_list)
    bucket_list = _fake_fallback(bucket_list, selected_region, errors, 'buckets')
    return render(request, 'cloud/buckets.html', {
        'provider': provider,
        'buckets': bucket_list,
        'regions': regions,
        'selected_region': selected_region,
        'cloud_error': errors,
    })


def instance_detail(request, provider_key, instance_id):
    provider = _get_provider(provider_key)
    instance_list, _, errors = _live_provider_data(provider_key)
    instance = next((item for item in instance_list if item.get('instance_id') == instance_id), None)
    if not instance:
        raise Http404('Instance not found')
    return render(request, 'cloud/instance_detail.html', {
        'provider': provider,
        'instance': instance,
        'cloud_error': errors,
    })


def disks(request):
    provider = _get_provider('aliyun')
    data = get_aliyun_disks()
    disk_list, selected_region, regions = _region_filter(request, data.get('items', []))
    disk_list = _fake_fallback(disk_list, selected_region, data.get('errors', []), 'disks')
    return render(request, 'cloud/disks.html', {
        'provider': provider,
        'disks': disk_list,
        'regions': regions,
        'selected_region': selected_region,
        'cloud_error': data.get('errors', []),
    })


def security_groups(request):
    provider = _get_provider('aliyun')
    data = get_aliyun_security_groups()
    group_list, selected_region, regions = _region_filter(request, data.get('items', []))
    group_list = _fake_fallback(group_list, selected_region, data.get('errors', []), 'security_groups')
    return render(request, 'cloud/security_groups.html', {
        'provider': provider,
        'security_groups': group_list,
        'regions': regions,
        'selected_region': selected_region,
        'cloud_error': data.get('errors', []),
    })


def vpcs(request):
    provider = _get_provider('aliyun')
    data = get_aliyun_vpcs()
    vpc_list, selected_region, regions = _region_filter(request, data.get('items', []))
    vpc_list = _fake_fallback(vpc_list, selected_region, data.get('errors', []), 'vpcs')
    return render(request, 'cloud/vpcs.html', {
        'provider': provider,
        'vpcs': vpc_list,
        'regions': regions,
        'selected_region': selected_region,
        'cloud_error': data.get('errors', []),
    })


def snapshots(request):
    provider = _get_provider('aliyun')
    data = get_aliyun_snapshots()
    snapshot_list, selected_region, regions = _region_filter(request, data.get('items', []))
    snapshot_list = _fake_fallback(snapshot_list, selected_region, data.get('errors', []), 'snapshots')
    return render(request, 'cloud/snapshots.html', {
        'provider': provider,
        'snapshots': snapshot_list,
        'regions': regions,
        'selected_region': selected_region,
        'cloud_error': data.get('errors', []),
    })


def service_page(request, service_key, provider_key='aliyun'):
    provider = _get_provider(provider_key)
    page = SERVICE_PAGES.get(service_key)
    if not page:
        raise Http404('Service page not found')
    return render(request, 'cloud/service_page.html', {
        'provider': provider,
        'page': page,
    })
