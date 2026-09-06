import hashlib
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

try:
    import oss2
    from alibabacloud_ecs20140526 import models as ecs_models
    from alibabacloud_ecs20140526.client import Client as EcsClient
    from alibabacloud_tea_openapi import models as open_api_models
    CLOUD_SDK_AVAILABLE = True
except ImportError:
    CLOUD_SDK_AVAILABLE = False

from k8sdashboard.models import CloudCredential
from k8sdashboard.cloud_fake_data import FAKE_RESOURCES


STATUS_TEXT = {
    'Running': '运行中',
    'Stopped': '已停止',
    'Starting': '启动中',
    'Stopping': '停止中',
    'Pending': '创建中',
    'Expired': '已过期',
    'Not-applicable': '未启动',
}

STATUS_BADGE = {
    'Running': 'layui-badge layui-bg-green',
    'Stopped': 'layui-badge layui-bg-gray',
    'Starting': 'layui-badge layui-bg-orange',
    'Stopping': 'layui-badge layui-bg-orange',
    'Pending': 'layui-badge layui-bg-blue',
    'Expired': 'layui-badge layui-bg-red',
}

CHARGE_TEXT = {
    'PrePaid': '包年包月',
    'PostPaid': '按量付费',
    'SpotPaid': '抢占式实例',
    'Spot': '抢占式实例',
}

ACL_TEXT = {
    'private': '私有',
    'public-read': '公共读',
    'public-read-write': '公共读写',
    'default': '继承 Bucket',
}


_CACHE = {}
_RESOURCE_CACHE = {}
_LOCK = threading.Lock()
CACHE_TTL = 120

DISK_STATUS_TEXT = {
    'In_use': '使用中',
    'Available': '可用',
    'Attaching': '挂载中',
    'Detaching': '卸载中',
    'Creating': '创建中',
    'ReIniting': '初始化中',
}

SECURITY_GROUP_TYPE_TEXT = {
    'normal': '普通安全组',
    'enterprise': '企业安全组',
}

VPC_STATUS_TEXT = {
    'Available': '可用',
    'Pending': '创建中',
}

SNAPSHOT_STATUS_TEXT = {
    'progressing': '创建中',
    'accomplished': '已完成',
    'failed': '失败',
}


def _human_size(size):
    try:
        value = float(size)
    except (TypeError, ValueError):
        return '-'
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if abs(value) < 1024.0 or unit == 'TiB':
            return '%s %s' % (round(value), unit)
        value /= 1024.0
    return '%s TiB' % round(value)


def _percent_color(percent):
    if percent is None:
        return '#ccc'
    if percent > 80:
        return '#FF5722'
    if percent > 50:
        return '#FFB800'
    return '#5FB878'


def _get_account():
    account = CloudCredential.objects.filter(provider='aliyun').first()
    if not account or not account.access_key or not account.secret_key:
        return None
    return account


def _cache_key():
    account = _get_account()
    if not account:
        return 'aliyun:not-configured'
    return 'aliyun:' + hashlib.sha256(account.access_key.encode('utf-8')).hexdigest()[:16]


def _region_list(account):
    from alibabacloud_ecs20140526 import models as em
    client = EcsClient(open_api_models.Config(
        access_key_id=account.access_key,
        access_key_secret=account.secret_key,
        region_id='cn-hangzhou',
        endpoint='ecs.cn-hangzhou.aliyuncs.com',
    ))
    data = client.describe_regions(em.DescribeRegionsRequest()).body.to_map()
    regions = (data.get('Regions') or {}).get('Region') or []
    return [region.get('RegionId') for region in regions if region.get('RegionId')]


