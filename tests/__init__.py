"""
GenFlow 测试包

本包包含GenFlow项目的测试代码。
测试用例主要针对以下几个方面：
1. 工具功能测试
2. 代理通信测试 
3. 主题工具测试
4. 集成测试

框架使用 pytest 作为测试框架。
"""

import os
import sys

# 确保将GenFlow项目根目录添加到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root) 