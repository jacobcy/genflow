# GenFlow 脚本工具集

本目录包含用于 GenFlow 项目开发、部署和维护的脚本工具集。以下是各脚本的功能说明和使用方法。

## 核心脚本

### 环境设置

| 脚本 | 描述 | 用法 |
|------|------|------|
| `setup-backend.sh` | 设置后端开发环境，安装依赖 | `./setup-backend.sh` |
| `setup-frontend.sh` | 设置前端开发环境，安装依赖 | `./setup-frontend.sh` |
| `test-environment.sh` | 测试开发环境配置是否正确 | `./test-environment.sh` |

### 开发工具

| 脚本 | 描述 | 用法 |
|------|------|------|
| `start-backend-debug.sh` | 以调试模式启动后端服务 | `./start-backend-debug.sh` |
| `start-frontend.sh` | 启动前端开发服务器 | `./start-frontend.sh` |
| `test-db-connection.sh` | 测试数据库连接 | `./test-db-connection.sh` |
| `initialize_database.py` | 初始化数据库结构和基础数据 | `python initialize_database.py` |
| `db_tools.py` | 数据库管理工具 | `python db_tools.py [command]` |
| `debug_redis.py` | Redis 调试工具 | `python debug_redis.py [command]` |

### 集成开发环境

| 脚本 | 描述 | 用法 |
|------|------|------|
| `start-dev.sh` | 启动完整开发环境（前后端） | `./start-dev.sh` |
| `check-submodules.sh` | 检查子模块状态 | `./check-submodules.sh` |
| `update-submodules.sh` | 更新所有子模块 | `./update-submodules.sh` |

### 子模块服务

| 脚本 | 描述 | 用法 |
|------|------|------|
| `start-daily.sh` | 启动日报子模块服务 | `./start-daily.sh` |
| `start-md.sh` | 启动 Markdown 解析子模块服务 | `./start-md.sh` |
| `start-manus.sh` | 启动手稿子模块服务 | `./start-manus.sh` |

## 生产部署脚本

| 脚本 | 描述 | 用法 |
|------|------|------|
| `start-backend.sh` | 以生产模式启动后端服务 | `./start-backend.sh` |
| `start-frontend-prod.sh` | 构建并以生产模式启动前端服务 | `./start-frontend-prod.sh` |
| `start-prod.sh` | 启动完整的生产环境（后端+前端） | `./start-prod.sh` |

## 废弃脚本

以下脚本已废弃，不再使用：

| 脚本 | 原功能 | 替代方案 |
|------|--------|----------|
| *暂无废弃脚本* | | |

## 使用示例

### 完整开发环境搭建

```bash
# 1. 设置后端环境
./scripts/setup-backend.sh

# 2. 设置前端环境
./scripts/setup-frontend.sh

# 3. 启动开发环境
./scripts/start-dev.sh
```

### 启动完整生产环境

```bash
./scripts/start-prod.sh
```

### 单独启动后端（生产模式）

```bash
./scripts/start-backend.sh
```

### 单独启动前端（生产模式）

```bash
./scripts/start-frontend-prod.sh
```

### 测试数据库连接

```bash
./scripts/test-db-connection.sh
```

## 脚本依赖关系

- `start-dev.sh` 依赖于 `initialize_database.py` 进行数据库初始化
- `start-backend-debug.sh`, `start-backend.sh`, `start-prod.sh` 都依赖于已配置好的环境变量
- `start-frontend-prod.sh` 依赖前端项目的构建脚本和 `serve` 工具
- `start-prod.sh` 依赖 `start-backend.sh` 和 `start-frontend-prod.sh`
- 所有脚本都假设已激活 Python 虚拟环境

## 注意事项

1. 运行脚本前确保位于项目根目录
2. 确保脚本有执行权限 (`chmod +x scripts/*.sh`)
3. 后端服务默认在 8081 端口运行，前端开发服务在 6060 端口，前端生产服务在 3000 端口
4. 环境变量配置在 `.env` 和 `backend/.env` 文件中
