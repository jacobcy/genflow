# GenFlow 快速启动指南

## 目录
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [项目配置](#项目配置)
- [开发指南](#开发指南)
- [常见问题](#常见问题)

## 环境要求

### 必需组件
- Docker Engine 24.0.0+
- Docker Compose v2.20.0+
- Git

### 推荐开发环境
- VSCode 或 JetBrains IDE
- Node.js 18+ (本地开发)
- Python 3.10+ (本地开发)

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-org/genflow.git
cd genflow
```

### 2. 环境配置
1. 复制环境变量模板：
```bash
# Docker 环境变量
cp ops/compose/.env.docker.example ops/compose/.env.docker

# 项目环境变量
cp .env.example .env
```

2. 根据需要修改环境变量：
   - 数据库配置
   - API密钥
   - 端口映射
   - 存储路径

### 3. 启动服务
```bash
# 创建必要的数据目录
mkdir -p ops/compose/data/{postgres,redis,nginx}

# 启动所有服务
cd ops/compose
docker compose up -d

# 查看服务状态
docker compose ps
```

### 4. 验证部署
- 前端页面：http://localhost:80
- 后端API：http://localhost:80/api
- 健康检查：http://localhost:80/health

## 项目配置

### 目录结构
```
genflow/
├── frontend/          # Next.js 前端项目
├── backend/           # Python 后端项目
├── ops/              
│   ├── compose/       # Docker Compose 配置
│   └── docker/        # Dockerfile 定义
├── docs/             # 项目文档
└── config/           # 配置文件
```

### 环境变量说明

#### Docker 环境变量 (.env.docker)
- \`NODE_ENV\`: Node.js 环境 (development/production)
- \`PYTHON_ENV\`: Python 环境 (development/production)
- \`POSTGRES_*\`: PostgreSQL 配置
- \`REDIS_URL\`: Redis 连接 URL
- \`*_PORT\`: 服务端口映射

#### 项目环境变量 (.env)
- 数据库连接配置
- API 密钥配置
- 认证相关配置
- 第三方服务集成配置

## 开发指南

### 本地开发
1. 启动依赖服务：
```bash
cd ops/compose
docker compose up -d postgres redis
```

2. 启动后端服务：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

3. 启动前端服务：
```bash
cd frontend
npm install
npm run dev
```

### 代码提交
```bash
git add .
git commit -m "feat: 添加新功能"
git push origin main
```

### 构建部署
```bash
# 构建镜像
docker compose build

# 部署服务
docker compose up -d
```

## 常见问题

### 1. 服务无法启动
- 检查端口占用：\`netstat -tulpn | grep LISTEN\`
- 检查日志：\`docker compose logs -f [service_name]\`
- 确认环境变量配置正确

### 2. 数据库连接失败
- 确认 PostgreSQL 服务运行状态
- 验证数据库连接信息
- 检查网络连接和防火墙设置

### 3. 前端访问后端 API 失败
- 确认 NEXT_PUBLIC_API_URL 配置正确
- 检查 CORS 配置
- 验证 nginx 代理配置

### 4. 文件权限问题
```bash
# 修复数据目录权限
sudo chown -R 1000:1000 ops/compose/data
```

### 5. 健康检查失败
- 检查服务日志
- 确认服务端口配置
- 验证依赖服务状态

## 获取帮助
- 查看详细文档：docs/
- 提交 Issue：GitHub Issues
- 技术支持：support@your-domain.com

## 许可证
MIT License - 详见 LICENSE 文件 