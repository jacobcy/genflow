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
    # 创建临时文件
    tmp_file=$(mktemp)
    
    # 更新子模块状态部分
    awk -v status="$submodule_status" '
    BEGIN { updating=0; updated=0 }
    /^## 子模块路径和状态$/ { updating=1; print; print ""; print "```"; next }
    /^```$/ && updating==1 {
        updating=0;
        updated=1;
        # 添加子模块状态
        split(status, lines, "\n")
        for (i in lines) {
            if (lines[i] != "") {
                # 提取 SHA 和路径
                match(lines[i], /([^ ]+) ([^ ]+) \(([^)]+)\)/)
                sha = substr(lines[i], RSTART, RLENGTH)
                path = substr(lines[i], RSTART+length(substr(lines[i], RSTART, RLENGTH))+1)
                branch = substr(lines[i], RSTART+length(substr(lines[i], RSTART, RLENGTH))-1, 1)
                
                # 格式化输出
                match(lines[i], /[^ ]+ ([^ ]+)/)
                path = substr(lines[i], RSTART+1, RLENGTH-1)
                match(lines[i], /^[ ]*([^ ]+)/)
                sha = substr(lines[i], RSTART, RLENGTH)
                match(lines[i], /\(([^)]+)\)/)
                branch = ""
                if (RLENGTH > 0) {
                    branch = substr(lines[i], RSTART+1, RLENGTH-2)
                }
                
                printf "%-24s - %s (%s)\n", path, sha, branch
            }
        }
        print "```";
        print "";
        next
    }
    { if (updating == 0) print }
    END { if (updated == 0) print "错误: 无法更新子模块状态部分" }
    ' "$PROJECT_ROOT/.gitmodules-config" > "$tmp_file"
    
    # 检查是否成功生成内容
    if [ -s "$tmp_file" ]; then
        mv "$tmp_file" "$PROJECT_ROOT/.gitmodules-config"
        echo -e "${GREEN}✓ .gitmodules-config 文件已更新${NC}"
    else
        echo -e "${RED}✗ 无法更新 .gitmodules-config 文件${NC}"
        rm "$tmp_file"
    fi
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