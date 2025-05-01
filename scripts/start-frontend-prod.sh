#!/bin/bash
# 启动前端生产环境脚本

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

# 检查前端目录是否存在
if [ ! -d "${FRONTEND_DIR}" ]; then
  echo -e "${RED}错误：找不到前端目录 '${FRONTEND_DIR}'${NC}"
  exit 1
fi

cd "${FRONTEND_DIR}"

echo -e "${GREEN}进入前端目录: ${FRONTEND_DIR}${NC}"

# 检查包管理器 (npm 或 yarn)
USE_YARN=false
if [ -f "yarn.lock" ]; then
  USE_YARN=true
  echo -e "${YELLOW}检测到 yarn.lock，将使用 yarn。${NC}"
elif [ -f "package-lock.json" ]; then
  echo -e "${YELLOW}检测到 package-lock.json，将使用 npm。${NC}"
elif [ -f "package.json" ]; then
  echo -e "${YELLOW}未找到 lock 文件，将使用 npm。${NC}"
else
  echo -e "${RED}错误：在 ${FRONTEND_DIR} 中未找到 package.json。${NC}"
  exit 1
fi

# 安装依赖
echo -e "${GREEN}正在安装前端依赖...${NC}"
if $USE_YARN; then
  yarn install --frozen-lockfile || { echo -e "${RED}yarn install 失败${NC}"; exit 1; }
else
  npm install --legacy-peer-deps || { echo -e "${RED}npm install 失败${NC}"; exit 1; }
fi

# 执行生产构建
echo -e "${GREEN}正在构建前端生产版本...${NC}"
if $USE_YARN; then
  yarn build || { echo -e "${RED}yarn build 失败${NC}"; exit 1; }
else
  npm run build || { echo -e "${RED}npm run build 失败${NC}"; exit 1; }
fi

# 检查构建目录 (通常是 build 或 dist)
BUILD_DIR="build"
if [ ! -d "${BUILD_DIR}" ]; then
  if [ -d "dist" ]; then
    BUILD_DIR="dist"
  else
    echo -e "${RED}错误：未找到构建目录 ('build' 或 'dist')。${NC}"
    exit 1
  fi
fi

echo -e "${GREEN}前端构建完成，输出目录: ${BUILD_DIR}${NC}"

# 检查并安装 serve (如果需要)
if ! command -v npx &> /dev/null; then
    echo -e "${RED}错误：找不到 npx 命令。请确保 Node.js 和 npm 已正确安装。${NC}"
    exit 1
fi

if ! npx serve --version &> /dev/null; then
    echo -e "${YELLOW}未找到 'serve' 包，正在尝试安装...${NC}"
    if $USE_YARN; then
        yarn add serve || { echo -e "${RED}安装 'serve' 失败 (yarn)${NC}"; exit 1; }
    else
        npm install serve || { echo -e "${RED}安装 'serve' 失败 (npm)${NC}"; exit 1; }
    fi
fi

# 启动生产服务器
PORT=3000
echo -e "${GREEN}正在端口 ${PORT} 上启动前端生产服务器，服务目录: ${BUILD_DIR}${NC}"
echo -e "${YELLOW}访问 http://localhost:${PORT}${NC}"

# 使用 npx 运行本地安装的 serve
npx serve -s "${BUILD_DIR}" -l ${PORT}

# 如果 serve 启动失败
if [ $? -ne 0 ]; then
    echo -e "${RED}启动前端生产服务器失败。${NC}"
    exit 1
fi

echo -e "${GREEN}前端生产服务器已停止。${NC}"

cd "${PROJECT_ROOT}"

exit 0 