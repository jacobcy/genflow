#!/bin/bash

# 脚本说明: 更新所有子模块到最新版本并提交更改
# 用法: ./scripts/update-submodules.sh [--force]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT"

echo -e "${BLUE}正在更新子模块到最新版本...${NC}"
echo

# 获取当前子模块状态
echo -e "${BLUE}当前子模块状态:${NC}"
git submodule status
echo

# 确保所有子模块都在正确的分支上
echo -e "${BLUE}确保所有子模块都在正确的分支上...${NC}"
git submodule foreach 'git checkout main 2>/dev/null || git checkout master 2>/dev/null || echo "警告: 无法检出主分支"'
echo

# 更新所有子模块
echo -e "${BLUE}拉取所有子模块的最新更改...${NC}"
git submodule foreach 'git pull origin $(git rev-parse --abbrev-ref HEAD) 2>/dev/null || echo "跳过未跟踪分支"'
echo

# 获取更新后的子模块状态
echo -e "${BLUE}更新后的子模块状态:${NC}"
submodule_status=$(git submodule status)
echo "$submodule_status"
echo

# 更新 .gitmodules-config 文件
echo -e "${BLUE}更新 .gitmodules-config 文件...${NC}"
if [ -f "$PROJECT_ROOT/.gitmodules-config" ]; then
    # 直接将当前状态格式化为所需格式
    formatted_status=""
    while read -r line; do
        if [[ -n "$line" ]]; then
            sha=$(echo "$line" | awk '{print $1}')
            path=$(echo "$line" | awk '{print $2}')
            branch=$(echo "$line" | grep -o '(heads/[^)]*)' | sed 's/(heads\///' | sed 's/)//')
            formatted_status="${formatted_status}${path}      - ${sha} (${branch})\n"
        fi
    done <<< "$(git submodule status)"

    # 检测操作系统
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed_cmd="sed -i ''"
    else
        # Linux
        sed_cmd="sed -i"
    fi

    # 创建临时文件
    temp_file=$(mktemp)

    # 提取子模块状态部分前面的内容
    awk 'BEGIN{found=0} /^## 子模块路径和状态$/{found=1; exit} {print}' "$PROJECT_ROOT/.gitmodules-config" > "$temp_file"

    # 添加子模块状态部分
    echo -e "## 子模块路径和状态\n\n\`\`\`" >> "$temp_file"
    echo -e "$formatted_status" >> "$temp_file"
    echo -e "\`\`\`\n" >> "$temp_file"

    # 提取子模块状态部分后面的内容
    awk 'BEGIN{found=0} /^## 子模块路径和状态$/{found=1} /^```$/ && found==1 {found=2; next} found==2 {print}' "$PROJECT_ROOT/.gitmodules-config" >> "$temp_file"

    # 替换原文件
    cp "$temp_file" "$PROJECT_ROOT/.gitmodules-config"
    rm "$temp_file"

    echo -e "${GREEN}✓ .gitmodules-config 文件已更新${NC}"
else
    echo -e "${YELLOW}警告: .gitmodules-config 文件不存在${NC}"
fi

# 提交更改
echo -e "${BLUE}提交子模块更改...${NC}"
git add integrations/
if [ -f "$PROJECT_ROOT/.gitmodules-config" ]; then
    git add "$PROJECT_ROOT/.gitmodules-config"
fi

# 检查是否有更改需要提交
if git diff --staged --quiet; then
    echo -e "${YELLOW}没有检测到子模块更改，不需要提交${NC}"
else
    if [ "$1" == "--force" ] || [ "$1" == "-f" ]; then
        # 强制提交
        PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "chore: 更新所有子模块到最新版本"
        echo -e "${GREEN}✓ 子模块更改已提交${NC}"
    else
        # 显示差异并询问用户
        echo -e "${YELLOW}以下是将要提交的更改:${NC}"
        git diff --staged

        read -p "是否提交这些更改? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "chore: 更新所有子模块到最新版本"
            echo -e "${GREEN}✓ 子模块更改已提交${NC}"
        else
            echo -e "${YELLOW}取消提交${NC}"
            git reset HEAD integrations/ "$PROJECT_ROOT/.gitmodules-config" 2>/dev/null || true
        fi
    fi
fi

echo -e "${GREEN}✓ 子模块更新完成${NC}"
