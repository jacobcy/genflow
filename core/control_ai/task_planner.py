"""
任务规划器 - 根据用户意图规划执行任务

该模块负责将用户意图转化为具体的任务执行计划，确定调用哪些专业团队，
以及如何组织多步骤任务流程。
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple

from openai import OpenAI

# 配置日志
logger = logging.getLogger(__name__)

class TaskPlanner:
    """任务规划器

    根据识别出的用户意图，规划具体的执行任务步骤。
    """

    # 支持的任务类型
    TASK_TYPES = {
        "trending_query": "获取热门话题",
        "research_request": "研究特定主题",
        "writing_request": "创作内容",
        "style_request": "调整内容风格",
        "review_request": "审核内容",
        "content_production": "完整内容生产流程",
        "information_query": "信息查询",
        "status_query": "任务状态查询",
        "help_request": "提供帮助信息",
        "cancel_request": "取消任务"
    }

    # 每种任务类型支持的行动步骤
    TASK_ACTIONS = {
        "trending_query": ["get_trending_topics"],
        "research_request": ["research_topic"],
        "writing_request": ["create_content"],
        "style_request": ["adjust_style"],
        "review_request": ["review_content"],
        "content_production": ["get_trending_topics", "select_topic", "research_topic",
                             "create_content", "adjust_style", "review_content"],
        "information_query": ["provide_information"],
        "status_query": ["check_status"],
        "help_request": ["provide_help"],
        "cancel_request": ["cancel_task"]
    }

    def __init__(self, system_prompt: Optional[str] = None):
        """初始化任务规划器

        Args:
            system_prompt: 可选的系统提示，用于引导LLM更好地规划任务
        """
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # 设置系统提示
        self.system_prompt = system_prompt or self._get_default_system_prompt()

    def plan(self, intent_result: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """根据意图规划任务

        Args:
            intent_result: 意图识别的结果
            context: 可选的上下文信息，如用户历史请求或当前状态

        Returns:
            Dict[str, Any]: 任务规划结果，包含任务类型、步骤和参数
        """
        try:
            # 提取意图类型和实体
            intent_type = intent_result.get("intent_type")
            entities = intent_result.get("entities", {})

            # 处理未知意图
            if intent_type == "unknown" or intent_type not in self.TASK_TYPES:
                logger.warning(f"无法为未知意图规划任务: {intent_type}")
                return self._create_default_plan("information_query", "无法理解请求")

            # 使用简单规则为某些意图直接创建计划
            if intent_type in ["status_query", "help_request", "cancel_request"]:
                return self._create_simple_plan(intent_type, entities)

            # 对于复杂任务，使用LLM来规划
            return self._plan_complex_task(intent_type, entities, context)

        except Exception as e:
            logger.error(f"任务规划失败: {str(e)}")

            # 返回错误信息计划
            return {
                "task_type": "information_query",
                "steps": [
                    {
                        "action": "provide_information",
                        "parameters": {
                            "message": f"任务规划失败: {str(e)}"
                        }
                    }
                ],
                "error": str(e)
            }

    def _create_simple_plan(self, intent_type: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """为简单意图创建任务计划

        Args:
            intent_type: 意图类型
            entities: 提取的实体

        Returns:
            Dict[str, Any]: 简单任务计划
        """
        # 获取该意图类型对应的行动列表
        actions = self.TASK_ACTIONS.get(intent_type, [])
        if not actions:
            return self._create_default_plan("information_query", "不支持的请求类型")

        # 创建步骤
        steps = []
        for action in actions:
            # 根据不同行动类型设置不同参数
            parameters = {}

            if action == "check_status":
                parameters = {"session_id": entities.get("session_id")}
            elif action == "cancel_task":
                parameters = {"session_id": entities.get("session_id")}
            elif action == "provide_help":
                parameters = {"topic": entities.get("topic")}

            steps.append({"action": action, "parameters": parameters})

        # 返回任务计划
        return {
            "task_type": intent_type,
            "steps": steps,
            "requires_confirmation": False
        }

    def _create_default_plan(self, task_type: str, message: str) -> Dict[str, Any]:
        """创建默认任务计划

        Args:
            task_type: 任务类型
            message: 消息内容

        Returns:
            Dict[str, Any]: 默认任务计划
        """
        return {
            "task_type": task_type,
            "steps": [
                {
                    "action": "provide_information",
                    "parameters": {
                        "message": message
                    }
                }
            ],
            "requires_confirmation": False
        }

    def _plan_complex_task(self,
                       intent_type: str,
                       entities: Dict[str, Any],
                       context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """使用LLM规划复杂任务

        Args:
            intent_type: 意图类型
            entities: 提取的实体
            context: 上下文信息

        Returns:
            Dict[str, Any]: 任务规划结果
        """
        # 构建上下文提示
        context_prompt = ""
        if context:
            context_prompt = "上下文信息:\n"
            if "current_topic" in context:
                context_prompt += f"当前话题: {context['current_topic']}\n"
            if "current_stage" in context:
                context_prompt += f"当前阶段: {context['current_stage']}\n"
            if "available_content" in context:
                context_prompt += f"可用内容: {context['available_content']}\n"

        # 构建实体描述
        entities_str = json.dumps(entities, ensure_ascii=False, indent=2)

        # 构建完整提示
        full_prompt = (f"{context_prompt}\n"
                       f"意图类型: {intent_type}\n"
                       f"实体信息:\n{entities_str}\n\n"
                       f"请为上述用户意图规划具体的任务执行步骤。")

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
        self._validate_plan(result)

        # 记录规划结果
        logger.info(f"任务规划完成: {result.get('task_type')} (步骤数: {len(result.get('steps', []))})")

        return result

    def _validate_plan(self, plan: Dict[str, Any]) -> None:
        """验证任务规划结果的格式

        Args:
            plan: 规划结果

        Raises:
            ValueError: 当结果格式不符合要求时
        """
        # 检查必要字段
        required_fields = ["task_type", "steps"]
        for field in required_fields:
            if field not in plan:
                raise ValueError(f"规划结果缺少必要字段: {field}")

        # 验证任务类型
        if plan["task_type"] not in self.TASK_TYPES:
            logger.warning(f"未知任务类型: {plan['task_type']}，将其归类为'information_query'")
            plan["task_type"] = "information_query"

        # 验证步骤是否为列表
        if not isinstance(plan["steps"], list):
            logger.warning("步骤应为列表格式，重置为空列表")
            plan["steps"] = []

        # 验证每个步骤的格式
        valid_steps = []
        for step in plan["steps"]:
            if not isinstance(step, dict):
                logger.warning(f"无效的步骤格式: {step}，已忽略")
                continue

            if "action" not in step:
                logger.warning(f"步骤缺少必要的action字段: {step}，已忽略")
                continue

            if "parameters" not in step:
                logger.warning(f"步骤缺少parameters字段，默认为空字典")
                step["parameters"] = {}

            # 验证该任务类型是否支持此行动
            task_type = plan["task_type"]
            action = step["action"]

            if task_type in self.TASK_ACTIONS and action not in self.TASK_ACTIONS[task_type]:
                logger.warning(f"任务类型'{task_type}'不支持行动'{action}'，将尝试使用")

            valid_steps.append(step)

        # 更新步骤
        plan["steps"] = valid_steps

    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示

        Returns:
            str: 默认系统提示
        """
        return """你是一个专业的任务规划系统，负责将用户意图转化为具体的任务执行计划。

你的任务是根据用户意图和实体信息，规划出需要执行的步骤序列，确定每一步的参数和依赖关系。

支持的任务类型:
- trending_query: 获取热门话题
- research_request: 研究特定主题
- writing_request: 创作内容
- style_request: 调整内容风格
- review_request: 审核内容
- content_production: 完整内容生产流程
- information_query: 信息查询
- status_query: 任务状态查询
- help_request: 提供帮助信息
- cancel_request: 取消任务

每种任务类型支持的行动:
- trending_query: [get_trending_topics]
- research_request: [research_topic]
- writing_request: [create_content]
- style_request: [adjust_style]
- review_request: [review_content]
- content_production: [get_trending_topics, select_topic, research_topic, create_content, adjust_style, review_content]
- information_query: [provide_information]
- status_query: [check_status]
- help_request: [provide_help]
- cancel_request: [cancel_task]

以JSON格式返回规划结果，包含:
1. task_type: 任务类型
2. steps: 步骤列表，每个步骤包含action和parameters
3. requires_confirmation: 是否需要用户确认后执行
4. explanation: 简短解释任务计划的逻辑

示例：
{
  "task_type": "content_production",
  "steps": [
    {
      "action": "get_trending_topics",
      "parameters": {
        "category": "科技",
        "limit": 5
      }
    },
    {
      "action": "select_topic",
      "parameters": {
        "criteria": "popularity"
      }
    },
    {
      "action": "research_topic",
      "parameters": {
        "depth": "medium",
        "focus": ["最新进展", "关键挑战"]
      }
    },
    {
      "action": "create_content",
      "parameters": {
        "style": "分析性",
        "structure": "问题-分析-解决方案"
      }
    }
  ],
  "requires_confirmation": true,
  "explanation": "基于用户请求创建科技类内容，流程包括获取热门话题、选择话题、研究和创作四个步骤。"
}"""
