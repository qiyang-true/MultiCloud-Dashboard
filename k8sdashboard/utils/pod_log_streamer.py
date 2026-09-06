"""
Pod日志流工具类
基于kubernetes client库实现稳定的Pod日志流获取
"""
import asyncio
import logging
import threading
import time
from typing import Optional, Callable, Any
from kubernetes import client, config, watch
from k8sdashboard.utils.kubernetes_config import _patch_rest_client_timeout
from kubernetes.client.rest import ApiException
from k8sdashboard.utils.kubernetes_config import get_kubeconfig_from_db

logger = logging.getLogger(__name__)


class PodLogStreamer:
    """
    Pod日志流处理器
    提供稳定的Kubernetes Pod日志流获取功能
    """
    
    def __init__(self, cluster_id: str, namespace: str, pod_name: str, container_name: Optional[str] = None):
        """
        初始化Pod日志流处理器
        
        Args:
            cluster_id: 集群ID
            namespace: Pod命名空间
            pod_name: Pod名称
            container_name: 容器名称（可选，如果Pod只有一个容器可以省略）
        """
        self.cluster_id = cluster_id
        self.namespace = namespace
        self.pod_name = pod_name
        self.container_name = container_name
        
        # 连接配置
        self.connection_timeout = 300  # 5分钟连接超时
        self.read_timeout = 36000  # 10小时读取超时
        self.max_retries = 10  # 增加重试次数
        self.base_retry_delay = 5  # 基础重试延迟
        self.max_retry_delay = 60  # 最大重试延迟
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        
        # 状态控制
        self.is_streaming = False
        self.stop_requested = False
        self.retry_count = 0
        self.last_heartbeat = time.time()
        self.connection_healthy = False
        
        # Kubernetes客户端
        self.v1_client = None
        self.watch = None
        
        # 回调函数
        self.on_log_line: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_status_change: Optional[Callable[[str], None]] = None

    def set_callbacks(self, 
                     on_log_line: Optional[Callable[[str], None]] = None,
                     on_error: Optional[Callable[[str], None]] = None,
                     on_status_change: Optional[Callable[[str], None]] = None):
        """
        设置回调函数
        
        Args:
            on_log_line: 日志行回调函数
            on_error: 错误回调函数
            on_status_change: 状态变化回调函数
        """
        self.on_log_line = on_log_line
        self.on_error = on_error
        self.on_status_change = on_status_change

    def _notify_status_change(self, status: str):
        """通知状态变化"""
        if self.on_status_change:
            try:
                self.on_status_change(status)
            except Exception as e:
                logger.error(f"状态变化回调函数执行失败: {e}")

    def _notify_error(self, error_msg: str):
        """通知错误"""
        if self.on_error:
            try:
                self.on_error(error_msg)
            except Exception as e:
                logger.error(f"错误回调函数执行失败: {e}")

    def _notify_log_line(self, log_line: str):
        """通知日志行"""
        if self.on_log_line:
            try:
                self.on_log_line(log_line)
                # 更新心跳时间
                self.last_heartbeat = time.time()
                self.connection_healthy = True
            except Exception as e:
                logger.error(f"日志行回调函数执行失败: {e}")

    def _check_connection_health(self) -> bool:
        """检查连接健康状态"""
        current_time = time.time()
        time_since_heartbeat = current_time - self.last_heartbeat
        
        # 如果超过心跳间隔时间没有收到数据，认为连接不健康
        if time_since_heartbeat > self.heartbeat_interval * 2:
            logger.warning(f"连接健康检查失败，超过 {self.heartbeat_interval * 2} 秒未收到数据")
            return False
        
        return True

    def _perform_health_check(self) -> bool:
        """执行健康检查"""
        try:
            if not self.v1_client:
                return False
            
            # 尝试获取Pod状态来验证连接
            pod = self.v1_client.read_namespaced_pod(
                name=self.pod_name,
                namespace=self.namespace
            )
            return pod is not None
        except Exception as e:
            logger.warning(f"健康检查失败: {e}")
            return False

    def _setup_kubernetes_client(self) -> bool:
        """
        设置Kubernetes客户端
        
        Returns:
            bool: 设置是否成功
        """
        try:
            # 获取kubeconfig配置
            config_path = get_kubeconfig_from_db(self.cluster_id)
            _patch_rest_client_timeout()
            config.load_kube_config(config_path)

            # 创建API客户端
            self.v1_client = client.CoreV1Api()
            
            # 测试连接
            self.v1_client.list_namespace()
            
            logger.info(f"Kubernetes客户端设置成功，集群ID: {self.cluster_id}")
            return True
            
        except Exception as e:
            logger.error(f"设置Kubernetes客户端失败: {e}")
            self._notify_error(f"连接Kubernetes集群失败: {e}")
            return False

    def _check_pod_exists(self) -> bool:
        """
        检查Pod是否存在
        
        Returns:
            bool: Pod是否存在
        """
        try:
            if not self.v1_client:
                return False
                
            pod = self.v1_client.read_namespaced_pod(
                name=self.pod_name,
                namespace=self.namespace
            )
            return pod is not None
            
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Pod {self.pod_name} 不存在")
                return False
            logger.error(f"检查Pod存在性时API错误: {e}")
            return False
        except Exception as e:
            logger.error(f"检查Pod存在性时出错: {e}")
            return False

    def _handle_retry(self):
        """处理重试逻辑，使用指数退避策略"""
        self.retry_count += 1
        if self.retry_count <= self.max_retries:
            # 计算指数退避延迟时间
            delay = min(self.base_retry_delay * (2 ** (self.retry_count - 1)), self.max_retry_delay)
            
            logger.info(f"第 {self.retry_count} 次重试，{delay} 秒后重连...")
            self._notify_error(f"连接中断，正在重试 ({self.retry_count}/{self.max_retries})，{delay}秒后重连...")
            
            # 重置连接健康状态
            self.connection_healthy = False
            
            time.sleep(delay)
        else:
            logger.error("已达到最大重试次数，停止重试")
            self._notify_error("连接失败，已达到最大重试次数")

    def start_streaming(self) -> bool:
        """
        开始日志流
        
        Returns:
            bool: 是否成功开始
        """
        if self.is_streaming:
            logger.warning("日志流已经在运行中")
            return False
            
        self.is_streaming = True
        self.stop_requested = False
        self.retry_count = 0
        
        # 在单独线程中运行
        self.stream_thread = threading.Thread(target=self._stream_logs, daemon=True)
        self.stream_thread.start()
        
        return True

    def stop_streaming(self):
        """停止日志流"""
        logger.info("请求停止日志流")
        self.stop_requested = True
        self.is_streaming = False
        
        if self.watch:
            self.watch.stop()
            
        # 等待线程结束
        if hasattr(self, 'stream_thread') and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=5)

    def _stream_logs(self):
        """在单独线程中流式获取Pod日志"""
        logger.info(f"开始Pod日志流: {self.namespace}/{self.pod_name}/{self.container_name}")
        self._notify_status_change("正在连接...")
        
        while not self.stop_requested and self.retry_count <= self.max_retries:
            try:
                # 设置Kubernetes客户端
                if not self._setup_kubernetes_client():
                    self._handle_retry()
                    continue
                
                # 检查Pod是否存在
                if not self._check_pod_exists():
                    self._notify_error(f"Pod {self.pod_name} 不存在或已被删除")
                    break
                
                # 创建watch对象
                self.watch = watch.Watch()
                
                # 重置重试计数和连接状态
                self.retry_count = 0
                self.connection_healthy = True
                self.last_heartbeat = time.time()
                self._notify_status_change("已连接，正在获取日志...")
                
                # 使用watch.stream获取日志流
                for log_line in self.watch.stream(
                    self.v1_client.read_namespaced_pod_log,
                    name=self.pod_name,
                    namespace=self.namespace,
                    container=self.container_name,
                    follow=True,
                    _preload_content=False,
                    _request_timeout=self.connection_timeout
                ):
                    if self.stop_requested:
                        break
                    
                    # 定期检查连接健康状态
                    if not self._check_connection_health():
                        logger.warning("连接健康检查失败，尝试重连")
                        self._handle_retry()
                        break
                        
                    try:
                        # 处理日志行 - watch.stream返回的可能是字符串或字节
                        if isinstance(log_line, bytes):
                            log_line_str = log_line.decode('utf-8').strip()
                        else:
                            log_line_str = str(log_line).strip()
                            
                        if log_line_str:
                            self._notify_log_line(log_line_str)
                    except UnicodeDecodeError as e:
                        logger.warning(f"日志行解码失败: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"处理日志行时出错: {e}")
                        continue
                
                # 如果正常退出循环，说明日志流结束
                if not self.stop_requested:
                    self._notify_status_change("日志流已结束")
                break
                        
            except ApiException as e:
                if e.status == 404:
                    logger.error(f"Pod {self.pod_name} 不存在")
                    self._notify_error(f"Pod {self.pod_name} 不存在")
                    break
                elif e.status == 403:
                    logger.error(f"没有权限访问Pod {self.pod_name}")
                    self._notify_error(f"没有权限访问Pod {self.pod_name}")
                    break
                else:
                    logger.error(f"Kubernetes API错误: {e}")
                    self._handle_retry()
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"获取Pod日志时出错: {error_msg}")
                
                # 检查是否是网络相关错误
                if any(keyword in error_msg.lower() for keyword in ['timeout', 'connection', 'network', 'unreachable']):
                    logger.warning(f"网络相关错误，尝试重连: {error_msg}")
                    self._handle_retry()
                elif "InvalidChunkLength" in error_msg or "Connection broken" in error_msg:
                    logger.warning(f"连接中断，尝试重连: {error_msg}")
                    self._handle_retry()
                elif "ReadTimeoutError" in error_msg or "ConnectTimeoutError" in error_msg:
                    logger.warning(f"超时错误，尝试重连: {error_msg}")
                    self._handle_retry()
                elif "SSL" in error_msg or "TLS" in error_msg:
                    logger.warning(f"SSL/TLS错误，尝试重连: {error_msg}")
                    self._handle_retry()
                elif "BadStatusLine" in error_msg or "IncompleteRead" in error_msg:
                    logger.warning(f"HTTP协议错误，尝试重连: {error_msg}")
                    self._handle_retry()
                else:
                    # 对于其他错误，先检查连接健康状态
                    if not self._check_connection_health():
                        logger.warning("连接健康检查失败，尝试重连")
                        self._handle_retry()
                    else:
                        logger.error(f"其他错误，停止重试: {error_msg}")
                        self._notify_error(f"获取Pod日志失败: {error_msg}")
                        break
        
        # 如果达到最大重试次数
        if self.retry_count > self.max_retries:
            self._notify_error("连接失败，已达到最大重试次数")
        
        self.is_streaming = False
        logger.info("Pod日志流已停止")


def stream_pod_logs(namespace: str, pod_name: str, container_name: Optional[str] = None, 
                   cluster_id: Optional[str] = None, on_log_line: Optional[Callable[[str], None]] = None):
    """
    便捷函数：流式获取Pod日志
    
    Args:
        namespace: Pod命名空间
        pod_name: Pod名称
        container_name: 容器名称（可选）
        cluster_id: 集群ID（可选，如果不提供则使用默认集群）
        on_log_line: 日志行回调函数
    """
    if not cluster_id:
        # 如果没有提供集群ID，尝试从数据库获取第一个可用集群
        try:
            from k8sdashboard.models import Cluster
            cluster = Cluster.objects.first()
            if not cluster:
                raise Exception("没有找到可用的集群配置")
            cluster_id = str(cluster.id)
        except Exception as e:
            logger.error(f"获取默认集群失败: {e}")
            return None
    
    streamer = PodLogStreamer(cluster_id, namespace, pod_name, container_name)
    
    if on_log_line:
        streamer.set_callbacks(on_log_line=on_log_line)
    
    return streamer
