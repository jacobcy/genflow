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

echo -e "${BLUE}🚀 启动 GenFlow 后端服务 (调试模式)...${NC}"

# 激活虚拟环境
echo -e "${BLUE}🔧 激活虚拟环境...${NC}"
source "$PROJECT_ROOT/.venv/bin/activate"

# 设置正确的 PYTHONPATH - 确保能找到所有模块
export PYTHONPATH="$BACKEND_SRC:$BACKEND_DIR:$PROJECT_ROOT:$PYTHONPATH"

# 确保日志目录存在
echo -e "${BLUE}📝 确保日志目录存在...${NC}"
mkdir -p "$BACKEND_DIR/logs"
touch "$BACKEND_DIR/logs/app.log"
touch "$BACKEND_DIR/logs/access.log"
touch "$BACKEND_DIR/logs/error.log"

# 确保在后端源码目录运行
cd "$BACKEND_SRC"

# 输出调试信息
echo -e "${BLUE}ℹ️ 环境信息:${NC}"
echo -e "  PYTHONPATH: ${YELLOW}$PYTHONPATH${NC}"
echo -e "  当前目录: ${YELLOW}$(pwd)${NC}"
echo -e "  日志目录: ${YELLOW}$BACKEND_DIR/logs${NC}"

# 启动 - 使用绝对路径指向日志配置文件
echo -e "${GREEN}✅ 正在启动开发服务器...${NC}"
uvicorn main:app --reload --host 0.0.0.0 --port 8090 --log-config="$BACKEND_DIR/logconfig.yml"
