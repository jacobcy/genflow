# GenFlow 快速启动指南

## 目录
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [项目配置](#项目配置)
- [开发指南](#开发指南)
- [常见问题](#常见问题)

## 环境要求

### 必需组件
- Python 3.12+
- Node.js 18+
- pnpm 8+
- Git
- PostgreSQL 15+
- Redis 7+
- uv (Python 包管理工具)

### 数据库要求
- PostgreSQL 15+ (主数据库)
  - 默认端口：5432
  - 需要创建数据库：genflow
- Redis 7+ (缓存和会话管理)
  - 默认端口：6379
  - 建议开启持久化

### 推荐开发环境
- VSCode 或 JetBrains IDE
- tmux (可选，用于更好的开发体验)
- Docker (可选，用于容器化部署)

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-org/genflow.git
cd genflow
```

### 2. 环境配置

#### 安装 uv
```bash
# 使用 pip 安装 uv
pip install uv

# 或使用 curl 安装
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 数据库配置
```bash
# PostgreSQL 配置
createdb genflow  # 创建数据库

# Redis 配置检查
redis-cli ping    # 应返回 PONG
```

#### 前端环境配置
```bash
# 运行前端环境配置脚本
./scripts/setup-frontend.sh
```

#### 后端环境配置
```bash
# 运行后端环境配置脚本
./scripts/setup-backend.sh
```

#### 初始化数据库
```bash
# 运行数据库初始化脚本
./scripts/init_db.py
```

### 3. 启动服务

#### 方案一：一键启动（推荐）
```bash
./scripts/start-dev.sh
```
这会同时启动前端和后端服务。如果安装了 tmux，会在 tmux 会话中启动；如果没有，会尝试打开新的终端窗口。

#### 方案二：分别启动
1. 启动后端：
```bash
./scripts/start-backend.sh
```

2. 启动前端：
```bash
./scripts/start-frontend.sh
```

#### 方案三：手动启动
1. 启动后端：
```bash
cd backend
source .venv/bin/activate  # 如果使用虚拟环境
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

2. 启动前端：
```bash
cd frontend
pnpm dev
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
└── config/           # 配置文件
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

## 开发指南

### 环境测试
在开始开发前，可以运行环境测试脚本确保所有配置正确：
```bash
./scripts/test-environment.sh
```

### 开发工作流
1. 确保环境配置正确
2. 启动开发服务器（使用 start-dev.sh）
3. 进行代码修改
4. 运行测试和类型检查
5. 提交代码

### 代码提交规范
```bash
git add .
git commit -m "feat: 添加新功能"
git push origin main
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
pip install -r requirements.txt
```

### 4. 数据库连接失败
- 检查数据库服务是否运行
- 验证数据库连接信息
- 确保已运行 init_db.py

### 5. tmux 会话管理
```bash
# 列出所有会话
tmux ls

# 连接到现有会话
tmux attach -t genflow

# 终止会话
tmux kill-session -t genflow
```

## 获取帮助
- 查看详细文档：docs/
- 提交 Issue：GitHub Issues
- 技术支持：support@your-domain.com

## 许可证
MIT License - 详见 LICENSE 文件
