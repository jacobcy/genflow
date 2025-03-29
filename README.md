# GenFlow

GenFlow 是一个基于 AI 的内容创作和发布平台，帮助自媒体创作者高效生产优质内容。本项目采用最小可行产品（MVP）原则设计，确保核心功能高效运行，同时避免过度设计和不必要的业务逻辑假设。

## 核心设计原则

- **最小可行产品（MVP）**：只实现必要的功能，避免猜测性扩展
- **关注点分离**：清晰分离数据模型、基础设施和业务逻辑
- **适配器模式**：使用适配器隔离底层细节，提高可维护性
- **统一接口**：提供一致的 API 接口访问核心功能

## 系统架构

GenFlow 采用分层架构设计：

```
┌─────────────────────────────────┐
│            业务层               │ ← 使用核心模型，实现业务逻辑
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│          模型/接口层            │ ← 提供统一访问接口，管理数据模型
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│            基础层               │ ← 处理配置、数据库等基础功能
└─────────────────────────────────┘
```

### 模型层核心组件

- **ContentManager**：统一访问入口，协调各管理器
- **DBAdapter**：数据库访问适配器，处理持久化
- **ConfigService**：配置加载和管理服务
- **各种Manager**：管理风格、内容类型等专项功能

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

## 核心模型使用指南

GenFlow 核心模型采用最小可行产品原则设计，专注于提供必要的数据结构和接口，而不预设业务逻辑。以下是正确使用核心模型的方法：

### 1. 初始化

在使用任何功能前，必须先初始化核心管理器：

```python
from core.models.content_manager import ContentManager

# 初始化 ContentManager（系统启动时）
ContentManager.initialize(use_db=True)
```

### 2. 配置管理

系统配置存储在 JSON 文件中，支持以下配置类型：

- 内容类型 (`config/content_types/*.json`)
- 文章风格 (`config/styles/*.json`)
- 平台配置 (`config/platforms/*.json`)

配置文件会在系统启动时自动加载，也可以使用以下方法手动加载：

```python
# 从配置文件同步到数据库
ContentManager.migrate_content_types_config()
ContentManager.migrate_article_styles_config()
ContentManager.migrate_platforms_config()
```

### 3. 访问数据模型

通过 ContentManager 统一访问各类数据模型：

```python
# 获取内容类型
content_type = ContentManager.get_content_type("blog")

# 获取文章风格
style = ContentManager.get_article_style("formal")

# 获取平台配置
platform = ContentManager.get_platform("medium")
```

### 4. 数据操作

核心数据操作示例：

```python
# 创建新话题
topic_id = ContentManager.save_topic({
    "title": "示例话题",
    "description": "这是一个示例话题描述"
})

# 获取话题
topic = ContentManager.get_topic(topic_id)

# 保存文章
article_id = ContentManager.save_article({
    "title": "示例文章",
    "content": "文章内容...",
    "topic_id": topic_id,
    "content_type": "blog",
    "style_id": "formal"
})
```

### 5. 扩展核心模型

可通过添加新的配置文件扩展功能：

```json
// 新的内容类型 (config/content_types/new_type.json)
{
  "id": "new_type",
  "name": "新内容类型",
  "description": "这是一个新的内容类型",
  "compatible_styles": ["formal", "casual"]
}
```

## 项目配置

### 目录结构
```
genflow/
├── frontend/          # Next.js 前端项目
├── backend/           # FastAPI 后端项目
├── scripts/           # 项目脚本
├── ops/               # 运维相关
│   ├── compose/       # Docker Compose 配置
│   └── docker/        # Dockerfile 定义
├── docs/              # 项目文档
├── config/            # 配置文件
|   ├── content_types/ # 内容类型配置
|   ├── styles/        # 文章风格配置
|   └── platforms/     # 平台配置
└── core/              # 核心模型
    ├── models/        # 数据模型定义
    │   ├── infra/     # 基础设施组件
    │   ├── article/   # 文章模型
    │   ├── style/     # 风格模型
    │   ├── db/        # 数据库支持
    │   └── content_manager.py # 统一访问接口
    └── controllers/   # 控制器层
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

## 最佳实践

### 遵循 MVP 原则

1. **避免过度设计**
   - 只实现必要功能，不猜测未来需求
   - 当需要添加新功能时，先评估其必要性

2. **层次分离**
   - 核心模型专注于数据管理，不包含业务逻辑
   - 业务逻辑应在上层实现，依赖核心模型提供的接口

3. **错误处理**
   - 检查返回值，不假设操作总是成功
   - 实现适当的重试和失败处理策略

4. **配置管理**
   - 通过配置文件扩展功能
   - 避免直接修改核心组件代码

## 常见问题

### 1. 启动脚本权限问题
```bash
# 添加执行权限
chmod +x scripts/*.sh scripts/*.py
```

### 2. 数据库连接问题
- 检查数据库服务是否运行
- 验证连接字符串格式是否正确
- 确认用户权限设置

### 3. 初始化失败问题
- 确保配置文件位置正确
- 检查配置文件格式是否有效
- 查看日志获取详细错误信息

## 开发团队

- 项目负责人：[联系方式]
- 技术支持：[邮箱]
- 问题反馈：[Issue 链接]

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
