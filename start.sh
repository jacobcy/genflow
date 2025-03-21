#!/bin/bash

# 确保脚本在错误时停止
set -e

# 设置颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}正在启动 GenFlow 服务集群...${NC}"

# 同步最新依赖
echo -e "${BLUE}正在同步依赖...${NC}"
uv pip sync requirements.txt

# 启动 Markdown 编辑器 (后台运行)
echo -e "${BLUE}启动 Markdown 编辑器...${NC}"
./scripts/start-md.sh --prod &
MD_EDITOR_PID=$!

# 启动 LangManus 服务 (后台运行)
echo -e "${BLUE}启动 LangManus 服务...${NC}"
./scripts/start-manus.sh &
MANUS_PID=$!

# 显示服务访问信息
echo -e "\n${GREEN}服务启动成功！${NC}"
echo -e "${YELLOW}服务访问地址：${NC}"
echo -e "- Markdown 编辑器: ${GREEN}http://localhost:9000/md${NC}"
echo -e "- LangManus API: ${GREEN}http://localhost:8000${NC}"
echo -e "- LangManus Web: ${GREEN}http://localhost:3000${NC}"
echo -e "- GenFlow 主应用: ${GREEN}http://localhost:6060${NC}"

# 启动主应用
echo -e "\n${BLUE}启动 GenFlow 主应用...${NC}"
uv run genflow

# 清理函数
cleanup() {
    echo -e "\n${BLUE}正在关闭服务...${NC}"
    kill $MD_EDITOR_PID 2>/dev/null || true
    kill $MANUS_PID 2>/dev/null || true
    exit 0
}

# 注册清理函数
trap cleanup EXIT

# 等待所有后台进程
wait