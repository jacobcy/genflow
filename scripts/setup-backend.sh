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

echo -e "${BLUE}🚀 Setting up GenFlow backend development environment...${NC}"

# 检查 Python 版本
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}❌ Error: Python $required_version or higher is required (you have $python_version)${NC}"
    echo -e "${YELLOW}💡 Tip: Install Python 3.12 using pyenv:${NC}"
    echo "   pyenv install 3.12"
    echo "   pyenv global 3.12"
    exit 1
fi

# 检查是否已安装 uv
if ! command -v uv &> /dev/null; then
    echo -e "${BLUE}📦 Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 进入后端目录
cd "$BACKEND_DIR"

# 创建虚拟环境并激活
echo -e "${BLUE}🔧 Creating virtual environment...${NC}"
python -m venv .venv
source .venv/bin/activate

# 使用 uv 安装项目依赖
echo -e "${BLUE}📚 Installing dependencies...${NC}"
cd "$PROJECT_ROOT"
uv pip install -e ".[dev]"

# 回到后端目录
cd "$BACKEND_DIR"

# 初始化预提交钩子
echo -e "${BLUE}🔧 Setting up pre-commit hooks...${NC}"
pre-commit install

# 创建 .env 文件（如果不存在）
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Creating .env file...${NC}"
    cp .env.example .env 2>/dev/null || echo -e "${YELLOW}⚠️  No .env.example found, skipping .env creation${NC}"
fi

# 初始化数据库
echo -e "${BLUE}🗄️ Initializing database...${NC}"
python "$PROJECT_ROOT/scripts/init_db.py"

echo -e "${GREEN}✅ Backend setup complete!${NC}"
echo -e "${BLUE}You can now run the development server with:${NC}"
echo "   cd backend && uvicorn src.main:app --reload"
echo ""
echo -e "${YELLOW}💡 Development Commands:${NC}"
echo "   • Run tests:            pytest"
echo "   • Format code:          black ."
echo "   • Lint code:            ruff check ."
echo "   • Type check:           mypy ."
echo "   • Update dependencies:  uv pip compile pyproject.toml -o requirements.txt"
echo ""
echo -e "${YELLOW}🔄 To update dependencies:${NC}"
echo "   1. Update versions in pyproject.toml"
echo "   2. Run: uv pip compile pyproject.toml -o requirements.txt"
echo "   3. Run: uv pip sync requirements.txt" 