AWS_SERVICE_PAGES = {
    'eks': {
        'title': 'Amazon EKS',
        'subtitle': '托管 Kubernetes 服务',
        'columns': ['集群名称', '区域', '版本', '节点数', '状态'],
        'rows': [
            ['prod-eks-mall', 'ap-southeast-1', '1.30', '6', 'ACTIVE'],
            ['staging-eks-ai', 'us-east-1', '1.29', '3', 'ACTIVE'],
        ],
    },
    'lambda': {
        'title': 'AWS Lambda',
        'subtitle': 'Serverless 函数',
        'columns': ['函数名称', '运行时', '内存', '超时时间', '调用次数'],
        'rows': [
            ['image-processor', 'Python 3.12', '512 MB', '60 sec', '128,450'],
            ['payment-webhook', 'Node.js 20', '256 MB', '30 sec', '32,180'],
            ['invoice-scheduler', 'Python 3.12', '128 MB', '120 sec', '890'],
        ],
    },
    'autoscaling': {
        'title': 'Auto Scaling',
        'subtitle': '弹性伸缩组',
        'columns': ['伸缩组名称', '区域', '最小实例', '最大实例', '当前实例', '状态'],
        'rows': [
            ['asg-web-prod', 'ap-southeast-1', '2', '8', '4', 'ACTIVE'],
            ['asg-worker-staging', 'us-east-1', '1', '5', '3', 'ACTIVE'],
        ],
    },
    'ebs': {
        'title': 'Amazon EBS',
        'subtitle': '块存储卷',
        'columns': ['卷 ID', '名称', '区域', '容量', '类型', '状态'],
        'rows': [
            ['vol-0a1b2c3d4e5f67890', 'root-volume-web-01', 'ap-southeast-1', '80 GiB', 'gp3', 'in-use'],
            ['vol-0f1a2b3c4d5e6f789', 'data-volume-db-01', 'us-east-1', '500 GiB', 'io2', 'in-use'],
            ['vol-0a9b8c7d6e5f43210', 'snapshot-staging-disk', 'ap-southeast-1', '100 GiB', 'gp3', 'available'],
        ],
    },
    'efs': {
        'title': 'Amazon EFS',
        'subtitle': '弹性文件系统',
        'columns': ['文件系统 ID', '名称', '区域', '存储类型', '挂载目标', '状态'],
        'rows': [
            ['fs-0a1b2c3d4e5f67890', 'shared-web-content', 'ap-southeast-1', 'Standard', '3', 'available'],
            ['fs-0f1a2b3c4d5e6f789', 'data-science-home', 'us-east-1', 'IA', '2', 'available'],
        ],
    },
    'rds-aws': {
        'title': 'Amazon RDS',
        'subtitle': '托管关系型数据库',
        'columns': ['实例 ID', '名称', '引擎', '规格', '区域', '状态'],
        'rows': [
            ['db-0a1b2c3d4e5f67890', 'prod-order-db', 'MySQL 8.0', 'db.r6g.2xlarge', 'ap-southeast-1', 'available'],
            ['db-0f1a2b3c4d5e6f789', 'analytics-report', 'PostgreSQL 15', 'db.r6g.xlarge', 'us-east-1', 'available'],
        ],
    },
    'dynamodb': {
        'title': 'Amazon DynamoDB',
        'subtitle': 'NoSQL 数据库',
        'columns': ['表名称', '区域', '主键', '容量模式', '表大小', '状态'],
        'rows': [
            ['user-session', 'ap-southeast-1', 'user_id', 'On-Demand', '18.4 GiB', 'ACTIVE'],
            ['order-event', 'us-east-1', 'order_id', 'On-Demand', '52.7 GiB', 'ACTIVE'],
        ],
    },
    'elasticache': {
        'title': 'Amazon ElastiCache',
        'subtitle': 'Redis / Memcached',
        'columns': ['集群 ID', '引擎', '节点规格', '分片', '区域', '状态'],
        'rows': [
            ['prod-hot-cache', 'Redis 7', 'cache.r6g.large', '3', 'ap-southeast-1', 'available'],
            ['session-cache', 'Redis 7', 'cache.t3.micro', '1', 'us-east-1', 'available'],
        ],
    },
    'vpc-aws': {
        'title': 'Amazon VPC',
        'subtitle': '虚拟私有云',
        'columns': ['VPC ID', '名称', 'CIDR', '区域', '子网数', '状态'],
        'rows': [
            ['vpc-0a1b2c3d4e5f67890', 'prod-vpc-singapore', '10.10.0.0/16', 'ap-southeast-1', '4', 'available'],
            ['vpc-0f1a2b3c4d5e6f789', 'staging-vpc-virginia', '172.20.0.0/16', 'us-east-1', '3', 'available'],
        ],
    },
    'elb': {
        'title': 'Elastic Load Balancing',
        'subtitle': 'ELB / ALB / NLB',
        'columns': ['负载均衡 ID', '名称', '类型', 'DNS 名称', '区域', '状态'],
        'rows': [
            ['app-0a1b2c3d4e5f67890', 'prod-api-alb', 'Application', 'prod-api-123456.ap-southeast-1.elb.amazonaws.com', 'ap-southeast-1', 'active'],
            ['net-0f1a2b3c4d5e6f789', 'internal-nlb', 'Network', 'internal-nlb-654321.us-east-1.elb.amazonaws.com', 'us-east-1', 'active'],
        ],
    },
    'cloudfront': {
        'title': 'Amazon CloudFront',
        'subtitle': '内容分发网络',
        'columns': ['分配 ID', '域名', '源站', '区域', '状态'],
        'rows': [
            ['E2ABCDEF123456', 'img.mall.example.com', 'mall-static.s3.ap-southeast-1.amazonaws.com', 'Global', 'Deployed'],
            ['E3GHIJKL789012', 'api-cdn.example.com', 'api.example.com', 'Global', 'Deployed'],
        ],
    },
    'route53': {
        'title': 'Amazon Route 53',
        'subtitle': 'DNS 与域名',
        'columns': ['托管区', '域名', '记录数', '状态'],
        'rows': [
            ['Z1234567890ABCD', 'example.com', '46', 'Active'],
            ['Z9876543210EFGH', 'mall.example.com', '28', 'Active'],
        ],
    },
    'cloudwatch': {
        'title': 'Amazon CloudWatch',
        'subtitle': '监控与告警',
        'columns': ['告警名称', '指标', '资源', '条件', '状态'],
        'rows': [
            ['EC2-CPU-High', 'CPUUtilization', 'i-0a1b2c3d4e5f67890', '> 80% for 5 min', 'ALARM'],
            ['RDS-Connections', 'DatabaseConnections', 'db-0a1b2c3d4e5f67890', '> 90% for 10 min', 'OK'],
            ['Lambda-Errors', 'Errors', 'image-processor', '> 1 for 5 min', 'OK'],
        ],
    },
    'cloudtrail': {
        'title': 'AWS CloudTrail',
        'subtitle': '操作审计',
        'columns': ['事件时间', '用户', '服务', '事件', '区域', '结果'],
        'rows': [
            ['2026-09-05 18:20:11', 'admin', 'EC2', 'RunInstances', 'ap-southeast-1', 'Success'],
            ['2026-09-05 17:44:08', 'qiyang', 'S3', 'PutObject', 'us-east-1', 'Success'],
        ],
    },
    'iam': {
        'title': 'AWS IAM',
        'subtitle': '访问控制',
        'columns': ['用户/角色', '类型', '创建时间', '最后使用', '状态'],
        'rows': [
            ['dashboard-admin', 'User', '2026-05-01', '2026-09-05', 'Active'],
            ['eks-node-role', 'Role', '2026-06-10', '2026-09-05', 'Active'],
            ['s3-readonly', 'User', '2026-07-20', '2026-09-04', 'Active'],
        ],
    },
    'cost': {
        'title': 'Cost Explorer',
        'subtitle': '成本与账单',
        'columns': ['月份', '服务', '区域', '上月费用', '本月费用', '同比'],
        'rows': [
            ['2026-09', 'EC2', 'ap-southeast-1', '$1,240.00', '$1,318.00', '+6.3%'],
            ['2026-09', 'RDS', 'us-east-1', '$860.00', '$798.00', '-7.2%'],
            ['2026-09', 'S3', 'Global', '$390.00', '$415.00', '+6.4%'],
        ],
    },
}

