#!/bin/bash

echo "Setting up GenFlow development environment..."

# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 创建必要的目录
mkdir -p logs
mkdir -p uploads/development

# 4. 设置环境变量
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template"
    echo "Please edit .env with your configurations"
fi

echo "Setup complete! To start development:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start Flask server: flask run"
echo "3. In another terminal, start Celery: celery -A wsgi.celery worker --loglevel=info" 