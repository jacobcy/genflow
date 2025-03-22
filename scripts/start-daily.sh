#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录
PROJECT_ROOT="$SCRIPT_DIR/.."

# 加载环境变量
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
    echo -e "${GREEN}已加载环境配置文件${NC}"
else
    echo -e "${YELLOW}未找到 .env 文件，将使用默认配置${NC}"
fi

# 设置默认值（如果环境变量未定义）
DAILY_HOT_UI_PORT=${DAILY_HOT_UI_PORT:-6699}
DAILY_HOT_API_PORT=${DAILY_HOT_API_PORT:-6688}
DAILY_HOT_CACHE_TIME=${DAILY_HOT_CACHE_TIME:-60}

echo -e "${BLUE}使用配置:${NC}"
echo -e "UI 端口: ${GREEN}$DAILY_HOT_UI_PORT${NC}"
echo -e "API 端口: ${GREEN}$DAILY_HOT_API_PORT${NC}"
echo -e "缓存时间: ${GREEN}${DAILY_HOT_CACHE_TIME}分钟${NC}"

# 检查必要的环境变量
if [ -z "$DAILY_HOT_UI_PORT" ] || [ -z "$DAILY_HOT_API_PORT" ]; then
    echo -e "${RED}错误: 请在 .env 文件中设置 DAILY_HOT_UI_PORT 和 DAILY_HOT_API_PORT${NC}"
    exit 1
fi

# 定义服务目录
DAILY_HOT_API_DIR="$PROJECT_ROOT/integrations/daily-hot-api"
DAILY_HOT_UI_DIR="$PROJECT_ROOT/integrations/daily-hot"

# 检查服务目录是否存在
if [ ! -d "$DAILY_HOT_API_DIR" ] || [ ! -d "$DAILY_HOT_UI_DIR" ]; then
    echo -e "${RED}错误: 服务目录不存在，请确保已正确初始化 Git 子模块${NC}"
    echo -e "${YELLOW}提示: 运行以下命令初始化子模块:${NC}"
    echo -e "git submodule update --init --recursive"
    exit 1
fi

# 启动 DailyHot API 服务
start_api_service() {
    echo -e "${BLUE}正在启动 DailyHot API 服务...${NC}"
    cd "$DAILY_HOT_API_DIR" || exit
    
    # 检查是否已安装依赖
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}正在安装 API 服务依赖...${NC}"
        pnpm install
    fi

    # 创建/更新 .env 文件
    echo "PORT=$DAILY_HOT_API_PORT" > .env
    echo "CACHE_TIME=${DAILY_HOT_CACHE_TIME:-60}" >> .env
    if [ ! -z "$DAILY_HOT_PROXY_HOST" ]; then
        echo "PROXY_HOST=$DAILY_HOT_PROXY_HOST" >> .env
    fi
    if [ ! -z "$DAILY_HOT_PROXY_PORT" ]; then
        echo "PROXY_PORT=$DAILY_HOT_PROXY_PORT" >> .env
    fi

    # 启动服务
    echo -e "${GREEN}正在启动 API 服务 (端口: $DAILY_HOT_API_PORT)${NC}"
    pnpm dev &
    API_PID=$!
    echo $API_PID > api.pid
}

# 启动 DailyHot UI 服务
start_ui_service() {
    echo -e "${BLUE}正在启动 DailyHot UI 服务...${NC}"
    cd "$DAILY_HOT_UI_DIR" || exit
    
    # 检查是否已安装依赖
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}正在安装 UI 服务依赖...${NC}"
        pnpm install
    fi

    # 创建/更新 .env 文件
    echo "VITE_API_URL=http://localhost:$DAILY_HOT_API_PORT" > .env

    # 启动服务
    echo -e "${GREEN}正在启动 UI 服务 (端口: $DAILY_HOT_UI_PORT)${NC}"
    VITE_PORT=$DAILY_HOT_UI_PORT pnpm dev &
    UI_PID=$!
    echo $UI_PID > ui.pid
}

# 清理函数
cleanup() {
    echo -e "${YELLOW}正在关闭服务...${NC}"
    if [ -f "$DAILY_HOT_API_DIR/api.pid" ]; then
        kill $(cat "$DAILY_HOT_API_DIR/api.pid")
        rm "$DAILY_HOT_API_DIR/api.pid"
    fi
    if [ -f "$DAILY_HOT_UI_DIR/ui.pid" ]; then
        kill $(cat "$DAILY_HOT_UI_DIR/ui.pid")
        rm "$DAILY_HOT_UI_DIR/ui.pid"
    fi
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

# 主流程
echo -e "${BLUE}=== DailyHot 服务启动脚本 ===${NC}"

# 启动服务
start_api_service
start_ui_service

echo -e "${GREEN}所有服务已启动:${NC}"
echo -e "API 服务: ${BLUE}http://localhost:$DAILY_HOT_API_PORT${NC}"
echo -e "UI 服务: ${BLUE}http://localhost:$DAILY_HOT_UI_PORT${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"

# 保持脚本运行
wait