AWS_OVERVIEW_RESOURCES = {
    'instances': [
        {'instance_id': 'i-0a1b2c3d4e5f67890', 'name': 'web-prod-01', 'region': 'ap-southeast-1', 'spec': 'm6i.xlarge', 'resource': '4 vCPU / 16 GiB', 'public_ip': '13.250.44.18', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': 'On-Demand', 'private_ip': '10.10.10.18', 'vpc_id': 'vpc-0a1b2c3d4e5f67890', 'vswitch_id': 'subnet-0a1b2c3d', 'zone_id': 'ap-southeast-1a', 'os_name': 'Amazon Linux 2023', 'image_id': 'ami-0abcdef1234567890', 'host_name': 'web-prod-01', 'creation_time': '2026-06-01T10:20:00Z', 'expired_time': '-', 'cpu_percent': 22.4, 'cpu_color': '#5FB878', 'memory_percent': 48.2, 'memory_color': '#0E7EEB'},
        {'instance_id': 'i-0f1a2b3c4d5e6f789', 'name': 'app-api-02', 'region': 'ap-southeast-1', 'spec': 'c6i.2xlarge', 'resource': '8 vCPU / 16 GiB', 'public_ip': '13.251.90.36', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': 'On-Demand', 'private_ip': '10.10.10.36', 'vpc_id': 'vpc-0a1b2c3d4e5f67890', 'vswitch_id': 'subnet-0f1a2b3c', 'zone_id': 'ap-southeast-1a', 'os_name': 'Amazon Linux 2023', 'image_id': 'ami-0abcdef1234567890', 'host_name': 'app-api-02', 'creation_time': '2026-06-05T10:20:00Z', 'expired_time': '-', 'cpu_percent': 11.6, 'cpu_color': '#5FB878', 'memory_percent': 36.8, 'memory_color': '#0E7EEB'},
        {'instance_id': 'i-0a9b8c7d6e5f43210', 'name': 'k8s-worker-03', 'region': 'us-east-1', 'spec': 'm6i.4xlarge', 'resource': '16 vCPU / 64 GiB', 'public_ip': '18.209.211.32', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': 'Reserved', 'private_ip': '172.20.20.32', 'vpc_id': 'vpc-0f1a2b3c4d5e6f789', 'vswitch_id': 'subnet-0a9b8c7d', 'zone_id': 'us-east-1a', 'os_name': 'Amazon Linux 2023', 'image_id': 'ami-1bcdef2345678901', 'host_name': 'k8s-worker-03', 'creation_time': '2026-06-10T10:20:00Z', 'expired_time': '-', 'cpu_percent': 47.8, 'cpu_color': '#FFB800', 'memory_percent': 68.4, 'memory_color': '#0E7EEB'},
        {'instance_id': 'i-0c1d2e3f4a5b67890', 'name': 'db-postgres-04', 'region': 'us-east-1', 'spec': 'r6i.2xlarge', 'resource': '8 vCPU / 64 GiB', 'public_ip': '18.208.101.55', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': 'Reserved', 'private_ip': '172.20.30.55', 'vpc_id': 'vpc-0f1a2b3c4d5e6f789', 'vswitch_id': 'subnet-0c1d2e3f', 'zone_id': 'us-east-1b', 'os_name': 'Ubuntu 22.04', 'image_id': 'ami-2cdef34567890123', 'host_name': 'db-postgres-04', 'creation_time': '2026-05-20T10:20:00Z', 'expired_time': '-', 'cpu_percent': 35.2, 'cpu_color': '#5FB878', 'memory_percent': 72.1, 'memory_color': '#0E7EEB'},
        {'instance_id': 'i-0e1f2a3b4c5d67890', 'name': 'batch-worker-05', 'region': 'eu-west-1', 'spec': 'm5.2xlarge', 'resource': '8 vCPU / 32 GiB', 'public_ip': '34.244.70.21', 'status': '运行中', 'badge': 'layui-badge layui-bg-green', 'charge': 'Spot', 'private_ip': '192.168.10.21', 'vpc_id': 'vpc-0e1f2a3b4c5d67890', 'vswitch_id': 'subnet-0e1f2a3b', 'zone_id': 'eu-west-1a', 'os_name': 'Amazon Linux 2', 'image_id': 'ami-3def45678901234', 'host_name': 'batch-worker-05', 'creation_time': '2026-08-01T10:20:00Z', 'expired_time': '-', 'cpu_percent': 81.5, 'cpu_color': '#FF5722', 'memory_percent': 88.6, 'memory_color': '#0E7EEB'},
        {'instance_id': 'i-0d1e2f3a4b5c78901', 'name': 'old-dev-box', 'region': 'ap-southeast-1', 'spec': 't3.medium', 'resource': '2 vCPU / 4 GiB', 'public_ip': '13.229.60.11', 'status': '已停止', 'badge': 'layui-badge layui-bg-gray', 'charge': 'On-Demand', 'private_ip': '10.10.50.11', 'vpc_id': 'vpc-0a1b2c3d4e5f67890', 'vswitch_id': 'subnet-0d1e2f3a', 'zone_id': 'ap-southeast-1b', 'os_name': 'Amazon Linux 2', 'image_id': 'ami-4efg56789012345', 'host_name': 'old-dev-box', 'creation_time': '2026-02-01T10:20:00Z', 'expired_time': '-', 'cpu_percent': None, 'cpu_color': '#ccc', 'memory_percent': None, 'memory_color': '#ccc'},
    ],
    'buckets': [
        {'bucket_name': 'prod-mall-static', 'region': 'ap-southeast-1', 'object_count': '256,490', 'storage_size': '512.6 GiB', 'acl': 'Public Read', 'badge': 'layui-badge layui-bg-green'},
        {'bucket_name': 'data-backup-daily', 'region': 'us-east-1', 'object_count': '12,380', 'storage_size': '2.6 TiB', 'acl': 'Private', 'badge': 'layui-badge layui-bg-gray'},
        {'bucket_name': 'app-log-archive', 'region': 'eu-west-1', 'object_count': '92,150', 'storage_size': '1.8 TiB', 'acl': 'Private', 'badge': 'layui-badge layui-bg-gray'},
        {'bucket_name': 'image-resize-cache', 'region': 'ap-southeast-1', 'object_count': '80,240', 'storage_size': '204.1 GiB', 'acl': 'Public Read', 'badge': 'layui-badge layui-bg-green'},
    ],
    'disks': [
        {'disk_id': 'vol-0a1b2c3d4e5f67890', 'disk_name': 'root-volume-web-01', 'region': 'ap-southeast-1', 'size': '80 GiB', 'category': 'gp3', 'status': '使用中', 'badge': 'layui-badge layui-bg-green', 'instance_id': 'i-0a1b2c3d4e5f67890', 'zone_id': 'ap-southeast-1a', 'charge': 'On-Demand', 'encrypted': '是', 'creation_time': '2026-06-01T10:20:00Z', 'expired_time': '-'},
        {'disk_id': 'vol-0f1a2b3c4d5e6f789', 'disk_name': 'data-volume-db-04', 'region': 'us-east-1', 'size': '1000 GiB', 'category': 'io2', 'status': '使用中', 'badge': 'layui-badge layui-bg-green', 'instance_id': 'i-0c1d2e3f4a5b67890', 'zone_id': 'us-east-1b', 'charge': 'Reserved', 'encrypted': '是', 'creation_time': '2026-05-20T10:20:00Z', 'expired_time': '-'},
        {'disk_id': 'vol-0a9b8c7d6e5f43210', 'disk_name': 'worker-system-disk', 'region': 'us-east-1', 'size': '120 GiB', 'category': 'gp3', 'status': '使用中', 'badge': 'layui-badge layui-bg-green', 'instance_id': 'i-0a9b8c7d6e5f43210', 'zone_id': 'us-east-1a', 'charge': 'On-Demand', 'encrypted': '否', 'creation_time': '2026-06-10T10:20:00Z', 'expired_time': '-'},
        {'disk_id': 'vol-0e1f2a3b4c5d67890', 'disk_name': 'batch-worker-disk', 'region': 'eu-west-1', 'size': '500 GiB', 'category': 'gp3', 'status': '使用中', 'badge': 'layui-badge layui-bg-green', 'instance_id': 'i-0e1f2a3b4c5d67890', 'zone_id': 'eu-west-1a', 'charge': 'On-Demand', 'encrypted': '否', 'creation_time': '2026-08-01T10:20:00Z', 'expired_time': '-'},
    ],
    'security_groups': [
        {'group_id': 'sg-0a1b2c3d4e5f67890', 'group_name': 'web-access-sg', 'region': 'ap-southeast-1', 'group_type': 'VPC Security Group', 'description': 'Web access rules', 'rule_count': 14, 'vpc_id': 'vpc-0a1b2c3d4e5f67890', 'creation_time': '2026-06-01T10:20:00Z'},
        {'group_id': 'sg-0f1a2b3c4d5e6f789', 'group_name': 'db-internal-sg', 'region': 'us-east-1', 'group_type': 'VPC Security Group', 'description': 'Database internal access', 'rule_count': 6, 'vpc_id': 'vpc-0f1a2b3c4d5e6f789', 'creation_time': '2026-06-02T10:20:00Z'},
        {'group_id': 'sg-0a9b8c7d6e5f43210', 'group_name': 'k8s-node-sg', 'region': 'us-east-1', 'group_type': 'VPC Security Group', 'description': 'EKS node rules', 'rule_count': 18, 'vpc_id': 'vpc-0f1a2b3c4d5e6f789', 'creation_time': '2026-06-03T10:20:00Z'},
        {'group_id': 'sg-0e1f2a3b4c5d67890', 'group_name': 'monitor-sg', 'region': 'eu-west-1', 'group_type': 'VPC Security Group', 'description': 'Monitoring outbound', 'rule_count': 4, 'vpc_id': 'vpc-0e1f2a3b4c5d67890', 'creation_time': '2026-08-01T10:20:00Z'},
    ],
    'vpcs': [
        {'vpc_id': 'vpc-0a1b2c3d4e5f67890', 'vpc_name': 'vpc-singapore-prod', 'cidr_block': '10.10.0.0/16', 'region': 'ap-southeast-1', 'status': '可用', 'badge': 'layui-badge layui-bg-green', 'switch_count': 4, 'creation_time': '2026-06-01T10:20:00Z'},
        {'vpc_id': 'vpc-0f1a2b3c4d5e6f789', 'vpc_name': 'vpc-virginia-prod', 'cidr_block': '172.20.0.0/16', 'region': 'us-east-1', 'status': '可用', 'badge': 'layui-badge layui-bg-green', 'switch_count': 3, 'creation_time': '2026-06-02T10:20:00Z'},
        {'vpc_id': 'vpc-0e1f2a3b4c5d67890', 'vpc_name': 'vpc-ireland-dev', 'cidr_block': '192.168.0.0/16', 'region': 'eu-west-1', 'status': '可用', 'badge': 'layui-badge layui-bg-green', 'switch_count': 2, 'creation_time': '2026-08-01T10:20:00Z'},
    ],
    'snapshots': [
        {'snapshot_id': 'snap-0a1b2c3d4e5f67890', 'snapshot_name': 'root-volume-web-01-backup', 'region': 'ap-southeast-1', 'source_disk_id': 'vol-0a1b2c3d4e5f67890', 'source_disk_size': '80 GiB', 'status': '已完成', 'badge': 'layui-badge layui-bg-green', 'progress': '100%', 'creation_time': '2026-09-01T10:00:00Z', 'last_modified_time': '2026-09-01T10:05:00Z'},
        {'snapshot_id': 'snap-0f1a2b3c4d5e6f789', 'snapshot_name': 'db-volume-daily-backup', 'region': 'us-east-1', 'source_disk_id': 'vol-0f1a2b3c4d5e6f789', 'source_disk_size': '1000 GiB', 'status': '已完成', 'badge': 'layui-badge layui-bg-green', 'progress': '100%', 'creation_time': '2026-09-02T10:00:00Z', 'last_modified_time': '2026-09-02T10:08:00Z'},
        {'snapshot_id': 'snap-0a9b8c7d6e5f43210', 'snapshot_name': 'batch-worker-backup', 'region': 'eu-west-1', 'source_disk_id': 'vol-0e1f2a3b4c5d67890', 'source_disk_size': '500 GiB', 'status': '创建中', 'badge': 'layui-badge layui-bg-orange', 'progress': '72%', 'creation_time': '2026-09-05T10:00:00Z', 'last_modified_time': '2026-09-05T10:03:00Z'},
    ],
}
