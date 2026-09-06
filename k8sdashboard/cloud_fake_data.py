SERVICE_PAGES = {
    'ack': {
        'title': '容器服务 ACK',
        'subtitle': 'Kubernetes 集群管理',
        'columns': ['集群 ID', '集群名称', 'K8s 版本', '地域', '节点数', '状态'],
        'rows': [
            ['c-2ze8m9q0x7a1', 'prod-k8s-mall', '1.30.1', 'cn-hangzhou', '5', '运行中'],
            ['c-3f9n0r1y8b2', 'staging-k8s-ai', '1.28.3', 'cn-beijing', '3', '运行中'],
            ['c-4g0p1s2z9c3', 'dev-k8s-web', '1.30.1', 'cn-shanghai', '1', '运行中'],
        ],
    },
    'fc': {
        'title': '函数计算 FC',
        'subtitle': 'Serverless 函数',
        'columns': ['函数名称', '运行时', '内存', '超时时间', '地域', '状态'],
        'rows': [
            ['image-resize', 'Python 3.10', '512 MB', '60 秒', 'cn-hangzhou', '已发布'],
            ['order-webhook', 'Node.js 18', '256 MB', '30 秒', 'cn-shanghai', '已发布'],
            ['daily-report', 'Python 3.10', '128 MB', '120 秒', 'cn-beijing', '测试中'],
        ],
    },
    'rds': {
        'title': '云数据库 RDS MySQL',
        'subtitle': '关系型数据库',
        'columns': ['实例 ID', '实例名称', '版本', '规格', '地域', '状态'],
        'rows': [
            ['rm-2ze8m9q0x7a1', 'prod-mall-mysql', 'MySQL 8.0', '4C16G 高可用', 'cn-hangzhou', '运行中'],
            ['rm-3f9n0r1y8b2', 'staging-order-db', 'MySQL 5.7', '2C8G 基础版', 'cn-beijing', '运行中'],
            ['rm-4g0p1s2z9c3', 'backup-report-db', 'MySQL 8.0', '2C4G 基础版', 'cn-shanghai', '已停止'],
        ],
    },
    'redis': {
        'title': '云数据库 Redis',
        'subtitle': '缓存数据库',
        'columns': ['实例 ID', '实例名称', '版本', '规格', '地域', '状态'],
        'rows': [
            ['r-2ze8m9q0x7a1', 'prod-session-cache', 'Redis 7.0', '16G 集群版', 'cn-hangzhou', '运行中'],
            ['r-3f9n0r1y8b2', 'search-hot-cache', 'Redis 6.0', '8G 标准版', 'cn-beijing', '运行中'],
        ],
    },
    'mongodb': {
        'title': '云数据库 MongoDB',
        'subtitle': '文档数据库',
        'columns': ['实例 ID', '实例名称', '版本', '规格', '存储空间', '状态'],
        'rows': [
            ['dds-2ze8m9q0x7a1', 'prod-user-profile', 'MongoDB 6.0', '4C16G 副本集', '100 GB', '运行中'],
            ['dds-3f9n0r1y8b2', 'dev-log-archive', 'MongoDB 5.0', '2C8G 副本集', '50 GB', '已停止'],
        ],
    },
    'slb': {
        'title': '负载均衡 SLB',
        'subtitle': '应用型负载均衡 ALB / SLB',
        'columns': ['实例 ID', '实例名称', '类型', 'VIP', '地域', '状态'],
        'rows': [
            ['alb-2ze8m9q0x7a1', 'prod-mall-gateway', 'ALB', '47.98.100.21', 'cn-hangzhou', '运行中'],
            ['slb-3f9n0r1y8b2', 'internal-api-lb', 'SLB', '100.98.20.35', 'cn-beijing', '运行中'],
        ],
    },
    'nat': {
        'title': 'NAT 网关',
        'subtitle': '公网 NAT / VPC NAT',
        'columns': ['网关 ID', '名称', '规格', 'SNAT 条目', '地域', '状态'],
        'rows': [
            ['ngw-2ze8m9q0x7a1', 'prod-outbound-nat', '中型', '12', 'cn-hangzhou', '运行中'],
            ['ngw-3f9n0r1y8b2', 'dev-egress-nat', '小型', '4', 'cn-shanghai', '运行中'],
        ],
    },
    'cdn': {
        'title': 'CDN 域名',
        'subtitle': '内容分发网络',
        'columns': ['加速域名', 'CNAME', '业务类型', '源站', '状态', 'HTTPS'],
        'rows': [
            ['img.mall.example.com', 'img.mall.example.com.w.cdngslb.com', '图片小文件', 'img-oss.example.aliyuncs.com', '运行中', '已开启'],
            ['api.mall.example.com', 'api.mall.example.com.w.cdngslb.com', 'API 加速', 'api.mall.example.com', '运行中', '已开启'],
        ],
    },
    'alarms': {
        'title': '云监控告警',
        'subtitle': '监控与告警规则',
        'columns': ['告警规则', '监控指标', '资源范围', '阈值', '状态'],
        'rows': [
            ['ECS-CPU-高负载', 'CPUUtilization', 'i-2ze9d7x8qidghmelgw6y', '平均 > 80%', '告警中'],
            ['ECS-磁盘-空间', 'diskusage_utilization', 'i-2ze9d7x8qidghmelgw6y', '平均 > 85%', '正常'],
            ['RDS-连接数', 'ConnectionUtilization', 'prod-mall-mysql', '平均 > 90%', '正常'],
        ],
    },
    'audit': {
        'title': '操作审计',
        'subtitle': 'ActionTrail 操作记录',
        'columns': ['操作时间', '操作者', '云服务', '操作事件', '结果'],
        'rows': [
            ['2026-09-05 18:30:12', 'admin', 'ECS', 'RebootInstance', '成功'],
            ['2026-09-05 17:42:08', 'admin', 'OSS', 'CreateBucket', '成功'],
            ['2026-09-05 16:55:31', 'qiyang', 'RDS', 'DescribeDBInstances', '成功'],
        ],
    },
}