def _query_instances(account):
    regions = []
    try:
        regions = _region_list(account)
    except Exception as exc:
        errors = ['获取地域列表失败: %s' % exc]
        regions = [account.default_region or 'cn-hangzhou']

    def query_region(region):
        try:
            client = EcsClient(open_api_models.Config(
                access_key_id=account.access_key,
                access_key_secret=account.secret_key,
                region_id=region,
                endpoint='ecs.%s.aliyuncs.com' % region,
            ))
            page = 1
            region_items = []
            while True:
                req = ecs_models.DescribeInstancesRequest(
                    region_id=region,
                    page_number=page,
                    page_size=100,
                )
                data = client.describe_instances(req).body.to_map()
                raw_items = (data.get('Instances') or {}).get('Instance') or []
                total = data.get('TotalCount') or 0
                for raw in raw_items:
                    region_items.append(_map_instance(raw))
                if len(region_items) >= total or len(raw_items) < 100:
                    break
                page += 1
            return region_items, None
        except Exception as exc:
            return [], '%s 查询失败: %s' % (region, exc)

    items = []
    errors = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(query_region, region) for region in regions]
        for future in futures:
            region_items, error = future.result()
            items.extend(region_items)
            if error:
                errors.append(error)

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(
            lambda item: item.update(_query_instance_usage(account, item['region'], item['instance_id'])),
            items,
        ))

    if items:
        errors = []
    items.sort(key=lambda item: (item['status'], item['region'], item['name']))
    return items, errors


def _map_instance(raw):
    instance_id = raw.get('InstanceId') or ''
    instance_name = raw.get('InstanceName') or raw.get('HostName') or instance_id
    public_ips = (raw.get('PublicIpAddress') or {}).get('IpAddress') or []
    eip = ((raw.get('EipAddress') or {}).get('IpAddress')) or ''
    if eip:
        public_ips.append(eip)
    public_ip = public_ips[0] if public_ips else '-'
    private_ips = ((raw.get('VpcAttributes') or {}).get('PrivateIpAddress') or {}).get('IpAddress') or []
    private_ip = ', '.join(private_ips) if private_ips else '-'
    vpc_attributes = raw.get('VpcAttributes') or {}
    os_name = raw.get('OSName') or raw.get('OSNameEn') or '-'

    cpu = raw.get('Cpu') or 0
    memory_mib = raw.get('Memory') or 0
    memory_gib = max(1, round(memory_mib / 1024))
    status = raw.get('Status') or ''

    return {
        'instance_id': instance_id,
        'name': instance_name,
        'region': raw.get('RegionId') or '',
        'spec': raw.get('InstanceType') or '',
        'resource': '%s vCPU / %s GiB' % (cpu, memory_gib),
        'public_ip': public_ip,
        'status': STATUS_TEXT.get(status, status),
        'badge': STATUS_BADGE.get(status, 'layui-badge layui-bg-gray'),
        'charge': CHARGE_TEXT.get(raw.get('InstanceChargeType') or '', raw.get('InstanceChargeType') or '-'),
        'private_ip': private_ip,
        'vpc_id': vpc_attributes.get('VpcId') or '-',
        'vswitch_id': vpc_attributes.get('VSwitchId') or '-',
        'zone_id': raw.get('ZoneId') or '-',
        'os_name': os_name,
        'image_id': raw.get('ImageId') or '-',
        'host_name': raw.get('HostName') or '-',
        'creation_time': raw.get('CreationTime') or '-',
        'expired_time': raw.get('ExpiredTime') or '-',
    }


