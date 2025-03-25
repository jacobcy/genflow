# GenFlow 热点话题模块

## 功能概述

基于 daily-hot-api (http://localhost:6688) 服务，实现热点数据的分类、缓存和查询功能。该模块支持平台配置和数据的 Redis 缓存、关键词搜索、分类过滤等功能。

## 数据来源

### API 基础信息
- 服务地址: http://localhost:6688

### API 端点说明
- /all
  - 功能：获取所有支持的数据源接口信息
  - 返回：包含可用平台列表及其对应的API路径
  - 返回格式：
    ```json
    {
        "code": 200,
        "count": 54,
        "routes": [
            {
                "name": "36kr",
                "path": "/36kr"
            },
            {
                "name": "zhihu",
                "path": "/zhihu"
            },
            {
                "name": "weibo",
                "path": "/weibo"
            }
            // ... 更多平台
        ]
    }
    ```

- /{platform}
  - 功能：获取特定平台的热点数据
  - 参数：platform - 平台标识符（如 weibo, zhihu, 36kr 等）
  - 返回：该平台的热点话题列表
  - 支持的平台：
    - 社交媒体：weibo, douyin, kuaishou
    - 技术社区：github, v2ex, juejin, csdn
    - 新闻资讯：36kr, sina-news, qq-news, netease-news, baidu
    - 问答平台：zhihu, zhihu-daily
    - 游戏社区：genshin, miyoushe, ngabbs
    - 其他平台：bilibili, douban-movie, sspai 等
  - 返回格式：
    ```json
    {
        "code": 200,
        "name": "baidu",
        "title": "百度",
        "type": "热搜",
        "params": {
            "type": {
                "name": "热搜类别",
                "type": {
                    "realtime": "热搜",
                    "novel": "小说",
                    "movie": "电影",
                    "teleplay": "电视剧",
                    "car": "汽车",
                    "game": "游戏"
                }
            }
        },
        "link": "https://top.baidu.com/board",
        "total": 50,
        "fromCache": false,
        "updateTime": "2025-03-25T10:09:20.290Z",
        "data": [
            {
                "id": 0,
                "title": "热搜标题",
                "desc": "详细描述",
                "hot": 7904941,
                "url": "PC端链接",
                "mobileUrl": "移动端链接",
                "cover": "封面图片URL",
                "author": "作者信息",
                "timestamp": 0
            }
        ]
    }
    ```

## 配置管理

### 环境变量
```python
# 必需配置
DAILY_HOT_API_URL: str  # API服务地址，默认 "http://localhost:6688"

# Redis配置（必需）
REDIS_HOST: str      # Redis主机地址，默认 "localhost"
REDIS_PORT: str      # Redis端口，默认 "6379"
REDIS_DB: str        # Redis数据库编号，默认 "0"
REDIS_PASSWORD: str  # Redis密码（可选）
REDIS_CACHE_TTL: int # Redis数据缓存过期时间（秒），默认 10800（3小时）
REDIS_CONFIG_TTL: int # Redis平台配置过期时间（秒），默认 604800（7天）

# 可选配置
PLATFORM_CONFIG_PATH: str  # 平台配置文件路径，默认 "<project_root>/data/platform_config.json"
CONFIG_UPDATE_INTERVAL: int  # 配置更新间隔(秒)，默认 7天
```

## 数据分类方案

### 平台分类管理
- 平台与分类的映射关系定义在 `platform_categories.py` 文件中
- 每个平台可以属于多个分类标签
- 分类标签分为以下几类：
  - 平台属性：社交、技术、新闻、知识、游戏等
  - 内容属性：热点、时事、娱乐、开发、编程等
  - 内容形式：短视频、讨论、综合、深度等
  - 其他属性：学习等

### 分类查询策略
- 不在数据存储时添加分类信息
- 在查询时根据平台映射关系返回相关数据
- 支持多分类标签的模糊匹配
- 一个平台可以属于多个分类

### 分类查询示例
```python
from .platform_categories import get_platforms_by_category, get_platform_categories

# 获取技术相关的所有平台
tech_platforms = get_platforms_by_category("技术")  # ["github", "v2ex", "juejin", "csdn"]

# 获取某个平台的所有分类
weibo_categories = get_platform_categories("weibo")  # ["社交", "热点", "时事"]
```

## 热度计算机制

### 1. 平台权重系统
- 配置文件：`platform_weights.py`
- 权重范围：0.5-1.0
- 权重分配原则：
  - 微博、百度等大平台权重为1.0（基准权重）
  - 主流新闻媒体权重为0.9
  - 技术社区权重为0.6-0.7
  - 垂直领域平台权重为0.5
- 未配置平台默认权重：0.5

### 2. 默认热度值
- 配置文件：`platform_weights.py`
- 基准值设置：
  - 社交媒体：8000-10000
  - 新闻媒体：8000-10000
  - 问答平台：3000-5000
  - 技术社区：200-500
  - 游戏社区：1000
- 未配置平台默认值：1000

### 3. 热度计算规则
```python
def calculate_normalized_hot_score(platform: str, raw_score: int = None) -> int:
    """计算标准化的热度值

    计算规则：
    1. 如果提供了原始热度值，使用原始值，否则使用默认值
    2. 将热度值乘以平台权重得到最终热度
    3. 确保返回的热度值为正整数
    """
```

### 4. 使用示例
```python
from .platform_weights import calculate_normalized_hot_score

# 计算微博话题的标准化热度
weibo_score = calculate_normalized_hot_score(
    platform="weibo",
    raw_score=10000  # 原始热度
)  # 结果：10000 * 1.0 = 10000

# 计算技术社区话题的标准化热度
github_score = calculate_normalized_hot_score(
    platform="github",
    raw_score=1000  # 原始热度
)  # 结果：1000 * 0.7 = 700

# 处理没有热度值的情况
zhihu_score = calculate_normalized_hot_score(
    platform="zhihu",
    raw_score=None  # 无热度值
)  # 结果：5000(默认值) * 0.8 = 4000
```

## 核心功能

### 1. 工具初始化
```python
class TrendingTopics(BaseTool):
    name = "trending_topics"
    description = "获取和搜索各大平台热点话题"
```

### 2. 主要方法

#### 2.1 执行工具
```python
from typing import Optional, List, Dict

async def execute(
    category: Optional[str] = "热点",  # 可选，默认获取热点分类
    keywords: Optional[str] = None,    # 可选，搜索关键词
    limit: Optional[int] = 20         # 可选，默认20，上限50
) -> ToolResult:
    """获取热点话题数据

    参数说明：
    - category: 话题分类，默认为"热点"
    - keywords: 搜索关键词，将在标题中进行匹配
    - limit: 返回结果数量，默认20条，最大50条

    返回策略：
    1. 如果结果数据的token数量不超过600，返回完整数据：
    {
        "topics": [
            {
                "title": "话题标题",
                "platform": "平台名称",
                "priority_score": 15000  # 综合优先级分数（已考虑热度和时效性）
            }
        ],
        "total": 20
    }

    2. 如果结果数据的token数量超过600，返回压缩后的摘要：
    {
        "summary": "主要热点趋势概述",  # 使用TextRank算法生成的热点摘要
        "total": 20,
        "top_platforms": ["weibo", "zhihu"]  # 主要来源平台
    }
    """
```

#### 2.2 话题搜索
```python
def _search_topics(
    topics: List[Dict],  # 话题列表
    keywords: str        # 搜索关键词
) -> List[Dict]:
    """在标题和描述中搜索关键词"""
```

#### 2.3 分类查询
```python
def _get_category_platforms(category: str) -> List[str]:
    """获取分类对应的平台列表

    1. 在平台分类映射中查找匹配的平台
    2. 支持模糊匹配（如"技术"可匹配"技术社区"）
    3. 返回符合条件的平台列表
    """

async def get_topics_by_category(
    category: str,
    limit: Optional[int] = None
) -> List[Dict]:
    """获取指定分类的话题列表

    1. 获取分类对应的平台列表
    2. 从这些平台获取话题数据
    3. 按热度排序并限制返回数量
    """
```

## 数据结构

### 1. 话题数据结构
```python
Topic = {
    "title": str,         # 标题（必需）
    "url": str,           # PC端链接
    "mobile_url": str,    # 移动端链接
    "platform": str,      # 来源平台
    "hot_score": int,     # 标准化后的热度值
    "raw_hot": int,       # 原始热度值（可选）
    "description": str,   # 描述（可选）
    "cover": str,         # 封面图片URL（可选）
}
```

### 2. 返回结果结构
```python
Result = {
    "topics": List[Topic],  # 话题列表
    "platforms": {          # 当前结果包含的平台信息
        "platform_name": {
            "name": str,         # 平台显示名称
            "type": str,         # 平台类型
            "total": int,        # 话题总数
            "update_time": str   # 更新时间
        }
    },
    "total": int           # 话题总数
}
```

### 3. 话题数据存储
- 唯一标识：使用话题标题（title）作为唯一标识
- 存储策略：
  1. 首次存储：直接保存数据
  2. 遇到相同标题：
     - 如果新数据来自权重更高的平台：替换现有数据
     - 如果新数据来自权重更低的平台：丢弃新数据
     - 如果平台权重相同：保留最新数据
- 过期时间：7天（604800秒）
- 数据结构：
```python
TopicData = {
    "title": str,           # 标题（作为唯一标识）
    "platform": str,        # 来源平台
    "url": str,            # PC端链接
    "mobile_url": str,     # 移动端链接
    "hot_score": int,      # 标准化后的热度值
    "raw_hot": int,        # 原始热度值（可选）
    "description": str,    # 描述（可选）
    "cover": str,          # 封面图片URL（可选）
    "source_time": int,    # 数据源原始时间戳（如果有）
    "fetch_time": int,     # 数据抓取时间戳（必需）
    "expire_time": int     # 数据过期时间戳（必需）
}
```

### 4. Redis 键格式
- 平台配置：`genflow:trending:platforms:config`
- 话题数据：`genflow:trending:topic:{title_hash}`  # 使用标题的哈希值作为键
- 平台索引：`genflow:trending:platform:{platform}:topics`  # 存储平台下最近3小时内抓取的话题标题哈希列表
- 索引时间：`genflow:trending:platform:{platform}:index_time`  # 记录平台索引的最后更新时间

### 5. 数据操作流程

#### 5.1 话题数据管理
```python
async def save_topic(topic_data: Dict) -> str:
    """保存话题数据

    1. 使用标题生成唯一哈希值
    2. 检查是否已存在相同标题的数据：
       - 如果不存在：创建新记录
       - 如果存在：
         * 获取现有数据的平台权重
         * 获取新数据的平台权重
         * 如果新平台权重更高：替换现有数据
         * 如果新平台权重更低：丢弃新数据
         * 如果权重相同：保留最新数据
    3. 设置时间字段：
       - 保留原始source_time（如果有）
       - 更新fetch_time
       - 更新expire_time（fetch_time + 7天）
    4. 返回话题哈希值
    """

async def update_platform_data(platform: str, topics: List[Dict]):
    """批量更新平台数据（每3小时调用一次）

    1. 获取当前平台的权重
    2. 检查索引更新时间
    3. 如果距离上次更新超过3小时：
       - 清空旧索引
       - 对每个话题：
         * 检查是否存在相同标题
         * 根据平台权重决定是否更新数据
         * 如果更新成功，将话题哈希添加到平台索引
       - 更新索引时间戳
    4. 如果未到更新时间：
       - 直接返回当前索引数据
    """

def should_update_topic(existing_platform: str, new_platform: str) -> bool:
    """判断是否应该更新话题数据

    1. 获取现有数据的平台权重
    2. 获取新数据的平台权重
    3. 返回是否应该用新数据替换现有数据

    判断规则：
    - 新平台权重更高：返回 True
    - 新平台权重更低：返回 False
    - 权重相同：返回 True（保留最新）
    """
```

## 数据缓存策略

### 1. Redis 键格式
- 平台配置：`genflow:trending:platforms:config`
- 话题数据：`genflow:trending:topic:{title_hash}`
- 平台索引：`genflow:trending:platform:{platform}:topics`  # 存储平台下最近3小时内抓取的话题标题哈希列表
- 索引时间：`genflow:trending:platform:{platform}:index_time`  # 记录平台索引的最后更新时间

### 2. 平台配置缓存
- 缓存内容：平台配置信息的 JSON 字符串
- 过期时间：7天（604800秒）
- 配置结构：
```python
PlatformConfig = {
    "update_time": int,      # 最后更新时间戳
    "platforms": {           # 平台配置信息
        "platform_name": {
            "path": str,        # API路径
            "category": str     # 平台分类
        }
    }
}
```
- 更新策略：
  - 获取配置时先检查 Redis 缓存
  - 如果缓存不存在或已过期（超过7天），从 `/all` 接口获取最新配置
  - 更新配置后刷新缓存和过期时间

### 4. 平台索引管理
- 索引更新周期：3小时
- 索引内容：平台最近一次抓取的所有话题标题哈希列表
- 更新策略：
  - 每次从API获取新数据时更新索引（3小时间隔）
  - 不在单条数据保存时更新索引
  - 索引更新时，清空旧索引并写入新索引
- 索引结构：
```python
PlatformIndex = {
    "topic_hashes": List[str],  # 话题哈希列表
    "update_time": int,      # 索引更新时间
    "next_update": int       # 下次更新时间（3小时后）
}
```

## 实现特性

1. 重复数据处理
   - 使用标题作为唯一标识
   - 基于平台权重的数据更新策略
   - 高权重平台数据优先
   - 相同权重保留最新
   - 低权重数据自动丢弃

2. Redis 数据管理
   - 基于标题哈希的数据存储
   - 智能数据更新机制
   - 平台索引定期更新（3小时）
   - 自动清理过期数据
   - 支持时间范围查询

3. 平台配置缓存
   - 本地缓存平台配置文件
   - 支持配置定期更新（默认7天）
   - 配置更新失败时使用本地备份

4. 数据处理优化
   - 标准化热度值处理（支持万、亿单位转换）
   - 数据类型安全检查和转换
   - 异常处理和日志记录

5. 搜索功能增强
   - 同时搜索标题和描述
   - 支持分类数据补充
   - 结果按热度排序

6. 返回结果优化
   - 包含平台元数据（名称、类型、更新时间等）
   - 提供分类信息
   - 支持结果数量限制
   - 区分PC端和移动端链接
   - 包含封面图片

7. 热度值标准化
   - 平台权重系统
   - 默认热度值配置
   - 智能热度计算
   - 多平台数据对比支持
   - 热度值有效性保证

## 使用示例

### CrewAI 工具调用
```python
from .tools import TrendingTopics

# 初始化工具
tool = TrendingTopics()

# 调用方法
async def execute(
    category: Optional[str] = "热点",  # 可选，默认获取热点分类
    keywords: Optional[str] = None,    # 可选，搜索关键词
    limit: Optional[int] = 20         # 可选，默认20，上限50
) -> ToolResult:
    """获取热点话题数据

    参数说明：
    - category: 话题分类，默认为"热点"
    - keywords: 搜索关键词，将在标题中进行匹配
    - limit: 返回结果数量，默认20条，最大50条

    返回策略：
    1. 如果结果数据的token数量不超过600，返回完整数据：
    {
        "topics": [
            {
                "title": "话题标题",
                "platform": "平台名称",
                "priority_score": 15000  # 综合优先级分数（已考虑热度和时效性）
            }
        ],
        "total": 20
    }

    2. 如果结果数据的token数量超过600，返回压缩后的摘要：
    {
        "summary": "主要热点趋势概述",  # 使用TextRank算法生成的热点摘要
        "total": 20,
        "top_platforms": ["weibo", "zhihu"]  # 主要来源平台
    }
    """
```

### 使用示例

```python
# 1. 获取默认热点数据（所有高权重平台的热点内容）
result = await tool.execute()  # 自动判断是返回完整数据还是压缩摘要

# 2. 获取技术分类的热点
result = await tool.execute(
    category="技术",
    limit=30
)

# 3. 搜索包含关键词的热点
result = await tool.execute(
    keywords="AI",
    limit=50
)

# 4. 获取特定分类下包含关键词的热点
result = await tool.execute(
    category="游戏",
    keywords="原神",
    limit=20
)
```