FAKE_RESOURCES = {
    'instances': [
        {
            'instance_id': 'i-demo-0001', 'name': 'web-prod-demo-01', 'region': 'cn-hangzhou',
            'spec': 'ecs.g7.xlarge', 'resource': '4 vCPU / 16 GiB', 'public_ip': '47.98.10.21',
            'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': '包年包月',
            'private_ip': '172.16.10.21', 'vpc_id': 'vpc-demo-0001', 'vswitch_id': 'vsw-demo-0001',
            'zone_id': 'cn-hangzhou-i', 'os_name': 'Alibaba Cloud Linux 3.2304', 'image_id': 'aliyun_3_9_x64_20G_uefi_alibase',
            'host_name': 'web-prod-demo-01', 'creation_time': '2026-06-01T10:20:00Z', 'expired_time': '2027-06-01T10:20:00Z',
            'cpu_percent': 23.6, 'cpu_color': '#5FB878',
        },
        {
            'instance_id': 'i-demo-0002', 'name': 'app-test-demo-02', 'region': 'cn-beijing',
            'spec': 'ecs.c7.large', 'resource': '2 vCPU / 8 GiB', 'public_ip': '120.92.18.33',
            'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': '按量付费',
            'private_ip': '172.16.20.33', 'vpc_id': 'vpc-demo-0002', 'vswitch_id': 'vsw-demo-0002',
            'zone_id': 'cn-beijing-g', 'os_name': 'CentOS 7.9 64位', 'image_id': 'centos_7_9_x64_20G',
            'host_name': 'app-test-demo-02', 'creation_time': '2026-07-12T08:00:00Z', 'expired_time': '-',
            'cpu_percent': 61.8, 'cpu_color': '#FFB800',
        },
    ],
    'buckets': [
        {'bucket_name': 'demo-static-web', 'region': 'oss-cn-hangzhou', 'object_count': '56,780', 'storage_size': '128.5 GiB', 'acl': '公共读', 'badge': 'layui-badge layui-bg-green'},
        {'bucket_name': 'demo-data-backup', 'region': 'oss-cn-beijing', 'object_count': '12,340', 'storage_size': '512.3 GiB', 'acl': '私有', 'badge': 'layui-badge layui-bg-gray'},
    ],
    'disks': [
        {'disk_id': 'd-demo-0001', 'disk_name': 'system-disk-01', 'region': 'cn-hangzhou', 'size': '40 GiB', 'category': 'cloud_essd', 'status': '使用中', 'badge': 'layui-badge layui-bg-green', 'instance_id': 'i-demo-0001', 'zone_id': 'cn-hangzhou-i', 'charge': '包年包月', 'encrypted': '否', 'creation_time': '2026-06-01T10:20:00Z', 'expired_time': '2027-06-01T10:20:00Z'},
        {'disk_id': 'd-demo-0002', 'disk_name': 'data-disk-01', 'region': 'cn-hangzhou', 'size': '200 GiB', 'category': 'cloud_essd', 'status': '可用', 'badge': 'layui-badge layui-bg-gray', 'instance_id': '-', 'zone_id': 'cn-hangzhou-i', 'charge': '按量付费', 'encrypted': '否', 'creation_time': '2026-07-01T08:00:00Z', 'expired_time': '-'},
    ],
    'security_groups': [
        {'group_id': 'sg-demo-0001', 'group_name': 'web-access-group', 'region': 'cn-hangzhou', 'group_type': '普通安全组', 'description': 'Demo Web 安全组', 'rule_count': 6, 'vpc_id': 'vpc-demo-0001', 'creation_time': '2026-06-01T10:20:00Z'},
        {'group_id': 'sg-demo-0002', 'group_name': 'db-internal-group', 'region': 'cn-beijing', 'group_type': '企业安全组', 'description': 'Demo 数据库安全组', 'rule_count': 4, 'vpc_id': 'vpc-demo-0002', 'creation_time': '2026-06-15T10:20:00Z'},
    ],
    'vpcs': [
        {'vpc_id': 'vpc-demo-0001', 'vpc_name': 'demo-main-vpc', 'cidr_block': '172.16.0.0/16', 'region': 'cn-hangzhou', 'status': '可用', 'badge': 'layui-badge layui-bg-green', 'switch_count': 3, 'creation_time': '2026-06-01T10:20:00Z'},
        {'vpc_id': 'vpc-demo-0002', 'vpc_name': 'demo-beijing-vpc', 'cidr_block': '10.10.0.0/16', 'region': 'cn-beijing', 'status': '可用', 'badge': 'layui-badge layui-bg-green', 'switch_count': 2, 'creation_time': '2026-06-05T10:20:00Z'},
    ],
    'snapshots': [
        {'snapshot_id': 's-demo-0001', 'snapshot_name': 'system-disk-demo-backup', 'region': 'cn-hangzhou', 'source_disk_id': 'd-demo-0001', 'source_disk_size': '40 GiB', 'status': '已完成', 'badge': 'layui-badge layui-bg-green', 'progress': '100%', 'creation_time': '2026-08-01T10:00:00Z', 'last_modified_time': '2026-08-01T10:05:00Z'},
        {'snapshot_id': 's-demo-0002', 'snapshot_name': 'data-disk-demo-backup', 'region': 'cn-beijing', 'source_disk_id': 'd-demo-0002', 'source_disk_size': '200 GiB', 'status': '已完成', 'badge': 'layui-badge layui-bg-green', 'progress': '100%', 'creation_time': '2026-08-02T11:00:00Z', 'last_modified_time': '2026-08-02T11:06:00Z'},
    ],
}