def _query_cpu_usage(account, region, instance_id):
    try:
        client = EcsClient(open_api_models.Config(
            access_key_id=account.access_key,
            access_key_secret=account.secret_key,
            region_id=region,
            endpoint='ecs.%s.aliyuncs.com' % region,
        ))
        now = datetime.now(timezone.utc)
        start_time = (now - timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        req = ecs_models.DescribeInstanceMonitorDataRequest(
            instance_id=instance_id,
            start_time=start_time,
            end_time=end_time,
            period=60,
        )
        data = client.describe_instance_monitor_data(req).body.to_map()
        points = data.get('MonitorData', {}).get('InstanceMonitorData', [])
        values = [float(point.get('CPU')) for point in points if point.get('CPU') is not None]
        return round(sum(values) / len(values), 1) if values else None
    except Exception:
        return None


def _query_instance_usage(account, region, instance_id):
    cpu_percent = _query_cpu_usage(account, region, instance_id)
    return {
        'cpu_percent': cpu_percent,
        'cpu_color': _percent_color(cpu_percent),
    }


def _map_resource_item(resource_type, raw):
    if resource_type == 'disks':
        status = raw.get('Status') or ''
        return {
            'disk_id': raw.get('DiskId') or '-',
            'disk_name': raw.get('DiskName') or raw.get('DiskId') or '-',
            'region': raw.get('RegionId') or '',
            'size': '%s GiB' % (raw.get('Size') or 0),
            'category': raw.get('Category') or '-',
            'status': DISK_STATUS_TEXT.get(status, status or '-'),
            'badge': 'layui-badge layui-bg-green' if status == 'In_use' else 'layui-badge layui-bg-gray',
            'instance_id': raw.get('InstanceId') or '-',
            'zone_id': raw.get('ZoneId') or '-',
            'charge': CHARGE_TEXT.get(raw.get('DiskChargeType') or '', raw.get('DiskChargeType') or '-'),
            'encrypted': '是' if raw.get('Encrypted') else '否',
            'creation_time': raw.get('CreationTime') or '-',
            'expired_time': raw.get('ExpiredTime') or '-',
        }
    if resource_type == 'security_groups':
        group_type = raw.get('SecurityGroupType') or ''
        return {
            'group_id': raw.get('SecurityGroupId') or '-',
            'group_name': raw.get('SecurityGroupName') or '-',
            'region': raw.get('RegionId') or '',
            'group_type': SECURITY_GROUP_TYPE_TEXT.get(group_type, group_type or '-'),
            'description': raw.get('Description') or '-',
            'rule_count': raw.get('RuleCount') or 0,
            'vpc_id': raw.get('VpcId') or '-',
            'creation_time': raw.get('CreationTime') or '-',
        }
    if resource_type == 'vpcs':
        status = raw.get('Status') or ''
        switches = ((raw.get('VSwitchIds') or {}).get('VSwitchId')) or []
        return {
            'vpc_id': raw.get('VpcId') or '-',
            'vpc_name': raw.get('VpcName') or '-',
            'cidr_block': raw.get('CidrBlock') or '-',
            'region': raw.get('RegionId') or '-',
            'status': VPC_STATUS_TEXT.get(status, status or '-'),
            'badge': 'layui-badge layui-bg-green' if status == 'Available' else 'layui-badge layui-bg-gray',
            'switch_count': len(switches),
            'creation_time': raw.get('CreationTime') or '-',
        }
    if resource_type == 'snapshots':
        status = raw.get('Status') or ''
        return {
            'snapshot_id': raw.get('SnapshotId') or '-',
            'snapshot_name': raw.get('SnapshotName') or '-',
            'region': raw.get('RegionId') or '',
            'source_disk_id': raw.get('SourceDiskId') or '-',
            'source_disk_size': '%s GiB' % (raw.get('SourceDiskSize') or 0),
            'status': SNAPSHOT_STATUS_TEXT.get(status, status or '-'),
            'badge': 'layui-badge layui-bg-green' if status == 'accomplished' else 'layui-badge layui-bg-gray',
            'progress': raw.get('Progress') or '-',
            'creation_time': raw.get('CreationTime') or '-',
            'last_modified_time': raw.get('LastModifiedTime') or '-',
        }
    return {}


def _query_resource(account, resource_type):
    regions = []
    try:
        regions = _region_list(account)
    except Exception as exc:
        errors = ['获取地域列表失败: %s' % exc]
        regions = [account.default_region or 'cn-hangzhou']

    container_map = {
        'disks': ('Disks', 'Disk'),
        'security_groups': ('SecurityGroups', 'SecurityGroup'),
        'vpcs': ('Vpcs', 'Vpc'),
        'snapshots': ('Snapshots', 'Snapshot'),
    }
    top_key, child_key = container_map[resource_type]
    page_size = 50 if resource_type == 'vpcs' else 100

    def query_region(region):
        try:
            client = EcsClient(open_api_models.Config(
                access_key_id=account.access_key,
                access_key_secret=account.secret_key,
                region_id=region,
                endpoint='ecs.%s.aliyuncs.com' % region,
            ))
            page = 1
            region_items = []
            while True:
                request = getattr(ecs_models, 'Describe%sRequest' % {
                    'disks': 'Disks',
                    'security_groups': 'SecurityGroups',
                    'vpcs': 'Vpcs',
                    'snapshots': 'Snapshots',
                }[resource_type])(region_id=region, page_number=page, page_size=page_size)
                method = getattr(client, 'describe_%s' % resource_type)
                data = method(request).body.to_map()
                raw_items = (data.get(top_key) or {}).get(child_key) or []
                total = data.get('TotalCount') or 0
                for raw in raw_items:
                    region_items.append(_map_resource_item(resource_type, raw))
                if len(region_items) >= total or len(raw_items) < page_size:
                    break
                page += 1
            return region_items, None
        except Exception as exc:
            return [], '%s 查询失败: %s' % (region, exc)

    items = []
    errors = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(query_region, region) for region in regions]
        for future in futures:
            region_items, error = future.result()
            items.extend(region_items)
            if error:
                errors.append(error)
    if items:
        errors = []
    return items, errors


