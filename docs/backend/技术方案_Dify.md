# GenFlow Dify 集成方案

## 1. Dify 应用配置

### 1.1 应用创建
- **应用类型:** Assistant
- **基础模型:** GPT-4
- **知识库:** 科技趋势库
- **工具插件:** 内容发布工具集

### 1.2 提示词模板
```yaml
# 文章生成模板
system: |
  你是一位专业的科技文章作者，擅长将复杂的技术概念转化为通俗易懂的内容。
  请基于用户提供的主题，生成一篇结构完整、观点明确的文章。

user: |
  主题：{topic}
  关键词：{keywords}
  字数要求：{word_count}
  目标平台：{platform}

assistant: |
  基于提供的主题和要求，我会生成一篇适合{platform}平台的文章。
  文章将包含以下部分：
  1. 引人入胜的标题
  2. 简明的导语
  3. 核心内容（3-4个主要观点）
  4. 总结和展望

# SEO 优化建议模板
system: |
  你是一位 SEO 优化专家，请为文章提供优化建议。

user: |
  标题：{title}
  内容：{content}
  目标平台：{platform}

assistant: |
  我将从以下几个方面提供优化建议：
  1. 标题优化
  2. 关键词密度
  3. 内容结构
  4. 图文配比
  5. 链接策略
```

## 2. API 集成

### 2.1 客户端封装
```python
# app/dify_client.py
import requests
from typing import Dict, List, Optional

class DifyClient:
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def generate_article(self,
                        topic: str,
                        keywords: List[str],
                        word_count: int,
                        platform: str) -> Dict:
        """生成文章内容"""
        response = requests.post(
            f'{self.endpoint}/completion',
            headers=self.headers,
            json={
                'messages': [{
                    'role': 'user',
                    'content': f'主题：{topic}\n关键词：{",".join(keywords)}\n'
                              f'字数要求：{word_count}\n目标平台：{platform}'
                }],
                'conversation_id': None  # 新对话
            }
        )
        return response.json()

    def get_seo_suggestions(self,
                          title: str,
                          content: str,
                          platform: str) -> Dict:
        """获取 SEO 优化建议"""
        response = requests.post(
            f'{self.endpoint}/completion',
            headers=self.headers,
            json={
                'messages': [{
                    'role': 'user',
                    'content': f'标题：{title}\n内容：{content}\n'
                              f'目标平台：{platform}'
                }],
                'conversation_id': None
            }
        )
        return response.json()

    def publish_to_platform(self,
                          article_data: Dict,
                          platform: str) -> Dict:
        """调用发布工具插件"""
        response = requests.post(
            f'{self.endpoint}/tool/publish',
            headers=self.headers,
            json={
                'platform': platform,
                'article': article_data
            }
        )
        return response.json()
```

### 2.2 服务层集成
```python
# app/services/article_service.py
from app.dify_client import DifyClient
from app.models import Article
from typing import List

class ArticleService:
    def __init__(self):
        self.dify_client = DifyClient(
            api_key=current_app.config['DIFY_API_KEY'],
            endpoint=current_app.config['DIFY_ENDPOINT']
        )

    async def create_article_with_ai(self,
                                   topic: str,
                                   keywords: List[str],
                                   platform: str) -> Article:
        """使用 AI 创建文章"""
        # 生成文章内容
        article_result = await self.dify_client.generate_article(
            topic=topic,
            keywords=keywords,
            word_count=2000,  # 可配置
            platform=platform
        )

        # 获取 SEO 建议
        seo_result = await self.dify_client.get_seo_suggestions(
            title=article_result['title'],
            content=article_result['content'],
            platform=platform
        )

        # 创建文章记录
        article = Article(
            title=article_result['title'],
            content=article_result['content'],
            seo_suggestions=seo_result['suggestions'],
            platform=platform,
            status='draft'
        )

        return article
```

## 3. 知识库管理

### 3.1 知识库更新
```python
# app/tasks/knowledge_tasks.py
from app.dify_client import DifyClient
from app.utils.scraper import TechNewsScraper
from celery import shared_task

@shared_task
def update_knowledge_base():
    """定期更新知识库内容"""
    # 抓取最新科技新闻
    scraper = TechNewsScraper()
    news_data = scraper.fetch_latest_news()

    # 更新到 Dify 知识库
    dify_client = DifyClient()
    for item in news_data:
        dify_client.update_knowledge_base(item)
```

### 3.2 趋势分析
```python
# app/services/trend_service.py
class TrendService:
    def __init__(self):
        self.dify_client = DifyClient()

    async def analyze_trends(self) -> List[Dict]:
        """分析当前科技趋势"""
        result = await self.dify_client.query_knowledge_base(
            prompt="分析最近一周的科技新闻，"
                   "提取出主要的技术趋势和热点话题"
        )
        return result['trends']
```

## 4. 工具插件开发

### 4.1 平台发布插件
```python
# app/dify_plugins/publisher.py
from dify.plugin import Plugin, PluginParameter

class ContentPublisher(Plugin):
    def __init__(self):
        self.parameters = [
            PluginParameter(
                name="platform",
                type="string",
                required=True,
                enum=["baidu", "sohu", "netease"]
            ),
            PluginParameter(
                name="article",
                type="object",
                required=True
            )
        ]

    async def execute(self, params):
        platform = params['platform']
        article = params['article']

        # 根据平台选择对应的发布器
        publisher = self.get_publisher(platform)
        result = await publisher.publish(article)

        return {
            'status': 'success',
            'url': result['url']
        }
```

## 5. 监控与优化

### 5.1 性能监控
```python
# app/utils/metrics.py
from prometheus_client import Counter, Histogram

dify_request_count = Counter(
    'dify_requests_total',
    'Total Dify API requests',
    ['endpoint', 'status']
)

dify_latency = Histogram(
    'dify_request_duration_seconds',
    'Dify API request latency',
    ['endpoint']
)
```

### 5.2 质量评估
```python
# app/services/quality_service.py
class ContentQualityService:
    def __init__(self):
        self.dify_client = DifyClient()

    async def evaluate_article(self, article: Dict) -> Dict:
        """评估文章质量"""
        result = await self.dify_client.evaluate_content({
            'title': article['title'],
            'content': article['content'],
            'metrics': [
                'readability',
                'originality',
                'engagement'
            ]
        })
        return result
```

## 6. 错误处理

### 6.1 重试机制
```python
# app/utils/retry.py
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def dify_api_call(func, *args, **kwargs):
    """带重试机制的 API 调用"""
    return await func(*args, **kwargs)
```

## 7. 安全配置

### 7.1 API 密钥管理
```python
# app/utils/security.py
from cryptography.fernet import Fernet

class APIKeyManager:
    def __init__(self, encryption_key):
        self.fernet = Fernet(encryption_key)

    def encrypt_api_key(self, api_key: str) -> str:
        """加密 API 密钥"""
        return self.fernet.encrypt(api_key.encode()).decode()

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """解密 API 密钥"""
        return self.fernet.decrypt(encrypted_key.encode()).decode()
```

## 8. 部署说明

### 8.1 环境变量
```bash
# .env
DIFY_API_KEY=your_api_key
DIFY_ENDPOINT=https://api.dify.ai/v1
DIFY_KNOWLEDGE_BASE_ID=your_kb_id
ENCRYPTION_KEY=your_encryption_key
```

### 8.2 依赖安装
```bash
pip install dify-client cryptography tenacity prometheus-client
```
