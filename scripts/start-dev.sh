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

echo -e "${BLUE}🚀 Starting GenFlow development environment...${NC}"

# 检查子模块状态
echo -e "${BLUE}🔍 Checking submodules status...${NC}"
if [ -f "$PROJECT_ROOT/scripts/check-submodules.sh" ]; then
    # 给脚本添加执行权限
    chmod +x "$PROJECT_ROOT/scripts/check-submodules.sh"
    # 执行子模块检查脚本
    "$PROJECT_ROOT/scripts/check-submodules.sh"

    # 如果检查到子模块有更改，提醒用户
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Some submodules have uncommitted changes.${NC}"
        echo -e "${YELLOW}💡 Run this command to fix:${NC}"
        echo "   $PROJECT_ROOT/scripts/check-submodules.sh --fix"

        # 询问用户是否继续
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}Exiting...${NC}"
            exit 1
        fi
    fi
fi

# 检查环境
echo -e "${BLUE}🔍 Checking development environment...${NC}"

# 检查 PostgreSQL 是否已安装和运行
if ! command -v pg_isready &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not installed${NC}"
    echo -e "${YELLOW}💡 Please install PostgreSQL:${NC}"
    echo "   • MacOS: brew install postgresql@14"
    echo "   • Ubuntu/Debian: sudo apt install postgresql"
    echo "   • CentOS/RHEL: sudo yum install postgresql-server"
    exit 1
fi

if ! pg_isready &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not running${NC}"
    echo -e "${YELLOW}💡 Start PostgreSQL service:${NC}"
    echo "   • MacOS: brew services start postgresql@14"
    echo "   • Ubuntu/Debian: sudo systemctl start postgresql"
    echo "   • CentOS/RHEL: sudo systemctl start postgresql"
    exit 1
fi

# 加载环境变量
echo -e "${BLUE}🔍 Loading environment configurations...${NC}"

