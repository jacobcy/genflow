#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo "使用方法: $0 [选项]"
    echo "选项:"
    echo "  -d, --dev     开发模式 (默认，使用开发服务器)"
    echo "  -p, --prod    生产模式 (构建并使用 serve 启动)"
    echo "  -h, --help    显示此帮助信息"
}

# 默认模式
MODE="dev"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dev)
            MODE="dev"
            shift
            ;;
        -p|--prod)
            MODE="prod"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

echo -e "${BLUE}Starting Markdown Editor...${NC}"

# 进入 md 编辑器目录
cd "$(dirname "$0")/../integrations/md" || exit

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing dependencies...${NC}"
    npm install
fi

# 检查是否安装了 serve
if [ "$MODE" = "prod" ] && ! command -v serve &> /dev/null; then
    echo -e "${BLUE}Installing serve package...${NC}"
    npm install -g serve
fi

# 根据模式启动服务
if [ "$MODE" = "dev" ]; then
    echo -e "${YELLOW}Starting in DEVELOPMENT mode${NC}"
    echo -e "${GREEN}Development server will be available at:${NC}"
    echo -e "${GREEN}http://localhost:9000/md${NC}"
    VITE_PORT=9000 npm run dev
else
    echo -e "${YELLOW}Starting in PRODUCTION mode${NC}"
    echo -e "${BLUE}Building project...${NC}"
    npm run build
    echo -e "${GREEN}Production server will be available at:${NC}"
    echo -e "${GREEN}http://localhost:9000/md${NC}"
    serve -s dist -l 9000
fi 