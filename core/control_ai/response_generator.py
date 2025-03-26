"""
响应生成器 - 将执行结果转化为自然语言回复

该模块负责将各类任务的执行结果转换为自然、友好的用户回复，根据结果内容和状态
生成适当的回复文本。
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional

from openai import OpenAI

# 配置日志
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """响应生成器

    将任务执行结果转化为自然语言回复。
    """

    def __init__(self, system_prompt: Optional[str] = None):
        """初始化响应生成器

        Args:
            system_prompt: 可选的系统提示，用于引导LLM生成更好的回复
        """
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # 设置系统提示
        self.system_prompt = system_prompt or self._get_default_system_prompt()

    def generate(self,
            task_result: Dict[str, Any],
            task_plan: Dict[str, Any],
            user_input: str,
            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """根据任务结果生成回复

        Args:
            task_result: 任务执行结果
            task_plan: 原始任务计划
            user_input: 用户原始输入
            context: 可选的上下文信息

        Returns:
            Dict[str, Any]: 生成的回复结果
        """
        try:
            # 提取任务类型和状态
            task_type = task_plan.get("task_type", "unknown")
            status = task_result.get("status", "error")

            # 处理任务执行错误的情况
            if status == "error":
                error_message = task_result.get("error", "未知错误")
                return self._create_error_response(error_message)

            # 对于简单结果直接使用模板生成回复
            if self._is_simple_result(task_type, task_result):
                return self._generate_simple_response(task_type, task_result)

            # 对于复杂结果使用LLM生成回复
            return self._generate_complex_response(task_result, task_plan, user_input, context)

        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}")

            # 返回错误回复
            return {
                "text": f"抱歉，在处理结果时遇到了问题: {str(e)}",
                "error": str(e)
            }

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建错误回复

        Args:
            error_message: 错误信息

        Returns:
            Dict[str, Any]: 错误回复
        """
        return {
            "text": f"抱歉，执行任务时遇到了问题: {error_message}",
            "suggestions": ["请尝试重新表述您的请求", "如需帮助，请输入'帮助'"]
        }

    def _is_simple_result(self, task_type: str, task_result: Dict[str, Any]) -> bool:
        """判断是否为简单结果类型

        Args:
            task_type: 任务类型
            task_result: 任务结果

        Returns:
            bool: 是否为简单结果
        """
        # 简单结果类型列表
        simple_types = ["status_query", "help_request", "cancel_request"]

        return task_type in simple_types

    def _generate_simple_response(self, task_type: str, task_result: Dict[str, Any]) -> Dict[str, Any]:
        """为简单结果生成回复

        Args:
            task_type: 任务类型
            task_result: 任务结果

        Returns:
            Dict[str, Any]: 简单回复
        """
        # 根据任务类型生成不同回复
        if task_type == "status_query":
            stage = task_result.get("stage", "未知")
            progress = task_result.get("progress", 0)
            text = f"当前任务进度: {stage} ({progress}%)"

            return {"text": text}

        elif task_type == "help_request":
            return {"text": "我可以帮助您进行内容创作、研究主题、查询热门话题等。您可以尝试以下请求:\n\n"
                          "1. 查询当前热门话题\n"
                          "2. 帮我研究[主题]\n"
                          "3. 写一篇关于[主题]的文章\n"
                          "4. 用[风格]风格写一篇[主题]的内容\n"
                          "5. 审核我的内容"}

        elif task_type == "cancel_request":
            result = task_result.get("result", "操作失败")
            return {"text": f"任务取消结果: {result}"}

        # 默认回复
        return {"text": "已完成处理。"}

    def _generate_complex_response(self,
                              task_result: Dict[str, Any],
                              task_plan: Dict[str, Any],
                              user_input: str,
                              context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """为复杂结果使用LLM生成回复

        Args:
            task_result: 任务执行结果
            task_plan: 原始任务计划
            user_input: 用户原始输入
            context: 可选的上下文信息

        Returns:
            Dict[str, Any]: 生成的复杂回复
        """
        # 获取任务类型
        task_type = task_plan.get("task_type", "unknown")

        # 构建上下文提示
        context_prompt = ""
        if context:
            context_prompt = "上下文信息:\n"
            if "current_topic" in context:
                context_prompt += f"当前话题: {context['current_topic']}\n"
            if "current_stage" in context:
                context_prompt += f"当前阶段: {context['current_stage']}\n"

        # 结果序列化
        task_result_str = json.dumps(task_result, ensure_ascii=False, indent=2)
        task_plan_str = json.dumps(task_plan, ensure_ascii=False, indent=2)

        # 构建完整提示
        full_prompt = (f"{context_prompt}\n"
                      f"用户输入: {user_input}\n\n"
                      f"任务类型: {task_type}\n"
                      f"任务计划:\n{task_plan_str}\n\n"
                      f"任务结果:\n{task_result_str}\n\n"
                      f"请根据上述任务结果生成自然、友好的回复。")

        # 构建消息
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": full_prompt}
        ]

        # 调用OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",  # 或其他适合的模型
            messages=messages,
            temperature=0.7,
        )

        # 解析响应
        text_response = response.choices[0].message.content

        # 尝试提取建议行动
        suggestions = self._extract_suggestions(text_response, task_type, task_result)

        # 记录生成结果
        logger.info(f"回复生成完成: {len(text_response)} 字符")

        return {
            "text": text_response,
            "suggestions": suggestions
        }

    def _extract_suggestions(self,
                        text: str,
                        task_type: str,
                        task_result: Dict[str, Any]) -> List[str]:
        """从回复文本中提取建议行动

        Args:
            text: 回复文本
            task_type: 任务类型
            task_result: 任务结果

        Returns:
            List[str]: 建议行动列表
        """
        suggestions = []

        # 根据任务类型添加建议
        if task_type == "trending_query":
            trending_topics = task_result.get("trending_topics", [])
            if trending_topics:
                # 取前三个话题作为建议
                top_topics = trending_topics[:3]
                for topic in top_topics:
                    topic_name = topic.get("topic", "")
                    if topic_name:
                        suggestions.append(f"写一篇关于'{topic_name}'的文章")

        elif task_type == "content_production" and task_result.get("status") == "success":
            suggestions.append("修改风格")
            suggestions.append("重新生成")
            suggestions.append("保存结果")

        # 全局默认建议
        if not suggestions:
            suggestions = ["查询热门话题", "帮助"]

        return suggestions

    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示

        Returns:
            str: 默认系统提示
        """
        return """你是一个专业的响应生成系统，负责将任务执行结果转化为自然、友好的回复文本。

你的任务是根据执行结果的内容和状态，生成一个针对用户原始请求的回复，回复应该是自然、简洁并且信息丰富的。

请注意以下生成原则:
1. 保持响应简洁明了，避免冗长
2. 重点突出关键信息和结果
3. 使用友好的对话风格，但保持专业性
4. 避免过度解释技术细节，除非用户特别询问
5. 如果结果包含错误，清晰指出并提供可能的解决方案
6. 如果内容很多，适当组织结构，使用标题或编号

根据不同任务类型，回复风格也应有所不同:
- trending_query: 简明列出热门话题，可以加入简短说明
- research_request: 提供研究发现的摘要，突出关键点
- writing_request: 介绍创作成果，可提及写作风格和主题
- style_request: 描述风格调整的变化
- review_request: 总结审核发现，指出优点和改进点
- content_production: 展示完整内容生产的结果，突出主题和风格特点

避免使用以下表达:
- "根据任务结果..."
- "系统已经..."
- "根据您的请求..."
- 过于机械的模板化表达

如果产出结果是很长的内容（如文章），不要完整复制，而是提供摘要和亮点，并告知用户内容已准备好。"""
