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
BACKEND_SRC="$BACKEND_DIR/src"

echo -e "${BLUE}🚀 Setting up GenFlow backend development environment...${NC}"

# 检查是否已安装 uv
if ! command -v uv &> /dev/null; then
    echo -e "${BLUE}📦 Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # 添加 uv 到当前会话的 PATH
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 创建虚拟环境并激活
echo -e "${BLUE}🔧 Creating virtual environment with Python 3.12...${NC}"
cd "$PROJECT_ROOT"
uv venv -p 3.12
source .venv/bin/activate

# 使用 uv 安装依赖
echo -e "${BLUE}📚 Installing dependencies...${NC}"

# 首先安装数据库依赖
echo -e "${BLUE}📦 Installing database dependencies...${NC}"
uv pip install sqlalchemy asyncpg psycopg alembic

# 安装开发工具
echo -e "${BLUE}📦 Installing development tools...${NC}"
uv pip install pre-commit

# 安装核心依赖
echo -e "${BLUE}📦 Installing core dependencies...${NC}"
uv pip install --pre python-readability  # 允许预发布版本

# 然后安装项目依赖
echo -e "${BLUE}📦 Installing project dependencies...${NC}"
uv pip install -e ".[dev,backend]" --pre  # 允许所有依赖使用预发布版本

# 初始化预提交钩子
echo -e "${BLUE}🔧 Setting up pre-commit hooks...${NC}"
pre-commit install

# 创建 backend/.env 文件（如果不存在）
if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    echo -e "${BLUE}📝 Creating backend/.env file...${NC}"
    cd "$PROJECT_ROOT/backend"
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

# 初始化数据库
echo -e "${BLUE}🗄️ Initializing database...${NC}"

# 确保在正确的目录中执行数据库初始化
cd "$PROJECT_ROOT"

# 设置正确的 PYTHONPATH - 确保能找到所有模块
export PYTHONPATH="$BACKEND_SRC:$BACKEND_DIR:$PROJECT_ROOT:$PYTHONPATH"

# 尝试初始化数据库
if python "$PROJECT_ROOT/scripts/init_db.py"; then
    echo -e "${GREEN}✅ Database initialization successful${NC}"
else
    echo -e "${RED}❌ Database initialization failed${NC}"
    echo -e "${YELLOW}💡 Make sure PostgreSQL is running and the database exists${NC}"
    echo -e "${YELLOW}💡 You can create the database manually with:${NC}"
    echo "   createdb genflow"
fi

echo -e "${GREEN}✅ Backend setup complete!${NC}"
echo -e "${BLUE}You can now run the development server with:${NC}"
echo "   ./scripts/start-dev.sh"
echo ""
echo -e "${YELLOW}💡 Development Commands:${NC}"
echo "   • Run tests:            pytest"
echo "   • Format code:          black ."
echo "   • Sort imports:         isort ."
echo "   • Lint code:            ruff check ."
echo "   • Type check:          mypy ."
echo "   • Update dependencies: uv pip compile pyproject.toml -o requirements.txt"
echo ""
echo -e "${YELLOW}🔄 To update dependencies:${NC}"
echo "   1. Update versions in pyproject.toml"
echo "   2. Run: uv pip compile pyproject.toml -o requirements.txt"
echo "   3. Run: uv pip sync requirements.txt"
