# GenFlow

GenFlow 是一个基于 AI 的内容创作和发布平台，帮助自媒体创作者高效生产优质内容。

## 功能特点

- AI 辅助写作
- 多平台内容发布
- 文章管理系统
- 数据分析报告

## 环境要求

### 必需组件
- Python 3.12+
- Node.js 18+
- pnpm 8+
- PostgreSQL 15+
- Redis 7+
- uv (Python 包管理工具)
- Git

### 数据库要求
- PostgreSQL 15+ (主数据库)
  - 默认端口：5432
  - 需要创建数据库：genflow
- Redis 7+ (缓存和会话管理)
  - 默认端口：6379
  - 建议开启持久化

### 推荐开发环境
- VSCode 或 JetBrains IDE
- tmux (推荐，用于更好的开发体验)
- Docker (可选，用于容器化部署)

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/jacobcy/genflow.git
cd genflow
```

### 2. 环境配置

#### 方案一：使用配置脚本（推荐）

1. 配置前端环境：
```bash
./scripts/setup-frontend.sh
```

2. 配置后端环境：
```bash
./scripts/setup-backend.sh
```

3. 初始化数据库：
```bash
./scripts/init_db.py
```

#### 方案二：手动配置

1. 复制环境变量模板：
```bash
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
```

2. 安装依赖：
```bash
# 前端依赖
cd frontend && pnpm install

# 后端依赖
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 3. 启动服务

#### 方案一：一键启动（推荐）
```bash
./scripts/start-dev.sh
```
这会在 tmux 会话中同时启动前端和后端服务，并提供日志监控窗口。

#### 方案二：分别启动
1. 启动后端：
```bash
./scripts/start-backend.sh
```

2. 启动前端：
```bash
./scripts/start-frontend.sh
```

#### 方案三：Docker 部署
```bash
cd ops/compose
docker compose up -d
```

### 4. 验证部署
- 前端页面：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 项目配置

### 目录结构
```
genflow/
├── frontend/          # Next.js 前端项目
├── backend/           # FastAPI 后端项目
├── scripts/          # 项目脚本
│   ├── setup-frontend.sh    # 前端环境配置
│   ├── setup-backend.sh     # 后端环境配置
│   ├── start-dev.sh        # 开发环境启动
│   ├── start-frontend.sh   # 前端服务启动
│   ├── start-backend.sh    # 后端服务启动
│   ├── init_db.py         # 数据库初始化
│   └── test-environment.sh # 环境测试
├── ops/
│   ├── compose/       # Docker Compose 配置
│   └── docker/        # Dockerfile 定义
├── docs/             # 项目文档
├── config/           # 配置文件
└── integrations/     # 第三方服务集成
    └── daily-hot/    # DailyHot 服务
```

### 环境变量说明

#### 前端环境变量 (.env)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME=GenFlow
NEXT_PUBLIC_APP_DESCRIPTION="AI Agent Flow Engine"
```

#### 后端环境变量 (.env)
```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/genflow

# 认证配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 管理员账户
ADMIN_EMAIL=admin@genflow.ai
ADMIN_PASSWORD=admin123456
```

## 子模块管理

GenFlow 使用 Git 子模块管理第三方集成组件。请遵循以下规则处理子模块：

### 子模块原则

1. **不修改子模块内容** - 子模块内容应保持与原始仓库同步
2. **通过原仓库更新** - 需要修改子模块功能时，应向原仓库提交 PR

### 子模块操作

```bash
# 克隆项目时获取所有子模块
git clone --recurse-submodules https://github.com/jacobcy/genflow.git

# 如果已克隆项目，初始化子模块
git submodule update --init --recursive

# 更新所有子模块到最新版本
git submodule update --remote

# 恢复子模块到未修改状态
cd integrations/<module-name>
git reset --hard
git clean -fd
```

### 自动化脚本

项目提供了自动化脚本来简化子模块管理：

```bash
# 检查子模块状态
./scripts/check-submodules.sh

# 恢复子模块到原始状态
./scripts/check-submodules.sh --fix

# 更新所有子模块到最新版本
./scripts/update-submodules.sh

# 更新所有子模块并自动提交（无需确认）
./scripts/update-submodules.sh --force
```

详细规则请参考项目根目录下的 `.gitmodules-config` 文件。

## 开发指南

### 环境测试
在开始开发前，可以运行环境测试脚本确保所有配置正确：
```bash
./scripts/test-environment.sh
```

### tmux 会话管理
```bash
# 列出所有会话
tmux ls

# 连接到现有会话
tmux attach -t genflow

# 终止会话
tmux kill-session -t genflow
```

### 常用命令
```bash
# 类型检查
cd frontend && pnpm type-check
cd backend && mypy .

# 代码格式化
cd frontend && pnpm format
cd backend && black .

# 运行测试
cd frontend && pnpm test
cd backend && pytest
```

## 常见问题

### 1. 启动脚本权限问题
```bash
# 添加执行权限
chmod +x scripts/*.sh scripts/*.py
```

### 2. 前端依赖安装失败
```bash
# 清理依赖并重新安装
cd frontend
rm -rf node_modules
pnpm install
```

### 3. 后端虚拟环境问题
```bash
# 重新创建虚拟环境
cd backend
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### 4. 数据库连接失败
- 检查数据库服务是否运行
- 验证数据库连接信息
- 确保已运行 init_db.py

### 5. 文件权限问题
```bash
# 修复数据目录权限
sudo chown -R $(id -u):$(id -g) ops/compose/data
```

## 更多资源

- 详细文档：[docs/](docs/)
- API 文档：http://localhost:8000/docs
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
