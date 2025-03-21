#!/bin/bash

# 确保脚本在错误时停止
set -e

# 设置颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}正在启动 LangManus 服务...${NC}"

# 进入项目根目录
cd "$(dirname "$0")/.." || exit

# 安装 LangManus Web 依赖
echo -e "${BLUE}安装 LangManus Web 依赖...${NC}"
cd integrations/langmanus-web
pnpm install
cd ../..

# 启动 LangManus API (后台运行)
echo -e "${BLUE}启动 LangManus API...${NC}"
cd integrations/langmanus
python server.py &
LANGMANUS_API_PID=$!
cd ../..

# 启动 LangManus Web (后台运行)
echo -e "${BLUE}启动 LangManus Web...${NC}"
cd integrations/langmanus-web
pnpm dev &
LANGMANUS_WEB_PID=$!
cd ../..

# 显示服务访问信息
echo -e "\n${GREEN}LangManus 服务启动成功！${NC}"
echo -e "${YELLOW}服务访问地址：${NC}"
echo -e "- LangManus API: ${GREEN}http://localhost:8000${NC}"
echo -e "- LangManus Web: ${GREEN}http://localhost:3000${NC}"

# 清理函数
cleanup() {
    echo -e "\n${BLUE}正在关闭服务...${NC}"
    kill $LANGMANUS_API_PID 2>/dev/null || true
    kill $LANGMANUS_WEB_PID 2>/dev/null || true
    exit 0
}

# 注册清理函数
trap cleanup EXIT

# 等待所有后台进程
wait 