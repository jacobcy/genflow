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

# 检查前端目录是否存在
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Error: Frontend directory not found${NC}"
    exit 1
fi

# 检查 node_modules 是否存在
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found, running setup...${NC}"
    "$PROJECT_ROOT/scripts/setup-frontend.sh"
fi

# 检查 .env 文件
if [ ! -f "$FRONTEND_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found, creating from example...${NC}"
    if [ -f "$FRONTEND_DIR/.env.example" ]; then
        cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
    else
        echo -e "${YELLOW}⚠️  Creating default .env file...${NC}"
        cat > "$FRONTEND_DIR/.env" << EOL
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_APP_URL=http://localhost:${FRONTEND_PORT:-6060}
NEXT_PUBLIC_APP_NAME=GenFlow
NEXT_PUBLIC_APP_DESCRIPTION="AI Agent Flow Engine"
EOL
    fi
fi

# 进入前端目录
cd "$FRONTEND_DIR"

# 启动前端服务
echo -e "${BLUE}🚀 Starting frontend server...${NC}"
echo -e "${GREEN}📝 Frontend will be available at: http://localhost:${FRONTEND_PORT:-6060}${NC}"

if [ -n "$TMUX" ]; then
    echo -e "${BLUE}Running in tmux session${NC}"
    exec PORT=${FRONTEND_PORT:-6060} pnpm dev
else
    PORT=${FRONTEND_PORT:-6060} pnpm dev
fi

# 保持终端窗口打开
echo "Frontend server stopped. Press any key to close this window..."
read -n 1
