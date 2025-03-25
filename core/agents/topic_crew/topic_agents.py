"""选题团队智能体"""
from typing import List, Dict
from crewai import Agent
from core.tools.search_tools import SearchAggregator
from core.tools.content_collectors import ContentCollector
from core.tools.nlp_tools import NLPAggregator
from core.tools.trending_tools import TrendingTopics
from core.config import Config

class TopicAgents:
    """选题团队智能体定义"""

    def __init__(self):
        """初始化工具"""
        # 加载配置
        config = Config()

        # 初始化工具
        self.search_tools = SearchAggregator()
        self.content_collector = ContentCollector()
        self.nlp_tools = NLPAggregator()

        # 初始化趋势工具，传入配置
        trending_config = {
            'baidu': {
                'api_key': config.BAIDU_API_KEY,
                'secret_key': config.BAIDU_SECRET_KEY
            },
            'weibo': {
                'api_key': config.WEIBO_APP_KEY
            }
        }
        self.trending_tools = TrendingTopics.get_instance(trending_config)

    def create_trend_analyzer(self) -> Agent:
        """创建趋势分析师"""
        return Agent(
            role='趋势分析师',
            goal='发现和分析当前热门话题趋势',
            backstory="""你是一位资深的趋势分析师，擅长发现热门话题和预测话题走势。
            你需要从各个平台收集数据，分析话题热度和发展趋势。""",
            tools=[
                self.trending_tools.execute,
                self.search_tools.execute,
                self.content_collector.execute
            ]
        )

    def create_topic_researcher(self) -> Agent:
        """创建话题研究员"""
        return Agent(
            role='话题研究员',
            goal='深入研究话题的价值和可行性',
            backstory="""你是一位专业的话题研究员，擅长评估话题的商业价值和内容可行性。
            你需要分析话题的受众群体、竞争情况和发展空间。""",
            tools=[
                self.search_tools.execute,
                self.nlp_tools.execute,
                self.trending_tools.execute
            ]
        )

    def create_report_writer(self) -> Agent:
        """创建报告撰写员"""
        return Agent(
            role='报告撰写员',
            goal='生成专业的选题分析报告',
            backstory="""你是一位专业的报告撰写员，擅长将数据和分析转化为清晰的报告。
            你需要整理各类信息，生成结构化的选题报告。""",
            tools=[self.nlp_tools.execute]
        )
