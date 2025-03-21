# GenFlow

GenFlow 是一个基于 AI 的内容创作和发布平台，帮助自媒体创作者高效生产优质内容。

## 功能特点

- AI 辅助写作
- 多平台内容发布
- 文章管理系统
- 数据分析报告

## 快速开始

1. 克隆项目：
```bash
git clone https://github.com/yourusername/genflow.git
cd genflow
```

2. 配置环境：
```bash
cp .env.example .env
# 编辑 .env 文件，根据你的环境修改配置
```

> **重要提示：** 首次使用时请务必修改管理员密码！
> - ADMIN_EMAIL：管理员邮箱，默认为 admin@genflow.ai
> - ADMIN_PASSWORD：管理员密码，默认为 admin123456

3. 选择安装方式：

### 方式一：使用 uv（推荐）

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

### 方式二：Docker 部署

安装 Docker：
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# MacOS
brew install --cask docker

# Windows
# 下载并安装 Docker Desktop: https://www.docker.com/products/docker-desktop
```

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 方式三：手动安装（不推荐）

1. 安装系统依赖：
```bash
# PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb genflow_dev

# MacOS
brew install postgresql
brew services start postgresql
createdb genflow_dev

# Windows
# 下载并安装 PostgreSQL: https://www.postgresql.org/download/windows/
# 使用 pgAdmin 或命令行创建数据库 genflow_dev

# Redis
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# MacOS
brew install redis
brew services start redis

# Windows
# 下载并安装 Redis for Windows
```

2. 创建 Python 环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 启动服务：

开发环境（默认）：
```bash
python run.py
```

生产环境：
```bash
python run.py --env production
```

自定义主机和端口：
```bash
python run.py --host 0.0.0.0 --port 8000
```

## 项目结构

```
genflow/
├── app/                    # 后端应用
│   ├── api/               # API 接口
│   │   ├── __init__.py
│   │   ├── auth.py       # 认证相关接口
│   │   └── platforms.py   # 平台相关接口
│   ├── models/            # 数据模型
│   │   ├── user.py
│   │   ├── article.py
│   │   └── platform.py
│   ├── services/          # 业务逻辑
│   │   ├── auth_service.py
│   │   └── platform_service.py
│   ├── tasks/             # 异步任务
│   │   ├── __init__.py
│   │   └── article_tasks.py
│   └── utils/             # 工具函数
│       ├── logger.py
│       └── errors.py
├── config/                # 配置文件
│   ├── __init__.py
│   ├── development.py
│   └── production.py
├── tests/                 # 测试用例
├── .env                   # 环境变量
├── .env.example          # 环境变量模板
├── requirements.txt      # 项目依赖
└── run.py               # 启动脚本
```

## 开发指南

1. **配置说明**
- 开发环境配置在 `config/development.py`
- 生产环境配置在 `config/production.py`
- 环境变量配置在 `.env` 文件中

2. **数据库**
- 开发环境默认使用本地 PostgreSQL
- 生产环境通过环境变量配置数据库连接

数据库重置
```bash docker环境
# 停止并删除现有容器
docker-compose down

# 删除数据卷（这会清除所有数据！）
docker volume rm genflow_postgres_data

# 重新启动服务
docker-compose up -d
```

```bash 手动环境
# 删除现有数据库
dropdb genflow_dev

# 创建新数据库
createdb genflow_dev

# 启动应用（会自动创建表和管理员账号）
uv run genflow
```

3. **异步任务**
- 使用 Celery 处理异步任务
- Redis 作为消息代理
- 文章发布等耗时操作都在后台处理

## 测试

运行测试：
```bash
uv pip sync requirements.txt[dev]  # 安装开发依赖
pytest
```

生成覆盖率报告：
```bash
pytest --cov=app tests/
```

## 部署

1. **Docker 部署**：
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

2. **传统部署**：
```bash
# 安装依赖
uv pip sync requirements.txt

# 启动服务
uv run genflow --env production --host 0.0.0.0
```

## 许可证

MIT License 

## 访问系统

1. 打开浏览器访问：http://localhost:6060
2. 使用管理员账号登录：
   - 邮箱：ADMIN_EMAIL 配置值（默认：admin@genflow.ai）
   - 密码：ADMIN_PASSWORD 配置值（默认：admin123456）

> **安全提示：** 为了系统安全，强烈建议在首次使用时修改默认管理员密码！ 

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