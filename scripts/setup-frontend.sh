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
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}🚀 Setting up GenFlow frontend development environment...${NC}"

# 检查 Node.js 版本
required_node_version="18.0.0"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Error: Node.js is not installed${NC}"
    echo -e "${YELLOW}💡 Tip: Install Node.js using nvm:${NC}"
    echo "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "   nvm install 18"
    echo "   nvm use 18"
    exit 1
fi

node_version=$(node -v | cut -d 'v' -f 2)
if [ "$(printf '%s\n' "$required_node_version" "$node_version" | sort -V | head -n1)" != "$required_node_version" ]; then
    echo -e "${RED}❌ Error: Node.js 18 or higher is required (you have $node_version)${NC}"
    exit 1
fi

# 检查 pnpm
if ! command -v pnpm &> /dev/null; then
    echo -e "${BLUE}📦 Installing pnpm...${NC}"
    npm install -g pnpm
fi

# 进入前端目录
cd "$FRONTEND_DIR"

# 安装依赖
echo -e "${BLUE}📚 Installing dependencies...${NC}"
pnpm install

# 检查并创建环境配置文件
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Creating .env file...${NC}"
    cp .env.example .env 2>/dev/null || echo -e "${YELLOW}⚠️  No .env.example found, creating default .env${NC}"
    if [ ! -f .env ]; then
        cat > .env << EOL
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME=GenFlow
NEXT_PUBLIC_APP_DESCRIPTION="AI Agent Flow Engine"
EOL
    fi
fi

# 检查 TypeScript 配置
if [ ! -f tsconfig.json ]; then
    echo -e "${RED}❌ Error: tsconfig.json not found${NC}"
    exit 1
fi

# 运行类型检查
echo -e "${BLUE}🔍 Running type check...${NC}"
pnpm type-check

# 运行 lint
echo -e "${BLUE}🔍 Running lint...${NC}"
pnpm lint

echo -e "${GREEN}✅ Frontend setup complete!${NC}"
echo -e "${BLUE}You can now start the development server with:${NC}"
echo "   cd frontend && pnpm dev"
echo ""
echo -e "${YELLOW}💡 Development Commands:${NC}"
echo "   • Start dev server:     pnpm dev"
echo "   • Build for production: pnpm build"
echo "   • Start production:     pnpm start"
echo "   • Type check:          pnpm type-check"
echo "   • Lint:                pnpm lint"
echo "   • Format code:         pnpm format"
echo ""
echo -e "${YELLOW}🔄 To update dependencies:${NC}"
echo "   1. Update versions in package.json"
echo "   2. Run: pnpm update"
echo "   3. Run: pnpm install" 