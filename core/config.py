"""配置文件"""
import os
from dotenv import load_dotenv
from typing import Dict, Any

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""

    def __init__(self):
        """初始化配置"""
        # 加载环境变量
        load_dotenv()

        # Firecrawl 配置
        self.FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
        self.RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))

        # 基础配置
        self.LANGUAGE = os.getenv('LANGUAGE', 'zh')
        self.OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')

        # OpenAI 配置
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')

        # 创建输出目录
        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            'firecrawl': {
                'api_key': self.FIRECRAWL_API_KEY,
                'max_retries': self.MAX_RETRIES,
                'retry_delay': self.RETRY_DELAY
            },
            'base': {
                'language': self.LANGUAGE,
                'output_dir': self.OUTPUT_DIR
            },
            'openai': {
                'api_key': self.OPENAI_API_KEY,
                'model': self.OPENAI_MODEL
            }
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """从字典创建配置对象

        Args:
            config_dict: 配置字典

        Returns:
            Config: 配置对象
        """
        config = cls()

        # 更新 Firecrawl 配置
        firecrawl_config = config_dict.get('firecrawl', {})
        config.FIRECRAWL_API_KEY = firecrawl_config.get('api_key', config.FIRECRAWL_API_KEY)
        config.MAX_RETRIES = firecrawl_config.get('max_retries', config.MAX_RETRIES)
        config.RETRY_DELAY = firecrawl_config.get('retry_delay', config.RETRY_DELAY)

        # 更新基础配置
        base_config = config_dict.get('base', {})
        config.LANGUAGE = base_config.get('language', config.LANGUAGE)
        config.OUTPUT_DIR = base_config.get('output_dir', config.OUTPUT_DIR)

        # 更新 OpenAI 配置
        openai_config = config_dict.get('openai', {})
        config.OPENAI_API_KEY = openai_config.get('api_key', config.OPENAI_API_KEY)
        config.OPENAI_MODEL = openai_config.get('model', config.OPENAI_MODEL)

        return config

    # SERP API配置
    SERP_API_KEY = os.getenv('SERP_API_KEY')

    # 百度API配置
    BAIDU_API_KEY = os.getenv('BAIDU_API_KEY')
    BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY')

    # 微博API配置
    WEIBO_APP_KEY = os.getenv('WEIBO_APP_KEY')
    WEIBO_APP_SECRET = os.getenv('WEIBO_APP_SECRET')

    # 文本检测配置
    PLAGIARISM_API_KEY = os.getenv('PLAGIARISM_API_KEY')
    AI_DETECTION_API_KEY = os.getenv('AI_DETECTION_API_KEY')

    # 文章保存路径
    ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'articles')

    # 风格模板
    STYLE_TEMPLATES = {
        "新闻报道": {
            "tone": "客观中立",
            "structure": "倒金字塔",
            "length": "800-1200字"
        },
        "科技评测": {
            "tone": "专业理性",
            "structure": "问题-分析-结论",
            "length": "1500-2500字"
        },
        "观点评论": {
            "tone": "犀利深刻",
            "structure": "论点-论据-结论",
            "length": "1000-1500字"
        }
    }
