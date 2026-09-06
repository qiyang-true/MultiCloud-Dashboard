from django.db import models

# Create your models here.


class Manager(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32, unique=True, verbose_name='管理员名')
    password = models.CharField(max_length=64, verbose_name='密码')
    role_id = models.PositiveSmallIntegerField(default=0, verbose_name='角色id')
    supermanager = models.BooleanField(default=False, verbose_name='超级管理员')
    mtime = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')
    atime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'manager'


class Authority(models.Model):
    id = models.AutoField(primary_key=True)
    menu = models.CharField(max_length=50, verbose_name='名称')
    pid = models.SmallIntegerField(verbose_name='父id')
    controller = models.CharField(max_length=32, default='', verbose_name='控制器')
    method = models.CharField(max_length=64, default='', verbose_name='操作方法')
    path = models.CharField(max_length=32, null=True, blank=True, verbose_name='全路径')
    level = models.SmallIntegerField(default=0, verbose_name='级别')
    top_menu_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='顶级菜单的id')
    orderby = models.CharField(max_length=20, null=True, blank=True, verbose_name='排序')
    atime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'authority'


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name='角色名称', unique=True)
    authority_id = models.TextField(blank=True, null=True, verbose_name='权限ids,1,2,5')
    controller_method = models.TextField(blank=True, null=True, verbose_name='模块-方法')
    mtime = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')
    atime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'role'

class Template(models.Model):
    id = models.AutoField(primary_key=True)
    managerid = models.IntegerField(default=0, verbose_name='管理员id')
    filename = models.CharField(max_length=180, default='', verbose_name='文件名')
    contents = models.TextField(blank=True, null=True, verbose_name='文件内容')
    mtime = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')
    atime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'template'  # 指定数据库表名
        # managed = False  # 如果希望Django不管理此表，可以设置为False
        verbose_name = '模板'
        verbose_name_plural = '模板'


def have_authority(request, controller, method):
    """
    检查当前用户是否有权限访问指定的控制器方法。
    
    :param request: HttpRequest对象，用于获取session
    :param controller: 控制器名称（字符串）
    :param method: 方法名称（字符串）
    :return: 布尔值，表示是否有权限
    """
    role_id = request.session.get('role_id')
    if not role_id:
        return False
    
    try:
        # 将role_id转换为整数，并查询角色
        role = Role.objects.get(id=int(role_id))
    except (Role.DoesNotExist, ValueError):
        return False
    
    # 获取权限字符串并处理
    controller_method = role.controller_method.lower()
    allowed_methods = controller_method.split(',')
    
    # 构造目标方法字符串
    target = f"{controller.strip().lower()}-{method.strip().lower()}"
    
    return target in allowed_methods


class Cluster(models.Model):
    id = models.AutoField(primary_key=True)
    managerid = models.PositiveIntegerField(default=0, verbose_name='管理员id')
    clustername = models.CharField(max_length=180, default='', verbose_name='k8s集群名称')
    server = models.CharField(max_length=280, default='', verbose_name='k8s集群的地址')
    username = models.CharField(max_length=180, default='', verbose_name='k8s用户名称')
    token = models.TextField(blank=True, null=True, verbose_name='用户的token和用户证书key任选一样即可')
    certificate_authority_data = models.TextField(blank=True, null=True, verbose_name='集群证书')
    client_certificate_data = models.TextField(blank=True, null=True, verbose_name='用户的证书')
    client_key_data = models.TextField(blank=True, null=True, verbose_name='用户的key')
    mtime = models.PositiveIntegerField(blank=True, null=True, verbose_name='修改时间')
    atime = models.PositiveIntegerField(blank=True, null=True, verbose_name='创建时间')

    class Meta:
        db_table = 'clusters'
        verbose_name = '集群'
        verbose_name_plural = '集群'

    def __str__(self):
        return self.clustername


class CloudCredential(models.Model):
    provider = models.CharField(max_length=32, unique=True, verbose_name='provider')
    access_key = models.CharField(max_length=128, default='', blank=True, verbose_name='access key')
    secret_key = models.CharField(max_length=256, default='', blank=True, verbose_name='secret key')
    default_region = models.CharField(max_length=64, default='', blank=True, verbose_name='region')
    mtime = models.DateTimeField(auto_now=True, verbose_name='mtime')
    atime = models.DateTimeField(auto_now_add=True, verbose_name='atime')

    class Meta:
        db_table = 'cloud_credential'

    def __str__(self):
        return self.provider
