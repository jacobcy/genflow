# 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV FLASK_APP=wsgi.py
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 6060

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:6060", "wsgi:app"] 