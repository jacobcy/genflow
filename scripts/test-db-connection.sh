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

echo -e "${BLUE}🔍 测试数据库连接...${NC}"

# 激活虚拟环境
echo -e "${BLUE}🔧 激活虚拟环境...${NC}"
source "$PROJECT_ROOT/.venv/bin/activate"

# 设置正确的 PYTHONPATH - 确保能找到所有模块
export PYTHONPATH="$BACKEND_SRC:$BACKEND_DIR:$PROJECT_ROOT:$PYTHONPATH"

# 输出调试信息
echo -e "${BLUE}ℹ️ 环境信息:${NC}"
echo -e "  PYTHONPATH: ${YELLOW}$PYTHONPATH${NC}"
echo -e "  Python版本: ${YELLOW}$(python --version)${NC}"

# 执行Python脚本测试数据库连接
cd "$PROJECT_ROOT"
cat > /tmp/test_db.py << EOF
import asyncio
from backend.src.db.session import get_async_session

async def test_db_connection():
    print('尝试连接数据库...')
    try:
        async for db in get_async_session():
            await db.execute('SELECT 1')
            print('\033[0;32m✅ 数据库连接成功\033[0m')
            break
    except Exception as e:
        print(f'\033[0;31m❌ 数据库连接失败: {e}\033[0m')

asyncio.run(test_db_connection())
EOF

python /tmp/test_db.py
rm /tmp/test_db.py

echo -e "${BLUE}🔍 测试完成${NC}"
