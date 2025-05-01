#!/bin/bash
# 启动完整生产环境脚本 (后端 + 前端)

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}正在启动 GenFlow 生产环境...${NC}"

# 检查必要的启动脚本是否存在
BACKEND_SCRIPT="${SCRIPT_DIR}/start-backend.sh"
FRONTEND_SCRIPT="${SCRIPT_DIR}/start-frontend-prod.sh"

if [ ! -f "${BACKEND_SCRIPT}" ]; then
  echo -e "${RED}错误：找不到后端启动脚本 '${BACKEND_SCRIPT}'${NC}"
  exit 1
fi

if [ ! -f "${FRONTEND_SCRIPT}" ]; then
  echo -e "${RED}错误：找不到前端生产启动脚本 '${FRONTEND_SCRIPT}'${NC}"
  exit 1
fi

# 确保脚本有执行权限
chmod +x "${BACKEND_SCRIPT}"
chmod +x "${FRONTEND_SCRIPT}"

# 定义日志文件
BACKEND_LOG="${SCRIPT_DIR}/../logs/backend-prod.log"
FRONTEND_LOG="${SCRIPT_DIR}/../logs/frontend-prod.log"

# 创建日志目录 (如果不存在)
mkdir -p "$(dirname "${BACKEND_LOG}")"
mkdir -p "$(dirname "${FRONTEND_LOG}")"

# 启动后端生产服务 (后台运行)
echo -e "${YELLOW}正在后台启动后端生产服务...${NC}"
echo "日志输出到: ${BACKEND_LOG}"
nohup "${BACKEND_SCRIPT}" > "${BACKEND_LOG}" 2>&1 &
BACKEND_PID=$!
sleep 2 # 等待一小段时间确保进程启动

# 检查后端进程是否仍在运行
if ps -p ${BACKEND_PID} > /dev/null; then
   echo -e "${GREEN}后端服务已启动 (PID: ${BACKEND_PID})。${NC}"
else
   echo -e "${RED}后端服务启动失败。请检查日志: ${BACKEND_LOG}${NC}"
   # 可以选择是否退出
   # exit 1
fi

# 启动前端生产服务 (后台运行)
echo -e "${YELLOW}正在后台启动前端生产服务...${NC}"
echo "日志输出到: ${FRONTEND_LOG}"
nohup "${FRONTEND_SCRIPT}" > "${FRONTEND_LOG}" 2>&1 &
FRONTEND_PID=$!
sleep 2 # 等待一小段时间确保进程启动

# 检查前端进程是否仍在运行
if ps -p ${FRONTEND_PID} > /dev/null; then
   echo -e "${GREEN}前端服务已启动 (PID: ${FRONTEND_PID})。${NC}"
   echo -e "${YELLOW}前端通常运行在 http://localhost:3000${NC}"
else
   echo -e "${RED}前端服务启动失败。请检查日志: ${FRONTEND_LOG}${NC}"
   # 可以选择是否退出
   # exit 1
fi

echo -e "${GREEN}GenFlow 生产环境启动命令已执行。${NC}"
echo -e "${YELLOW}使用 'pkill -f start-backend.sh' 和 'pkill -f start-frontend-prod.sh' 或 'pkill -f serve' 来停止服务。${NC}"

exit 0 