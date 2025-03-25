#!/bin/bash

# 确保脚本在错误时退出
set -e

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# 检查后端目录是否存在
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Error: Backend directory not found${NC}"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found, running setup...${NC}"
    "$PROJECT_ROOT/scripts/setup-backend.sh"
fi

# 激活虚拟环境
source "$PROJECT_ROOT/.venv/bin/activate"

# 设置 PYTHONPATH
export PYTHONPATH="$BACKEND_DIR/src:$PYTHONPATH"

# 检查依赖是否完整安装
echo -e "${BLUE}📦 Verifying dependencies...${NC}"
if ! python -c "import fastapi, uvicorn, sqlalchemy, asyncpg" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Some dependencies are missing, reinstalling...${NC}"
    cd "$PROJECT_ROOT"
    uv pip install -e ".[all]"
fi

# 检查 .env 文件
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found, creating from example...${NC}"
    cd "$BACKEND_DIR"
    if [ -f .env.development ]; then
        echo -e "${BLUE}📝 Using development environment...${NC}"
        cp .env.development .env
    elif [ -f .env.example ]; then
        echo -e "${BLUE}📝 Using example environment...${NC}"
        cp .env.example .env
    else
        echo -e "${YELLOW}⚠️  Creating default .env file...${NC}"
        cat > .env << EOL
# 基本配置
NODE_ENV=development
PYTHON_ENV=development

# 服务端口配置
BACKEND_PORT=8080
FRONTEND_PORT=6060

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/genflow
REDIS_URL=redis://localhost:6379/0

# 安全配置
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 管理员配置
ADMIN_EMAIL=admin@genflow.dev
ADMIN_PASSWORD=admin123456

# 日志配置
LOG_LEVEL=DEBUG
EOL
    fi
fi

# 检查数据库连接
echo -e "${BLUE}🔍 Checking database connection...${NC}"
cd "$BACKEND_DIR"
python << EOL
import asyncio
import asyncpg
from os import getenv
from dotenv import load_dotenv

async def check_db():
    try:
        load_dotenv()
        db_url = getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')
        conn = await asyncpg.connect(db_url)
        await conn.close()
        print(f"${GREEN}✅ Database connection successful${NC}")
        return True
    except Exception as e:
        print(f"${RED}❌ Database connection failed: {str(e)}${NC}")
        return False

if not asyncio.run(check_db()):
    print(f"${YELLOW}⚠️  Please check your database configuration in .env${NC}")
    print(f"${YELLOW}💡 Make sure PostgreSQL is running and the database exists${NC}")
EOL

# 启动后端服务
echo -e "${BLUE}🚀 Starting backend server...${NC}"
echo -e "${GREEN}📝 API will be available at: http://localhost:${BACKEND_PORT:-8080}${NC}"
echo -e "${GREEN}📚 API docs will be available at: http://localhost:${BACKEND_PORT:-8080}/docs${NC}"

cd "$BACKEND_DIR/src"
if [ -n "$TMUX" ]; then
    echo -e "${BLUE}Running in tmux session${NC}"
    exec uvicorn main:app --reload --host 0.0.0.0 --port ${BACKEND_PORT:-8080} --reload-dir .
else
    uvicorn main:app --reload --host 0.0.0.0 --port ${BACKEND_PORT:-8080} --reload-dir .
fi

# 保持终端窗口打开
echo "Backend server stopped. Press any key to close this window..."
read -n 1