def _get_resource_data(resource_type):
    if not CLOUD_SDK_AVAILABLE:
        key_map = {
            'disks': 'disks',
            'security_groups': 'security_groups',
            'vpcs': 'vpcs',
            'snapshots': 'snapshots',
        }
        return {'items': FAKE_RESOURCES.get(key_map.get(resource_type, ''), []), 'errors': []}
    account = _get_account()
    if not account:
        return {'items': [], 'errors': ['未配置阿里云 AccessKey']}
    key = _cache_key() + ':' + resource_type
    now = time.time()
    with _LOCK:
        cached = _RESOURCE_CACHE.get(key)
        if cached and now - cached['time'] < CACHE_TTL:
            return cached['data']
    items, errors = _query_resource(account, resource_type)
    data = {'items': items, 'errors': errors}
    with _LOCK:
        _RESOURCE_CACHE[key] = {'time': time.time(), 'data': data}
    return data


def _query_buckets(account):
    errors = []
    region = account.default_region or 'cn-hangzhou'
    auth = oss2.Auth(account.access_key, account.secret_key)
    service = oss2.Service(auth, 'https://oss-%s.aliyuncs.com' % region)
    bucket_items = []
    marker = ''

    try:
        while True:
            result = service.list_buckets(marker=marker, max_keys=100)
            bucket_items.extend(result.buckets or [])
            if not result.is_truncated:
                break
            marker = result.next_marker
    except Exception as exc:
        errors.append('获取 OSS Bucket 列表失败: %s' % exc)
        return [], errors

    buckets = []
    for bucket_info in bucket_items:
        bucket_name = bucket_info.name
        endpoint = bucket_info.extranet_endpoint
        if endpoint and not endpoint.startswith('http'):
            endpoint = 'https://' + endpoint
        if not endpoint:
            endpoint = 'https://oss-%s.aliyuncs.com' % region

        stat = None
        acl = None
        try:
            bucket = oss2.Bucket(auth, endpoint, bucket_name)
            stat = bucket.get_bucket_stat()
            acl = bucket.get_bucket_acl().acl
        except Exception:
            pass

        object_count = format(stat.object_count, ',') if stat else '-'
        storage_size = _human_size(stat.storage_size_in_bytes) if stat else '-'
        acl_name = ACL_TEXT.get(acl, acl or '-')
        buckets.append({
            'bucket_name': bucket_name,
            'region': bucket_info.location or bucket_info.region or region,
            'object_count': object_count,
            'storage_size': storage_size,
            'acl': acl_name,
            'badge': 'layui-badge layui-bg-green' if acl in ('public-read', 'public-read-write') else 'layui-badge layui-bg-gray',
        })
    return buckets, errors


def _load_data():
    if not CLOUD_SDK_AVAILABLE:
        return {
            'instances': FAKE_RESOURCES.get('instances', []),
            'buckets': FAKE_RESOURCES.get('buckets', []),
            'errors': [],
        }
    account = _get_account()
    if not account:
        return {'instances': [], 'buckets': [], 'errors': ['未配置阿里云 AccessKey']}
    instances, instance_errors = _query_instances(account)
    buckets, bucket_errors = _query_buckets(account)
    return {
        'instances': instances,
        'buckets': buckets,
        'errors': instance_errors + bucket_errors,
    }


def get_aliyun_data():
    key = _cache_key()
    now = time.time()
    with _LOCK:
        cached = _CACHE.get(key)
        if cached and now - cached['time'] < CACHE_TTL:
            return cached['data']

    data = _load_data()
    with _LOCK:
        _CACHE[key] = {'time': time.time(), 'data': data}
    return data


def get_aliyun_disks():
    return _get_resource_data('disks')


def get_aliyun_security_groups():
    return _get_resource_data('security_groups')


def get_aliyun_vpcs():
    return _get_resource_data('vpcs')


def get_aliyun_snapshots():
    return _get_resource_data('snapshots')


def invalidate_cache():
    with _LOCK:
        _CACHE.clear()
        _RESOURCE_CACHE.clear()
