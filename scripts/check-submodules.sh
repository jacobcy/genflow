#!/bin/bash

# 脚本说明: 检查子模块状态并在必要时恢复到原始状态
# 用法: ./scripts/check-submodules.sh [--fix]

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

echo -e "${BLUE}正在检查子模块状态...${NC}"
echo

# 检查每个子模块
submodules_changed=false
submodule_paths=$(git config --file .gitmodules --get-regexp path | awk '{ print $2 }')

for submodule in $submodule_paths; do
    echo -e "${BLUE}检查子模块: ${YELLOW}$submodule${NC}"
    
    # 检查子模块是否有未提交的更改
    if [ -d "$submodule" ]; then
        cd "$submodule"
        
        if [[ -n $(git status -s) ]]; then
            echo -e "${RED}警告: 子模块 $submodule 有未提交的更改${NC}"
            git status -s
            submodules_changed=true
            
            # 如果提供了 --fix 参数，则恢复子模块状态
            if [[ "$1" == "--fix" ]]; then
                echo -e "${YELLOW}正在恢复子模块 $submodule 到原始状态...${NC}"
                git reset --hard
                git clean -fd
                echo -e "${GREEN}子模块 $submodule 已恢复到原始状态${NC}"
            fi
        else
            echo -e "${GREEN}子模块 $submodule 状态正常${NC}"
        fi
        
        cd "$PROJECT_ROOT"
    else
        echo -e "${RED}错误: 子模块目录 $submodule 不存在${NC}"
    fi
    echo
done

# 总结
if $submodules_changed; then
    if [[ "$1" == "--fix" ]]; then
        echo -e "${GREEN}所有子模块已恢复到原始状态${NC}"
        echo -e "${YELLOW}请记得提交这些更改:${NC}"
        echo "git add $submodule_paths"
        echo "git commit -m \"chore: 恢复子模块到原始状态\""
    else
        echo -e "${YELLOW}检测到子模块有未提交的更改${NC}"
        echo -e "${YELLOW}使用以下命令恢复子模块:${NC}"
        echo "$0 --fix"
    fi
else
    echo -e "${GREEN}所有子模块状态正常${NC}"
fi 