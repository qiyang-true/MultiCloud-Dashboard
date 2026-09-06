import json
import asyncio
import threading
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from k8sdashboard.utils.kubernetes_config import get_kubeconfig_from_db
from k8sdashboard.utils.pod_log_streamer import PodLogStreamer
import logging

logger = logging.getLogger(__name__)

class PodLogConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = None
        self.pod_name = None
        self.cluster_id = None
        self.container_name = None
        self.log_streamer = None
        # 队列用于线程安全的消息传递
        self.log_queue = asyncio.Queue()
        self.error_queue = asyncio.Queue()
        self.status_queue = asyncio.Queue()

    async def connect(self):
        # 从URL路径中获取参数
        self.namespace = self.scope['url_route']['kwargs']['namespace']
        self.pod_name = self.scope['url_route']['kwargs']['pod_name']
        self.container_name = self.scope['url_route']['kwargs']['container_name']
        # 从查询参数中获取集群ID
        query_string = self.scope['query_string'].decode()
        if 'cluster_id=' in query_string:
            self.cluster_id = query_string.split('cluster_id=')[1].split('&')[0]
        
        # 加入房间组
        self.room_group_name = f'pod_logs_{self.namespace}_{self.pod_name}_{self.container_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # 开始日志流
        await self.start_log_stream()

    async def disconnect(self, close_code):
        # 停止日志流
        if self.log_streamer:
            self.log_streamer.stop_streaming()
        
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message_type = text_data_json.get('type')
        
        if message_type == 'start_logs':
            await self.start_log_stream()
        elif message_type == 'stop_logs':
            if self.log_streamer:
                self.log_streamer.stop_streaming()

    async def start_log_stream(self):
        """启动Pod日志流"""
        if self.log_streamer and self.log_streamer.is_streaming:
            return
            
        # 创建日志流处理器
        self.log_streamer = PodLogStreamer(
            cluster_id=self.cluster_id,
            namespace=self.namespace,
            pod_name=self.pod_name,
            container_name=self.container_name
        )
        
        # 设置回调函数 - 使用队列机制
        self.log_streamer.set_callbacks(
            on_log_line=self._queue_log_line,
            on_error=self._queue_error,
            on_status_change=self._queue_status
        )
        
        # 开始流式获取日志
        self.log_streamer.start_streaming()
        
        # 启动处理队列的任务
        asyncio.create_task(self._process_queues())

    def _queue_log_line(self, log_line: str):
        """将日志行放入队列"""
        try:
            self.log_queue.put_nowait(log_line)
        except Exception as e:
            logger.error(f"无法将日志行放入队列: {e}")

    def _queue_error(self, error_message: str):
        """将错误消息放入队列"""
        try:
            self.error_queue.put_nowait(error_message)
        except Exception as e:
            logger.error(f"无法将错误消息放入队列: {e}")

    def _queue_status(self, status: str):
        """将状态消息放入队列"""
        try:
            self.status_queue.put_nowait(status)
        except Exception as e:
            logger.error(f"无法将状态消息放入队列: {e}")

    async def _process_queues(self):
        """处理队列中的消息"""
        while True:
            try:
                # 处理日志队列
                if not self.log_queue.empty():
                    log_line = self.log_queue.get_nowait()
                    await self._send_log_line(log_line)
                
                # 处理错误队列
                if not self.error_queue.empty():
                    error_msg = self.error_queue.get_nowait()
                    await self._send_error_message(error_msg)
                
                # 处理状态队列
                if not self.status_queue.empty():
                    status_msg = self.status_queue.get_nowait()
                    await self._send_status_message(status_msg)
                
                # 短暂休眠避免过度占用CPU
                await asyncio.sleep(0.01)
                
            except asyncio.QueueEmpty:
                # 队列为空，短暂休眠
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"处理队列时出错: {e}")
                await asyncio.sleep(0.1)

    async def _send_log_line(self, log_line):
        """发送单行日志到WebSocket"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'log_message',
                'message': log_line,
                'pod_name': self.pod_name,
                'namespace': self.namespace,
                'container_name': self.container_name
            }
        )

    async def _send_error_message(self, error_message):
        """发送错误消息到WebSocket"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'error_message',
                'message': error_message,
                'pod_name': self.pod_name,
                'namespace': self.namespace,
                'container_name': self.container_name
            }
        )

    async def _send_status_message(self, status_message):
        """发送状态消息到WebSocket"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'status_message',
                'message': status_message,
                'pod_name': self.pod_name,
                'namespace': self.namespace,
                'container_name': self.container_name
            }
        )

    async def log_message(self, event):
        """处理日志消息"""
        import time
        await self.send(text_data=json.dumps({
            'type': 'log',
            'message': event['message'],
            'pod_name': event['pod_name'],
            'namespace': event['namespace'],
            'container_name': event['container_name'],
            'timestamp': time.time()
        }))

    async def error_message(self, event):
        """处理错误消息"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': event['message'],
            'pod_name': event['pod_name'],
            'namespace': event['namespace'],
            'container_name': event['container_name']
        }))

    async def status_message(self, event):
        """处理状态消息"""
        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': event['message'],
            'pod_name': event['pod_name'],
            'namespace': event['namespace'],
            'container_name': event['container_name']
        }))