# 检查并加载环境变量
load_env() {
    local env_file=$1
    if [ -f "$env_file" ]; then
        echo -e "${GREEN}✓ Loading configuration from: $env_file${NC}"
        # 只导出非注释行且包含等号的行
        while IFS='=' read -r key value; do
            # 跳过注释行和空行
            if [[ $key != \#* ]] && [[ -n $key ]] && [[ -n $value ]]; then
                # 移除可能的引号
                value=$(echo "$value" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
                # 导出环境变量
                export "$key=$value"
            fi
        done < <(grep -v '^[[:space:]]*#' "$env_file" | grep '=')
    fi
}

# 优先加载根目录的环境配置
if [ -f "$PROJECT_ROOT/.env" ]; then
    load_env "$PROJECT_ROOT/.env"
elif [ -f "$PROJECT_ROOT/.env.example" ]; then
    echo -e "${YELLOW}⚠️  No .env found in root directory. Creating from .env.example...${NC}"
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    load_env "$PROJECT_ROOT/.env"
else
    echo -e "${RED}❌ No .env or .env.example found in root directory${NC}"
    exit 1
fi

# 检查后端环境
echo -e "${BLUE}Checking backend environment...${NC}"
if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Creating backend .env from root configuration...${NC}"
    # 提取后端所需的环境变量
    {
        echo "# Backend Environment - Generated from root configuration"
        echo ""
        grep -E "^(DB_|REDIS_|JWT_|API_|LOG_|UPLOAD_|OPENAI_)" "$PROJECT_ROOT/.env" | grep -v '#'
        echo ""
        echo "# Backend specific configuration"
        echo "HOST=0.0.0.0"
        echo "PORT=$BACKEND_PORT"
    } > "$PROJECT_ROOT/backend/.env"
fi

# 检查前端环境
echo -e "${BLUE}Checking frontend environment...${NC}"
if [ ! -f "$PROJECT_ROOT/frontend/.env" ]; then
    echo -e "${YELLOW}⚠️  Creating frontend .env from root configuration...${NC}"
    # 提取前端所需的环境变量
    {
        echo "# Frontend Environment - Generated from root configuration"
        echo ""
        grep -E "^(PORT=|OPENAI_|AI_ASSISTANT_|LANGMANUS_|DAILY_HOT_)" "$PROJECT_ROOT/.env" | grep -v '#'
        echo ""
        echo "# Frontend specific configuration"
        echo "BACKEND_URL=http://localhost:$BACKEND_PORT"
    } > "$PROJECT_ROOT/frontend/.env"
fi

# 检查并设置虚拟环境
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${YELLOW}⚠️ Virtual environment not found. Running setup-backend.sh...${NC}"
    "$PROJECT_ROOT/scripts/setup-backend.sh"
else
    # 激活虚拟环境
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# 检查数据库连接和初始化
echo -e "${BLUE}🔍 Checking database...${NC}"

# 设置 PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/backend/src:$PYTHONPATH"

python << EOL
import asyncio
import asyncpg
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# 添加项目根目录和后端源码目录到 Python 路径
project_root = Path("$PROJECT_ROOT")
backend_src = project_root / "backend" / "src"
sys.path.extend([str(project_root), str(backend_src)])

# 加载环境变量，优先使用项目根目录的 .env
env_file = project_root / ".env"
backend_env = project_root / "backend" / ".env"
backend_env_dev = project_root / "backend" / ".env.development"
backend_env_example = project_root / "backend" / ".env.example"

if env_file.exists():
    load_dotenv(env_file)
elif backend_env.exists():
    load_dotenv(backend_env)
elif backend_env_dev.exists():
    load_dotenv(backend_env_dev)
elif backend_env_example.exists():
    load_dotenv(backend_env_example)

async def check_db():
    try:
        # 优先使用分离的数据库配置参数
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'postgres')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_name = os.getenv('DB_NAME', 'genflow_dev')

        # 构建数据库 URL
        db_url = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'

        # 如果存在完整的 DATABASE_URL，则使用它
        db_url = os.getenv('DATABASE_URL', db_url)

        # 确保 URL 格式正确
        if 'postgresql+asyncpg://' in db_url:
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')

        print(f"${BLUE}Connecting to database: {db_url}${NC}")

        # 尝试连接到 PostgreSQL 服务器
        conn = await asyncpg.connect(
            db_url,
            timeout=3
        )
        await conn.close()
        return True
    except asyncpg.InvalidCatalogNameError:
        # 数据库不存在
        print(f"${YELLOW}⚠️  Database does not exist. Will initialize it.${NC}")
        return False
    except Exception as e:
        print(f"${RED}❌ Database connection error: {str(e)}${NC}")
        return None

result = asyncio.run(check_db())
exit(0 if result is not None else 1)
EOL

DB_CHECK_RESULT=$?

if [ $DB_CHECK_RESULT -eq 1 ]; then
    echo -e "${RED}❌ Failed to connect to PostgreSQL. Please check your database configuration.${NC}"
    exit 1
elif [ $DB_CHECK_RESULT -eq 0 ]; then
    echo -e "${BLUE}🗄️  Initializing database...${NC}"
    # 确保在正确的目录中
    cd "$PROJECT_ROOT"
    # 运行数据库初始化脚本
    python "$PROJECT_ROOT/scripts/initialize_database.py"
fi

# 检查前端环境
echo -e "${BLUE}Checking frontend environment...${NC}"
cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
    pnpm install
fi

# 检查是否安装了 tmux
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}⚠️ tmux not found. Will start services in separate terminals.${NC}"
    echo -e "${YELLOW}💡 Tip: Install tmux for a better experience:${NC}"
    echo "   • MacOS: brew install tmux"
    echo "   • Ubuntu/Debian: apt install tmux"
    echo "   • CentOS/RHEL: yum install tmux"

    # 启动后端（在新终端）
    echo -e "${BLUE}Starting backend server...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_ROOT' && ./scripts/start-backend.sh\""
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "cd '$PROJECT_ROOT' && ./scripts/start-backend.sh; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -e "cd '$PROJECT_ROOT' && ./scripts/start-backend.sh" &
        else
            echo -e "${RED}❌ No suitable terminal emulator found.${NC}"
            echo "Please start backend manually in a new terminal:"
            echo "cd '$PROJECT_ROOT' && ./scripts/start-backend.sh"
        fi
    else
        echo -e "${RED}❌ Unsupported OS.${NC}"
        echo "Please start backend manually in a new terminal:"
        echo "cd '$PROJECT_ROOT' && ./scripts/start-backend.sh"
    fi

    # 启动前端（在当前终端）
    echo -e "${BLUE}Starting frontend server...${NC}"
    cd "$PROJECT_ROOT/frontend"
    exec PORT=$FRONTEND_PORT pnpm dev

else
    # 使用 tmux 启动服务
    SESSION="genflow"

    # 如果会话已存在，则附加到会话
    if tmux has-session -t $SESSION 2>/dev/null; then
        echo -e "${YELLOW}⚠️ Session $SESSION already exists. Attaching...${NC}"
        tmux attach-session -t $SESSION
        exit 0
    fi

    # 创建新会话
    echo -e "${BLUE}Creating tmux session...${NC}"
    tmux new-session -d -s $SESSION

    # 创建窗口并启动后端
    tmux rename-window -t $SESSION:0 'backend'
    tmux send-keys -t $SESSION:0 "cd '$PROJECT_ROOT' && ./scripts/start-backend.sh" C-m

    # 创建窗口并启动前端
    tmux new-window -t $SESSION:1 -n 'frontend'
    tmux send-keys -t $SESSION:1 "cd '$PROJECT_ROOT/frontend' && PORT=$FRONTEND_PORT pnpm dev" C-m

    # 额外的日志窗口
    tmux new-window -t $SESSION:2 -n 'logs'
    tmux send-keys -t $SESSION:2 "cd '$PROJECT_ROOT' && " C-m
    tmux send-keys -t $SESSION:2 "echo 'Log monitor - Press Ctrl+C to exit'" C-m
    tmux send-keys -t $SESSION:2 "tail -f backend/logs/*.log 2>/dev/null || echo 'Waiting for log files...'" C-m

    # 返回到第一个窗口
    tmux select-window -t $SESSION:0

    # 附加到会话
    echo -e "${GREEN}✅ Development environment started!${NC}"
    echo -e "${YELLOW}💡 Tmux commands:${NC}"
    echo "   • Switch window: Ctrl+b + window number (0, 1, 2)"
    echo "   • Detach session: Ctrl+b + d"
    echo "   • Scroll: Ctrl+b + [ (use arrow keys to scroll, q to exit)"
    echo "   • Split vertically: Ctrl+b + %"
    echo "   • Split horizontally: Ctrl+b + \""
    tmux attach-session -t $SESSION
fi
