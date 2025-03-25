#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}🔍 Testing GenFlow development environment...${NC}"

# 测试后端
echo -e "${BLUE}Testing backend...${NC}"
cd "$PROJECT_ROOT/backend"

# 检查Python环境
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Running setup...${NC}"
    cd "$PROJECT_ROOT"
    bash scripts/setup-backend.sh
fi

# 激活虚拟环境
source .venv/bin/activate

# 测试 uvicorn 命令
if ! command -v uvicorn &> /dev/null; then
    echo -e "${RED}❌ Error: uvicorn not found. Please check backend installation.${NC}"
    exit 1
fi

# 测试导入模块
python -c "
try:
    from src.main import app
    print('✅ Backend imports successful')
except Exception as e:
    print(f'❌ Backend import error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Backend test failed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend test successful!${NC}"

# 测试前端
echo -e "${BLUE}Testing frontend...${NC}"
cd "$PROJECT_ROOT/frontend"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Running setup...${NC}"
    cd "$PROJECT_ROOT"
    bash scripts/setup-frontend.sh
fi

# 测试 next 命令
if ! pnpm next -v &> /dev/null; then
    echo -e "${RED}❌ Error: next.js not found. Please check frontend installation.${NC}"
else
    echo -e "${GREEN}✅ Next.js found!${NC}"
fi

# 检查 package.json 中的必要脚本
echo -e "${BLUE}Checking package.json scripts...${NC}"
REQUIRED_SCRIPTS=("dev" "build" "start")
MISSING_SCRIPTS=()

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if ! grep -q "\"$script\":" package.json; then
        MISSING_SCRIPTS+=("$script")
    fi
done

if [ ${#MISSING_SCRIPTS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All required scripts found in package.json!${NC}"
else
    echo -e "${YELLOW}⚠️  Missing scripts in package.json: ${MISSING_SCRIPTS[*]}${NC}"
fi

echo -e "${GREEN}✅ Environment tests completed!${NC}"
echo -e "${BLUE}You can now start the development servers:${NC}"
echo -e "${YELLOW}Backend:${NC} cd backend && uvicorn src.main:app --reload"
echo -e "${YELLOW}Frontend:${NC} cd frontend && pnpm dev"
