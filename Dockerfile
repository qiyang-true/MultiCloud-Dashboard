# 使用官方Python 3.6.8镜像作为基础
FROM python:3.6.8

# 设置环境变量，确保Python输出直接显示在容器日志中
ENV PYTHONUNBUFFERED 1

# 创建并设置工作目录
RUN mkdir /app
WORKDIR /app

# 配置国内PyPI镜像加速（可选）
RUN mkdir -p /root/.pip && \
    echo "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple" > /root/.pip/pip.conf

# 先复制依赖文件并安装，利用Docker层缓存优化
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目到容器中
COPY . /app/

# 暴露Django默认端口
EXPOSE 8000

# 使用daphne启动ASGI生产服务器
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "dashboard.asgi:application"]