FAKE_RESOURCES = {
    'instances': [
        {'instance_id': 'i-2ze8m9q0x7a1', 'name': 'web-prod-01', 'region': 'cn-hangzhou', 'spec': 'ecs.g7.xlarge', 'resource': '4 vCPU / 16 GiB', 'public_ip': '47.98.110.21', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': '包年包月', 'private_ip': '172.16.10.21', 'vpc_id': 'vpc-2ze8m9q0', 'vswitch_id': 'vsw-2ze8m9q0', 'zone_id': 'cn-hangzhou-i', 'os_name': 'Alibaba Cloud Linux 3.2304', 'image_id': 'aliyun_3_9_x64_20G_uefi_alibase', 'host_name': 'web-prod-01', 'creation_time': '2026-06-01T10:20:00Z', 'expired_time': '2027-06-01T10:20:00Z', 'cpu_percent': 23.6, 'cpu_color': '#5FB878'},
        {'instance_id': 'i-3f9n0r1y8b2', 'name': 'app-gateway-02', 'region': 'cn-hangzhou', 'spec': 'ecs.g7.2xlarge', 'resource': '8 vCPU / 32 GiB', 'public_ip': '47.98.121.42', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': '包年包月', 'private_ip': '172.16.10.22', 'vpc_id': 'vpc-2ze8m9q0', 'vswitch_id': 'vsw-2ze8m9q0', 'zone_id': 'cn-hangzhou-i', 'os_name': 'Alibaba Cloud Linux 3.2304', 'image_id': 'aliyun_3_9_x64_20G_uefi_alibase', 'host_name': 'app-gateway-02', 'creation_time': '2026-06-03T10:20:00Z', 'expired_time': '2027-06-03T10:20:00Z', 'cpu_percent': 11.2, 'cpu_color': '#5FB878'},
        {'instance_id': 'i-4g0p1s2z9c3', 'name': 'k8s-worker-03', 'region': 'cn-beijing', 'spec': 'ecs.c7.4xlarge', 'resource': '16 vCPU / 64 GiB', 'public_ip': '120.92.88.31', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': '按量付费', 'private_ip': '10.10.20.31', 'vpc_id': 'vpc-3f9n0r1y', 'vswitch_id': 'vsw-3f9n0r1y', 'zone_id': 'cn-beijing-g', 'os_name': 'Alibaba Cloud Linux 3.2304', 'image_id': 'aliyun_3_9_x64_20G_uefi_alibase', 'host_name': 'k8s-worker-03', 'creation_time': '2026-06-08T10:20:00Z', 'expired_time': '2027-06-08T10:20:00Z', 'cpu_percent': 47.8, 'cpu_color': '#5FB878'},
        {'instance_id': 'i-5h1q2t3a0d4', 'name': 'db-mysql-04', 'region': 'cn-beijing', 'spec': 'ecs.r7.2xlarge', 'resource': '8 vCPU / 64 GiB', 'public_ip': '120.92.89.12', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': '包年包月', 'private_ip': '10.10.30.12', 'vpc_id': 'vpc-3f9n0r1y', 'vswitch_id': 'vsw-3f9n0r1y', 'zone_id': 'cn-beijing-g', 'os_name': 'CentOS 7.9 64位', 'image_id': 'centos_7_9_x64_20G', 'host_name': 'db-mysql-04', 'creation_time': '2026-05-11T10:20:00Z', 'expired_time': '2027-05-11T10:20:00Z', 'cpu_percent': 35.4, 'cpu_color': '#5FB878'},
        {'instance_id': 'i-6i2r3u4b1e5', 'name': 'redis-cache-05', 'region': 'cn-shanghai', 'spec': 'ecs.g7.xlarge', 'resource': '4 vCPU / 16 GiB', 'public_ip': '101.132.77.64', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': '包年包月', 'private_ip': '172.20.10.64', 'vpc_id': 'vpc-4g0p1s2z', 'vswitch_id': 'vsw-4g0p1s2z', 'zone_id': 'cn-shanghai-b', 'os_name': 'Ubuntu 22.04 64位', 'image_id': 'ubuntu_22_04_x64_docker_20G', 'host_name': 'redis-cache-05', 'creation_time': '2026-07-01T10:20:00Z', 'expired_time': '2027-07-01T10:20:00Z', 'cpu_percent': 8.9, 'cpu_color': '#5FB878'},
        {'instance_id': 'i-7j3s4v5c2f6', 'name': 'etl-node-06', 'region': 'cn-shenzhen', 'spec': 'ecs.g6.4xlarge', 'resource': '16 vCPU / 64 GiB', 'public_ip': '139.199.30.88', 'status': '已停止', 'badge': 'layui-badge layui-bg-gray', 'charge': '按量付费', 'private_ip': '172.18.10.88', 'vpc_id': 'vpc-5h1q2t3a', 'vswitch_id': 'vsw-5h1q2t3a', 'zone_id': 'cn-shenzhen-e', 'os_name': 'CentOS 7.9 64位', 'image_id': 'centos_7_9_x64_20G', 'host_name': 'etl-node-06', 'creation_time': '2026-03-01T10:20:00Z', 'expired_time': '-', 'cpu_percent': None, 'cpu_color': '#ccc'},
        {'instance_id': 'i-8k4t6w7d3g7', 'name': 'log-collector-07', 'region': 'cn-qingdao', 'spec': 'ecs.c7.large', 'resource': '2 vCPU / 8 GiB', 'public_ip': '106.14.91.32', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': '按量付费', 'private_ip': '172.16.50.32', 'vpc_id': 'vpc-6i2r3u4b', 'vswitch_id': 'vsw-6i2r3u4b', 'zone_id': 'cn-qingdao-c', 'os_name': 'Alibaba Cloud Linux 3.2304', 'image_id': 'aliyun_3_9_x64_20G_uefi_alibase', 'host_name': 'log-collector-07', 'creation_time': '2026-08-01T10:20:00Z', 'expired_time': '-', 'cpu_percent': 5.6, 'cpu_color': '#5FB878'},
        {'instance_id': 'i-9l5u7x8e4h8', 'name': 'monitor-agent-08', 'region': 'cn-hongkong', 'spec': 'ecs.t5-c1m1.large', 'resource': '2 vCPU / 4 GiB', 'public_ip': '47.89.12.77', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': '按量付费', 'private_ip': '172.21.10.77', 'vpc_id': 'vpc-7j3s4v5c', 'vswitch_id': 'vsw-7j3s4v5c', 'zone_id': 'cn-hongkong-b', 'os_name': 'Ubuntu 20.04 64位', 'image_id': 'ubuntu_20_04_x64_20G', 'host_name': 'monitor-agent-08', 'creation_time': '2026-08-20T10:20:00Z', 'expired_time': '-', 'cpu_percent': 2.1, 'cpu_color': '#5FB878'},
    ],
    'buckets': [
        {'bucket_name': 'prod-mall-static', 'region': 'oss-cn-hangzhou', 'object_count': '128,462', 'storage_size': '316.7 GiB', 'acl': '公共读', 'badge': 'layui-badge layui-bg-green'},
        {'bucket_name': 'prod-mall-media', 'region': 'oss-cn-hangzhou', 'object_count': '342,110', 'storage_size': '1.82 TiB', 'acl': '公共读', 'badge': 'layui-badge layui-bg-green'},
        {'bucket_name': 'data-backup-daily', 'region': 'oss-cn-beijing', 'object_count': '9,810', 'storage_size': '1.28 TiB', 'acl': '私有', 'badge': 'layui-badge layui-bg-gray'},
        {'bucket_name': 'app-log-archive', 'region': 'oss-cn-shanghai', 'object_count': '87,402', 'storage_size': '640.8 GiB', 'acl': '私有', 'badge': 'layui-badge layui-bg-gray'},
        {'bucket_name': 'image-resize-cache', 'region': 'oss-cn-shenzhen', 'object_count': '45,110', 'storage_size': '90.4 GiB', 'acl': '公共读', 'badge': 'layui-badge layui-bg-green'},
        {'bucket_name': 'etl-staging-warehouse', 'region': 'oss-cn-qingdao', 'object_count': '221,890', 'storage_size': '2.13 TiB', 'acl': '私有', 'badge': 'layui-badge layui-bg-gray'},
    ],
    'disks': [
        {'disk_id': 'd-2ze8m9q0x7a1', 'disk_name': 'system-disk-web-01', 'region': 'cn-hangzhou', 'size': '40 GiB', 'category': 'cloud_essd', 'status': '使用中', 'badge': 'layui-badge layui-bg-green', 'instance_id': 'i-2ze8m9q0x7a1', 'zone_id': 'cn-hangzhou-i', 'charge': '包年包月', 'encrypted': '否', 'creation_time': '2026-06-01T10:20:00Z', 'expired_time': '2027-06-01T10:20:00Z'},
        {'disk_id': 'd-3f9n0r1y8b2', 'disk_name': 'data-disk-mysql-04', 'region': 'cn-beijing', 'size': '500 GiB', 'category': 'cloud_essd', 'status': '使用中', 'badge': 'layui-badge layui-bg-green', 'instance_id': 'i-5h1q2t3a0d4', 'zone_id': 'cn-beijing-g', 'charge': '包年包月', 'encrypted': '是', 'creation_time': '2026-05-11T10:20:00Z', 'expired_time': '2027-05-11T10:20:00Z'},
        {'disk_id': 'd-4g0p1s2z9c3', 'disk_name': 'system-disk-k8s-03', 'region': 'cn-beijing', 'size': '80 GiB', 'category': 'cloud_essd_pl1', 'status': '使用中', 'badge': 'layui-badge layui-bg-green', 'instance_id': 'i-4g0p1s2z9c3', 'zone_id': 'cn-beijing-g', 'charge': '按量付费', 'encrypted': '否', 'creation_time': '2026-06-08T10:20:00Z', 'expired_time': '-'},
        {'disk_id': 'd-5h1q2t3a0d4', 'disk_name': 'system-disk-ecs-05', 'region': 'cn-shanghai', 'size': '40 GiB', 'category': 'cloud_ssd', 'status': '使用中', 'badge': 'layui-badge layui-bg-green', 'instance_id': 'i-6i2r3u4b1e5', 'zone_id': 'cn-shanghai-b', 'charge': '包年包月', 'encrypted': '否', 'creation_time': '2026-07-01T10:20:00Z', 'expired_time': '2027-07-01T10:20:00Z'},
        {'disk_id': 'd-6i2r3u4b1e5', 'disk_name': 'data-disk-etl-06', 'region': 'cn-shenzhen', 'size': '1000 GiB', 'category': 'cloud_essd_pl2', 'status': '可用', 'badge': 'layui-badge layui-bg-gray', 'instance_id': '-', 'zone_id': 'cn-shenzhen-e', 'charge': '按量付费', 'encrypted': '否', 'creation_time': '2026-03-01T10:20:00Z', 'expired_time': '-'},
        {'disk_id': 'd-7j3s4v5c2f6', 'disk_name': 'backup-disk-archive-07', 'region': 'cn-qingdao', 'size': '2000 GiB', 'category': 'cloud_essd_pl3', 'status': '可用', 'badge': 'layui-badge layui-bg-gray', 'instance_id': '-', 'zone_id': 'cn-qingdao-c', 'charge': '按量付费', 'encrypted': '是', 'creation_time': '2026-08-01T10:20:00Z', 'expired_time': '-'},
    ],
    'security_groups': [
        {'group_id': 'sg-2ze8m9q0x7a1', 'group_name': 'web-prod-access', 'region': 'cn-hangzhou', 'group_type': '普通安全组', 'description': '生产 Web 入口安全组', 'rule_count': 12, 'vpc_id': 'vpc-2ze8m9q0', 'creation_time': '2026-06-01T10:20:00Z'},
        {'group_id': 'sg-3f9n0r1y8b2', 'group_name': 'app-internal-allow', 'region': 'cn-hangzhou', 'group_type': '普通安全组', 'description': '应用服务内部互访', 'rule_count': 8, 'vpc_id': 'vpc-2ze8m9q0', 'creation_time': '2026-06-02T10:20:00Z'},
        {'group_id': 'sg-4g0p1s2z9c3', 'group_name': 'db-restricted-access', 'region': 'cn-beijing', 'group_type': '企业安全组', 'description': '数据库仅允许应用网段访问', 'rule_count': 5, 'vpc_id': 'vpc-3f9n0r1y', 'creation_time': '2026-06-03T10:20:00Z'},
        {'group_id': 'sg-5h1q2t3a0d4', 'group_name': 'k8s-worker-rule', 'region': 'cn-beijing', 'group_type': '企业安全组', 'description': 'ACK Worker 节点安全规则', 'rule_count': 16, 'vpc_id': 'vpc-3f9n0r1y', 'creation_time': '2026-06-05T10:20:00Z'},
        {'group_id': 'sg-6i2r3u4b1e5', 'group_name': 'monitor-outbound', 'region': 'cn-hongkong', 'group_type': '普通安全组', 'description': '监控节点出站访问规则', 'rule_count': 4, 'vpc_id': 'vpc-7j3s4v5c', 'creation_time': '2026-08-20T10:20:00Z'},
    ],
    'vpcs': [
        {'vpc_id': 'vpc-2ze8m9q0', 'vpc_name': 'vpc-hangzhou-prod', 'cidr_block': '172.16.0.0/16', 'region': 'cn-hangzhou', 'status': '可用', 'badge': 'layui-badge layui-bg-green', 'switch_count': 4, 'creation_time': '2026-06-01T10:20:00Z'},
        {'vpc_id': 'vpc-3f9n0r1y', 'vpc_name': 'vpc-beijing-prod', 'cidr_block': '10.10.0.0/16', 'region': 'cn-beijing', 'status': '可用', 'badge': 'layui-badge layui-bg-green', 'switch_count': 3, 'creation_time': '2026-06-02T10:20:00Z'},
        {'vpc_id': 'vpc-4g0p1s2z', 'vpc_name': 'vpc-shanghai-prod', 'cidr_block': '172.20.0.0/16', 'region': 'cn-shanghai', 'status': '可用', 'badge': 'layui-badge layui-bg-green', 'switch_count': 2, 'creation_time': '2026-06-03T10:20:00Z'},
        {'vpc_id': 'vpc-5h1q2t3a', 'vpc_name': 'vpc-shenzhen-dev', 'cidr_block': '172.18.0.0/16', 'region': 'cn-shenzhen', 'status': '可用', 'badge': 'layui-badge layui-bg-green', 'switch_count': 2, 'creation_time': '2026-06-04T10:20:00Z'},
    ],
    'snapshots': [
        {'snapshot_id': 's-2ze8m9q0x7a1', 'snapshot_name': 'system-disk-web-01-20260901', 'region': 'cn-hangzhou', 'source_disk_id': 'd-2ze8m9q0x7a1', 'source_disk_size': '40 GiB', 'status': '已完成', 'badge': 'layui-badge layui-bg-green', 'progress': '100%', 'creation_time': '2026-09-01T10:00:00Z', 'last_modified_time': '2026-09-01T10:05:00Z'},
        {'snapshot_id': 's-3f9n0r1y8b2', 'snapshot_name': 'data-disk-mysql-04-20260902', 'region': 'cn-beijing', 'source_disk_id': 'd-3f9n0r1y8b2', 'source_disk_size': '500 GiB', 'status': '已完成', 'badge': 'layui-badge layui-bg-green', 'progress': '100%', 'creation_time': '2026-09-02T10:00:00Z', 'last_modified_time': '2026-09-02T10:06:00Z'},
        {'snapshot_id': 's-4g0p1s2z9c3', 'snapshot_name': 'k8s-worker-03-daily', 'region': 'cn-beijing', 'source_disk_id': 'd-4g0p1s2z9c3', 'source_disk_size': '80 GiB', 'status': '已完成', 'badge': 'layui-badge layui-bg-green', 'progress': '100%', 'creation_time': '2026-09-03T10:00:00Z', 'last_modified_time': '2026-09-03T10:07:00Z'},
        {'snapshot_id': 's-5h1q2t3a0d4', 'snapshot_name': 'app-gateway-02-backup', 'region': 'cn-hangzhou', 'source_disk_id': 'd-5h1q2t3a0d4', 'source_disk_size': '100 GiB', 'status': '创建中', 'badge': 'layui-badge layui-bg-orange', 'progress': '68%', 'creation_time': '2026-09-05T10:00:00Z', 'last_modified_time': '2026-09-05T10:02:00Z'},
    ],
}
