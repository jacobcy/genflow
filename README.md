# GenFlow

GenFlow 是一个基于 AI 的内容创作和发布平台，帮助自媒体创作者高效生产优质内容。

## 功能特点

- AI 辅助写作
- 多平台内容发布
- 文章管理系统
- 数据分析报告

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

> **重要提示：** 首次使用时请务必修改管理员密码！
> - ADMIN_EMAIL：管理员邮箱，默认为 admin@genflow.ai
> - ADMIN_PASSWORD：管理员密码，默认为 admin123456

### 3. 启动服务

#### 方式一：Docker 部署（推荐）
```bash
# 创建必要的数据目录
mkdir -p ops/compose/data/{postgres,redis,nginx}

# 启动所有服务
cd ops/compose
docker compose up -d

# 查看服务状态
docker compose ps
```

#### 方式二：使用 uv

1. 安装 uv：
```bash
# MacOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. 安装依赖：
```bash
# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip sync requirements.txt
```

3. 安装项目：
```bash
uv pip install -e .
```

4. 启动服务：
```bash
# 开发环境（默认）
uv run genflow

# 生产环境
uv run genflow --env production

# 自定义主机和端口
uv run genflow --host 0.0.0.0 --port 8000
```

#### 方式三：手动安装
详见完整文档 [docs/quickstart.md](docs/quickstart.md)

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

### 数据库操作

数据库重置（Docker环境）:
```bash
# 停止并删除现有容器
docker-compose down

# 删除数据卷（这会清除所有数据！）
docker volume rm genflow_postgres_data

# 重新启动服务
docker-compose up -d
```

数据库重置（手动环境）:
```bash
# 删除现有数据库
dropdb genflow_dev

# 创建新数据库
createdb genflow_dev

# 启动应用（会自动创建表和管理员账号）
uv run genflow
```

## 常见问题

### 1. 服务无法启动
- 检查端口占用：`netstat -tulpn | grep LISTEN`
- 检查日志：`docker compose logs -f [service_name]`
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

## 访问系统

1. 打开浏览器访问：http://localhost:80
2. 使用管理员账号登录：
   - 邮箱：ADMIN_EMAIL 配置值（默认：admin@genflow.ai）
   - 密码：ADMIN_PASSWORD 配置值（默认：admin123456）

> **安全提示：** 为了系统安全，强烈建议在首次使用时修改默认管理员密码！

## 更多资源

- 详细文档：[docs/quickstart.md](docs/quickstart.md)
- 提交 Issue：GitHub Issues
- 技术支持：support@your-domain.com

## 许可证

MIT License - 详见 LICENSE 文件

## 数据库设计

### 核心表结构

#### users 用户表
| 字段名         | 类型         | 说明                |
|----------------|--------------|---------------------|
| id             | SERIAL       | 主键                |
| username       | VARCHAR(80)  | 唯一用户名          |
| email          | VARCHAR(120) | 唯一邮箱            |
| password_hash  | VARCHAR(256) | 加密后的密码        |
| role           | VARCHAR(20)  | 用户角色 (user/admin)|
| created_at     | TIMESTAMP    | 创建时间            |

#### articles 文章表
| 字段名         | 类型         | 说明                |
|----------------|--------------|---------------------|
| id             | SERIAL       | 主键                |
| title          | VARCHAR(200) | 文章标题            |
| content        | TEXT         | 文章内容            |
| user_id        | INTEGER      | 外键关联users表     |
| created_at     | TIMESTAMP    | 创建时间            |
| updated_at     | TIMESTAMP    | 最后更新时间        | 