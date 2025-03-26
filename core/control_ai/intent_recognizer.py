"""
意图识别器 - 从用户自然语言输入中识别意图和实体

该模块负责分析用户输入，识别用户意图并提取关键实体，为后续任务规划提供基础。
使用OpenAI API进行语义理解，支持多种用户意图类型。
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional

from openai import OpenAI

# 配置日志
logger = logging.getLogger(__name__)

class IntentRecognizer:
    """意图识别器

    从用户自然语言输入中识别意图和提取实体，分析用户需求意图。
    """

    # 支持的意图类型
    INTENT_TYPES = [
        "trending_query",     # 热门话题查询
        "research_request",   # 研究请求
        "writing_request",    # 写作请求
        "style_request",      # 风格调整
        "review_request",     # 审核请求
        "content_production", # 完整内容生产
        "information_query",  # 信息查询
        "status_query",       # 状态查询
        "feedback",           # 用户反馈
        "help_request",       # 帮助请求
        "cancel_request",     # 取消请求
        "unknown"             # 未知意图
    ]

    def __init__(self, system_prompt: Optional[str] = None):
        """初始化意图识别器

        Args:
            system_prompt: 可选的系统提示，用于引导LLM更好地识别意图
        """
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # 设置系统提示
        self.system_prompt = system_prompt or self._get_default_system_prompt()

    def recognize(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """识别用户输入的意图和实体

        Args:
            user_input: 用户的自然语言输入
            context: 可选的上下文信息，如用户历史交互

        Returns:
            Dict[str, Any]: 包含意图类型、置信度和提取实体的结果
        """
        try:
            # 构建上下文提示
            context_prompt = ""
            if context:
                context_prompt = "上下文信息:\n"
                if "history" in context:
                    # 添加最近的历史交互记录
                    history = context["history"][-5:] if len(context["history"]) > 5 else context["history"]
                    for item in history:
                        if "user" in item:
                            context_prompt += f"用户: {item['user']}\n"
                        if "assistant" in item:
                            context_prompt += f"助手: {item['assistant']}\n"

                # 添加其他上下文信息
                if "current_topic" in context:
                    context_prompt += f"当前话题: {context['current_topic']}\n"
                if "current_stage" in context:
                    context_prompt += f"当前阶段: {context['current_stage']}\n"

            # 构建完整提示
            full_prompt = f"{context_prompt}\n用户输入: {user_input}\n\n请识别上述用户输入的意图和相关实体。"

            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": full_prompt}
            ]

            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",  # 或其他适合的模型
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            # 解析响应
            content = response.choices[0].message.content
            result = json.loads(content)

            # 验证结果格式
            self._validate_result(result)

            # 记录识别结果
            logger.info(f"识别意图: {result.get('intent_type')} (置信度: {result.get('confidence')})")
            logger.debug(f"识别实体: {result.get('entities')}")

            return result

        except Exception as e:
            logger.error(f"意图识别失败: {str(e)}")

            # 返回未知意图
            return {
                "intent_type": "unknown",
                "confidence": 0.0,
                "entities": {},
                "error": str(e)
            }

    def _validate_result(self, result: Dict[str, Any]) -> None:
        """验证意图识别结果的格式

        Args:
            result: API返回的识别结果

        Raises:
            ValueError: 当结果格式不符合要求时
        """
        # 检查必要字段
        required_fields = ["intent_type", "confidence", "entities"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"识别结果缺少必要字段: {field}")

        # 验证意图类型
        if result["intent_type"] not in self.INTENT_TYPES:
            logger.warning(f"未知意图类型: {result['intent_type']}，将其归类为'unknown'")
            result["intent_type"] = "unknown"

        # 验证置信度
        if not isinstance(result["confidence"], (int, float)) or not (0 <= result["confidence"] <= 1):
            logger.warning(f"无效置信度值: {result['confidence']}，设置为默认值0.5")
            result["confidence"] = 0.5

        # 验证实体是否为字典
        if not isinstance(result["entities"], dict):
            logger.warning("实体应为字典格式，重置为空字典")
            result["entities"] = {}

    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示

        Returns:
            str: 默认系统提示
        """
        return """你是一个专业的意图识别系统，负责从用户自然语言输入中识别出用户意图和关键实体。

你的任务是理解用户请求，并将其分类为以下意图类型之一:
- trending_query: 用户想了解当前热门话题
- research_request: 用户请求对特定主题进行研究
- writing_request: 用户请求创作某个主题的内容
- style_request: 用户请求调整已有内容的风格
- review_request: 用户请求审核内容
- content_production: 用户请求完整的内容生产流程
- information_query: 用户询问系统或功能相关信息
- status_query: 用户询问当前任务状态
- feedback: 用户提供反馈意见
- help_request: 用户请求帮助
- cancel_request: 用户请求取消当前任务
- unknown: 无法确定用户意图

对于每个意图，提取相关实体:
- 对于content_production，提取topic(主题)、category(分类)、style(风格)、keywords(关键词)等
- 对于writing_request，提取topic(主题)、style(风格)等
- 对于research_request，提取topic(主题)、focus_areas(关注点)等

以JSON格式返回结果，包含:
1. intent_type: 意图类型
2. confidence: 置信度(0-1之间的数值)
3. entities: 提取的实体和属性
4. explanation: 简短解释为何识别为该意图

示例：
{
  "intent_type": "content_production",
  "confidence": 0.92,
  "entities": {
    "topic": "2023年AI发展趋势",
    "category": "科技",
    "style": "分析性",
    "keywords": ["人工智能", "大模型", "发展趋势"]
  },
  "explanation": "用户明确要求创建关于AI发展趋势的内容，并指定了类别和风格。"
}"""
