from django.core.management.base import BaseCommand
from k8sdashboard.models import Authority, Role


ROWS = [
    # 阿里云
    {'id': 20, 'menu': '阿里云', 'pid': 0, 'controller': 'aliyun',
     'method': 'instances/?leftpid=110&leftid=111', 'path': '20', 'level': 0, 'top_menu_id': '20', 'orderby': '20'},
    {'id': 110, 'menu': '计算与存储', 'pid': 20, 'controller': 'aliyun',
     'method': '', 'path': '20-110', 'level': 1, 'top_menu_id': '20', 'orderby': '110'},
    {'id': 111, 'menu': 'ECS 实例列表', 'pid': 110, 'controller': 'aliyun',
     'method': 'instances', 'path': '20-110-111', 'level': 2, 'top_menu_id': '20', 'orderby': '111'},
    {'id': 112, 'menu': 'OSS 存储管理', 'pid': 110, 'controller': 'aliyun',
     'method': 'buckets', 'path': '20-110-112', 'level': 2, 'top_menu_id': '20', 'orderby': '112'},
    {'id': 113, 'menu': '资源总览', 'pid': 110, 'controller': 'aliyun',
     'method': 'overview', 'path': '20-110-113', 'level': 2, 'top_menu_id': '20', 'orderby': '113'},
    {'id': 122, 'menu': 'AccessKey 配置', 'pid': 110, 'controller': 'aliyun',
     'method': 'credentials', 'path': '20-110-122', 'level': 2, 'top_menu_id': '20', 'orderby': '122'},
    {'id': 123, 'menu': '云盘管理', 'pid': 110, 'controller': 'aliyun',
     'method': 'disks', 'path': '20-110-123', 'level': 2, 'top_menu_id': '20', 'orderby': '123'},
    {'id': 124, 'menu': '快照管理', 'pid': 110, 'controller': 'aliyun',
     'method': 'snapshots', 'path': '20-110-124', 'level': 2, 'top_menu_id': '20', 'orderby': '124'},
    {'id': 125, 'menu': '容器服务 ACK', 'pid': 110, 'controller': 'aliyun',
     'method': 'ack', 'path': '20-110-125', 'level': 2, 'top_menu_id': '20', 'orderby': '125'},
    {'id': 126, 'menu': '函数计算 FC', 'pid': 110, 'controller': 'aliyun',
     'method': 'fc', 'path': '20-110-126', 'level': 2, 'top_menu_id': '20', 'orderby': '126'},
    {'id': 127, 'menu': '网络与安全', 'pid': 20, 'controller': 'aliyun',
     'method': '', 'path': '20-127', 'level': 1, 'top_menu_id': '20', 'orderby': '127'},
    {'id': 128, 'menu': '安全组', 'pid': 127, 'controller': 'aliyun',
     'method': 'security-groups', 'path': '20-127-128', 'level': 2, 'top_menu_id': '20', 'orderby': '128'},
    {'id': 129, 'menu': 'VPC 网络', 'pid': 127, 'controller': 'aliyun',
     'method': 'vpcs', 'path': '20-127-129', 'level': 2, 'top_menu_id': '20', 'orderby': '129'},
    {'id': 130, 'menu': '云数据库', 'pid': 20, 'controller': 'aliyun',
     'method': '', 'path': '20-130', 'level': 1, 'top_menu_id': '20', 'orderby': '130'},
    {'id': 131, 'menu': 'RDS MySQL', 'pid': 130, 'controller': 'aliyun',
     'method': 'rds', 'path': '20-130-131', 'level': 2, 'top_menu_id': '20', 'orderby': '131'},
    {'id': 132, 'menu': 'Redis 实例', 'pid': 130, 'controller': 'aliyun',
     'method': 'redis', 'path': '20-130-132', 'level': 2, 'top_menu_id': '20', 'orderby': '132'},
    {'id': 133, 'menu': 'MongoDB 实例', 'pid': 130, 'controller': 'aliyun',
     'method': 'mongodb', 'path': '20-130-133', 'level': 2, 'top_menu_id': '20', 'orderby': '133'},
    {'id': 134, 'menu': '网络与 CDN', 'pid': 20, 'controller': 'aliyun',
     'method': '', 'path': '20-134', 'level': 1, 'top_menu_id': '20', 'orderby': '134'},
    {'id': 135, 'menu': '负载均衡 SLB', 'pid': 134, 'controller': 'aliyun',
     'method': 'slb', 'path': '20-134-135', 'level': 2, 'top_menu_id': '20', 'orderby': '135'},
    {'id': 136, 'menu': 'NAT 网关', 'pid': 134, 'controller': 'aliyun',
     'method': 'nat', 'path': '20-134-136', 'level': 2, 'top_menu_id': '20', 'orderby': '136'},
    {'id': 137, 'menu': 'CDN 域名', 'pid': 134, 'controller': 'aliyun',
     'method': 'cdn', 'path': '20-134-137', 'level': 2, 'top_menu_id': '20', 'orderby': '137'},
    {'id': 138, 'menu': '安全与监控', 'pid': 20, 'controller': 'aliyun',
     'method': '', 'path': '20-138', 'level': 1, 'top_menu_id': '20', 'orderby': '138'},
    {'id': 139, 'menu': '云监控告警', 'pid': 138, 'controller': 'aliyun',
     'method': 'alarms', 'path': '20-138-139', 'level': 2, 'top_menu_id': '20', 'orderby': '139'},
    {'id': 140, 'menu': '操作审计', 'pid': 138, 'controller': 'aliyun',
     'method': 'audit', 'path': '20-138-140', 'level': 2, 'top_menu_id': '20', 'orderby': '140'},
    # 腾讯云
    {'id': 21, 'menu': '腾讯云', 'pid': 0, 'controller': 'tencent',
     'method': 'instances/?leftpid=114&leftid=115', 'path': '21', 'level': 0, 'top_menu_id': '21', 'orderby': '21'},
    {'id': 114, 'menu': '腾讯云资源', 'pid': 21, 'controller': 'tencent',
     'method': '', 'path': '21-114', 'level': 1, 'top_menu_id': '21', 'orderby': '114'},
    {'id': 115, 'menu': 'CVM 实例列表', 'pid': 114, 'controller': 'tencent',
     'method': 'instances', 'path': '21-114-115', 'level': 2, 'top_menu_id': '21', 'orderby': '115'},
    {'id': 116, 'menu': 'COS 存储管理', 'pid': 114, 'controller': 'tencent',
     'method': 'buckets', 'path': '21-114-116', 'level': 2, 'top_menu_id': '21', 'orderby': '116'},
    {'id': 117, 'menu': '资源总览', 'pid': 114, 'controller': 'tencent',
     'method': 'overview', 'path': '21-114-117', 'level': 2, 'top_menu_id': '21', 'orderby': '117'},
    # AWS
    {'id': 22, 'menu': 'AWS', 'pid': 0, 'controller': 'aws',
     'method': 'instances/?leftpid=118&leftid=119', 'path': '22', 'level': 0, 'top_menu_id': '22', 'orderby': '22'},
    {'id': 118, 'menu': 'AWS 资源', 'pid': 22, 'controller': 'aws',
     'method': '', 'path': '22-118', 'level': 1, 'top_menu_id': '22', 'orderby': '118'},
    {'id': 119, 'menu': 'EC2 实例列表', 'pid': 118, 'controller': 'aws',
     'method': 'instances', 'path': '22-118-119', 'level': 2, 'top_menu_id': '22', 'orderby': '119'},
    {'id': 120, 'menu': 'S3 存储管理', 'pid': 118, 'controller': 'aws',
     'method': 'buckets', 'path': '22-118-120', 'level': 2, 'top_menu_id': '22', 'orderby': '120'},
    {'id': 121, 'menu': '资源总览', 'pid': 118, 'controller': 'aws',
     'method': 'overview', 'path': '22-118-121', 'level': 2, 'top_menu_id': '22', 'orderby': '121'},
    {'id': 141, 'menu': '计算', 'pid': 22, 'controller': 'aws',
     'method': '', 'path': '22-141', 'level': 1, 'top_menu_id': '22', 'orderby': '141'},
    {'id': 142, 'menu': 'Amazon EKS', 'pid': 141, 'controller': 'aws',
     'method': 'eks', 'path': '22-141-142', 'level': 2, 'top_menu_id': '22', 'orderby': '142'},
    {'id': 143, 'menu': 'AWS Lambda', 'pid': 141, 'controller': 'aws',
     'method': 'lambda', 'path': '22-141-143', 'level': 2, 'top_menu_id': '22', 'orderby': '143'},
    {'id': 144, 'menu': 'Auto Scaling', 'pid': 141, 'controller': 'aws',
     'method': 'autoscaling', 'path': '22-141-144', 'level': 2, 'top_menu_id': '22', 'orderby': '144'},
    {'id': 145, 'menu': '存储与数据库', 'pid': 22, 'controller': 'aws',
     'method': '', 'path': '22-145', 'level': 1, 'top_menu_id': '22', 'orderby': '145'},
    {'id': 146, 'menu': 'EBS 存储卷', 'pid': 145, 'controller': 'aws',
     'method': 'ebs', 'path': '22-145-146', 'level': 2, 'top_menu_id': '22', 'orderby': '146'},
    {'id': 147, 'menu': 'EFS 文件系统', 'pid': 145, 'controller': 'aws',
     'method': 'efs', 'path': '22-145-147', 'level': 2, 'top_menu_id': '22', 'orderby': '147'},
    {'id': 148, 'menu': 'Amazon RDS', 'pid': 145, 'controller': 'aws',
     'method': 'rds-aws', 'path': '22-145-148', 'level': 2, 'top_menu_id': '22', 'orderby': '148'},
    {'id': 149, 'menu': 'DynamoDB', 'pid': 145, 'controller': 'aws',
     'method': 'dynamodb', 'path': '22-145-149', 'level': 2, 'top_menu_id': '22', 'orderby': '149'},
    {'id': 150, 'menu': 'ElastiCache', 'pid': 145, 'controller': 'aws',
     'method': 'elasticache', 'path': '22-145-150', 'level': 2, 'top_menu_id': '22', 'orderby': '150'},
    {'id': 151, 'menu': '网络与内容分发', 'pid': 22, 'controller': 'aws',
     'method': '', 'path': '22-151', 'level': 1, 'top_menu_id': '22', 'orderby': '151'},
    {'id': 152, 'menu': 'Amazon VPC', 'pid': 151, 'controller': 'aws',
     'method': 'vpc-aws', 'path': '22-151-152', 'level': 2, 'top_menu_id': '22', 'orderby': '152'},
    {'id': 153, 'menu': 'ELB 负载均衡', 'pid': 151, 'controller': 'aws',
     'method': 'elb', 'path': '22-151-153', 'level': 2, 'top_menu_id': '22', 'orderby': '153'},
    {'id': 154, 'menu': 'CloudFront', 'pid': 151, 'controller': 'aws',
     'method': 'cloudfront', 'path': '22-151-154', 'level': 2, 'top_menu_id': '22', 'orderby': '154'},
    {'id': 155, 'menu': 'Route 53', 'pid': 151, 'controller': 'aws',
     'method': 'route53', 'path': '22-151-155', 'level': 2, 'top_menu_id': '22', 'orderby': '155'},
    {'id': 156, 'menu': '管理与监控', 'pid': 22, 'controller': 'aws',
     'method': '', 'path': '22-156', 'level': 1, 'top_menu_id': '22', 'orderby': '156'},
    {'id': 157, 'menu': 'CloudWatch', 'pid': 156, 'controller': 'aws',
     'method': 'cloudwatch', 'path': '22-156-157', 'level': 2, 'top_menu_id': '22', 'orderby': '157'},
    {'id': 158, 'menu': 'CloudTrail', 'pid': 156, 'controller': 'aws',
     'method': 'cloudtrail', 'path': '22-156-158', 'level': 2, 'top_menu_id': '22', 'orderby': '158'},
    {'id': 159, 'menu': 'IAM', 'pid': 156, 'controller': 'aws',
     'method': 'iam', 'path': '22-156-159', 'level': 2, 'top_menu_id': '22', 'orderby': '159'},
    {'id': 160, 'menu': 'Cost Explorer', 'pid': 156, 'controller': 'aws',
     'method': 'cost', 'path': '22-156-160', 'level': 2, 'top_menu_id': '22', 'orderby': '160'},
]


class Command(BaseCommand):
    help = 'Seed cloud provider navigation and grant them to the admin role.'

    def handle(self, *args, **options):
        menu_ids = []
        for row in ROWS:
            defaults = dict(row)
            menu_id = defaults.pop('id')
            Authority.objects.update_or_create(id=menu_id, defaults=defaults)
            menu_ids.append(menu_id)

        role = Role.objects.get(id=1)
        current_ids = [int(item) for item in role.authority_id.split(',') if item]
        for menu_id in menu_ids:
            if menu_id not in current_ids:
                current_ids.append(menu_id)
        role.authority_id = ','.join(str(item) for item in current_ids)
        role.save(update_fields=['authority_id'])

        self.stdout.write(self.style.SUCCESS('Cloud provider menus seeded.'))
