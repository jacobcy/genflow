"""
控制AI - GenFlow内容生产系统的智能控制中心

该模块实现了ControlAI类，作为GenFlow内容生产系统的大脑，负责自然语言理解、
任务规划和执行协调，将用户请求转化为具体任务并调度专业团队完成内容生产。
"""

import json
import logging
import os
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from core.control_ai.intent_recognizer import IntentRecognizer
from core.control_ai.task_planner import TaskPlanner
from core.control_ai.response_generator import ResponseGenerator
from core.control_ai.clients import TeamClientFactory
from core.controllers.content_controller import ContentController

# 配置日志
logger = logging.getLogger(__name__)

# 会话状态
class SessionState:
    """用户会话状态

    存储与用户交互的上下文信息。
    """

    def __init__(self, session_id: str):
        """初始化会话状态

        Args:
            session_id: 会话标识符
        """
        self.session_id = session_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.history = []
        self.current_task = None
        self.task_results = {}
        self.task_status = "idle"  # idle, processing, completed, failed
        self.content = None

    def update(self):
        """更新会话状态时间戳"""
        self.updated_at = datetime.now()

    def add_interaction(self, user_input: str, response: str):
        """添加交互记录

        Args:
            user_input: 用户输入
            response: 系统响应
        """
        self.history.append({
            "user": user_input,
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })
        self.update()

    def set_task(self, task: Dict[str, Any]):
        """设置当前任务

        Args:
            task: 任务信息
        """
        self.current_task = task
        self.task_status = "processing"
        self.update()

    def set_task_result(self, task_id: str, result: Dict[str, Any]):
        """设置任务结果

        Args:
            task_id: 任务ID
            result: 任务结果
        """
        self.task_results[task_id] = result
        self.update()

    def set_task_status(self, status: str):
        """设置任务状态

        Args:
            status: 新状态
        """
        self.task_status = status
        self.update()

    def set_content(self, content: Dict[str, Any]):
        """设置生成的内容

        Args:
            content: 内容信息
        """
        self.content = content
        self.update()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict[str, Any]: 会话状态字典
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "history_length": len(self.history),
            "last_interaction": self.history[-1] if self.history else None,
            "task_status": self.task_status,
            "has_content": self.content is not None
        }

    def get_context(self) -> Dict[str, Any]:
        """获取会话上下文

        Returns:
            Dict[str, Any]: 会话上下文
        """
        context = {
            "history": self.history[-5:] if len(self.history) > 5 else self.history,
            "current_task": self.current_task,
            "task_status": self.task_status
        }

        if self.content:
            context["current_topic"] = self.content.get("topic")
            context["available_content"] = True

        return context


class ControlAI:
    """控制AI

    GenFlow内容生产系统的智能控制中心，负责理解用户意图、规划和协调任务执行。
    """

    def __init__(self, config_dir: Optional[str] = None):
        """初始化控制AI

        Args:
            config_dir: 配置目录路径，如果不提供则使用默认路径
        """
        # 设置配置目录
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "config")

        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)

        # 加载系统提示
        system_prompt_path = os.path.join(self.config_dir, "system_prompt.txt")
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = None
            logger.warning(f"系统提示文件不存在: {system_prompt_path}")

        # 初始化组件
        self.intent_recognizer = IntentRecognizer(self.system_prompt)
        self.task_planner = TaskPlanner()
        self.response_generator = ResponseGenerator()
        self.client_factory = TeamClientFactory()
        self.content_controller = ContentController()

        # 用户会话存储
        self.sessions = {}

        logger.info("控制AI初始化完成")

    async def process_request(self,
                        user_input: str,
                        session_id: Optional[str] = None) -> Dict[str, Any]:
        """处理用户请求

        Args:
            user_input: 用户输入内容
            session_id: 可选的会话ID，如果不提供则创建新会话

        Returns:
            Dict[str, Any]: 处理结果
        """
        # 获取或创建会话
        session = self.get_session(session_id)

        try:
            logger.info(f"处理用户请求: {user_input[:50]}...，会话ID: {session.session_id}")

            # 1. 识别用户意图
            context = session.get_context()
            intent_result = self.intent_recognizer.recognize(user_input, context)

            logger.info(f"识别出意图: {intent_result.get('intent_type')}")

            # 2. 规划任务
            task_plan = self.task_planner.plan(intent_result, context)

            logger.info(f"规划任务: {task_plan.get('task_type')}，步骤数: {len(task_plan.get('steps', []))}")

            # 3. 执行任务
            task_id = str(uuid.uuid4())
            task_plan["task_id"] = task_id

            # 设置会话当前任务
            session.set_task(task_plan)

            # 立即执行简单任务，复杂任务异步执行
            if self._is_simple_task(task_plan):
                task_result = await self._execute_task(task_plan)
                session.set_task_result(task_id, task_result)
                session.set_task_status("completed" if task_result.get("status") == "success" else "failed")
            else:
                # 返回任务已开始的响应
                asyncio.create_task(self._execute_task_async(session, task_plan))
                task_result = {
                    "status": "pending",
                    "message": "任务正在处理中",
                    "task_id": task_id
                }

            # 4. 生成回复
            response = self.response_generator.generate(task_result, task_plan, user_input, context)

            # 5. 更新会话
            session.add_interaction(user_input, response.get("text", ""))

            # 构建响应
            result = {
                "response": response.get("text", ""),
                "session_id": session.session_id,
                "suggestions": response.get("suggestions", []),
                "task_id": task_id,
                "task_status": "pending" if task_result.get("status") == "pending" else "completed"
            }

            return result

        except Exception as e:
            logger.error(f"处理请求失败: {str(e)}")

            # 更新会话状态
            if session.current_task:
                session.set_task_status("failed")

            # 添加错误交互记录
            error_response = f"抱歉，处理您的请求时出现了问题: {str(e)}"
            session.add_interaction(user_input, error_response)

            # 返回错误响应
            return {
                "response": error_response,
                "session_id": session.session_id,
                "error": str(e),
                "suggestions": ["请尝试重新表述您的请求", "如需帮助，请输入'帮助'"]
            }

    def get_session(self, session_id: Optional[str] = None) -> SessionState:
        """获取会话状态

        Args:
            session_id: 会话ID，如果不提供则创建新会话

        Returns:
            SessionState: 会话状态
        """
        if not session_id:
            # 创建新会话
            new_id = str(uuid.uuid4())
            session = SessionState(new_id)
            self.sessions[new_id] = session
            return session

        # 获取现有会话
        if session_id in self.sessions:
            return self.sessions[session_id]

        # 创建指定ID的新会话
        session = SessionState(session_id)
        self.sessions[session_id] = session
        return session

    async def execute_task_step(self,
                          session_id: str,
                          task_id: str,
                          action: str) -> Dict[str, Any]:
        """执行任务步骤

        Args:
            session_id: 会话ID
            task_id: 任务ID
            action: 行动名称(confirm/cancel/retry等)

        Returns:
            Dict[str, Any]: 执行结果
        """
        # 获取会话
        session = self.get_session(session_id)

        # 验证任务ID
        if not session.current_task or session.current_task.get("task_id") != task_id:
            raise ValueError(f"找不到任务: {task_id}")

        # 处理不同行动
        if action == "confirm":
            # 确认执行任务
            if session.task_status == "processing":
                return {"status": "success", "message": "任务已在处理中"}

            task_plan = session.current_task
            asyncio.create_task(self._execute_task_async(session, task_plan))

            return {
                "status": "success",
                "message": "任务已确认执行",
                "task_id": task_id
            }

        elif action == "cancel":
            # 取消任务
            session.set_task_status("cancelled")

            return {
                "status": "success",
                "message": "任务已取消",
                "task_id": task_id
            }

        elif action == "retry":
            # 重试任务
            task_plan = session.current_task
            session.set_task_status("processing")
            asyncio.create_task(self._execute_task_async(session, task_plan))

            return {
                "status": "success",
                "message": "任务正在重试",
                "task_id": task_id
            }

        else:
            # 不支持的行动
            return {
                "status": "error",
                "message": f"不支持的行动: {action}",
                "task_id": task_id
            }

    def _is_simple_task(self, task_plan: Dict[str, Any]) -> bool:
        """判断是否为简单任务

        简单任务可以立即执行，复杂任务需要异步执行

        Args:
            task_plan: 任务计划

        Returns:
            bool: 是否为简单任务
        """
        # 简单任务类型列表
        simple_types = [
            "information_query",
            "status_query",
            "help_request",
            "cancel_request"
        ]

        task_type = task_plan.get("task_type")

        # 首先检查类型
        if task_type in simple_types:
            return True

        # 然后检查步骤数量
        steps = task_plan.get("steps", [])
        return len(steps) <= 1

    async def _execute_task(self, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务

        Args:
            task_plan: 任务计划

        Returns:
            Dict[str, Any]: 任务执行结果
        """
        task_type = task_plan.get("task_type")
        steps = task_plan.get("steps", [])

        # 处理信息查询类任务
        if task_type == "information_query":
            message = "对不起，无法提供相关信息。"
            for step in steps:
                if step.get("action") == "provide_information":
                    message = step.get("parameters", {}).get("message", message)

            return {
                "status": "success",
                "message": message
            }

        # 处理状态查询
        elif task_type == "status_query":
            # 从参数中获取会话ID
            session_id = None
            for step in steps:
                if step.get("action") == "check_status":
                    session_id = step.get("parameters", {}).get("session_id")

            # 如果没有会话ID，返回错误
            if not session_id or session_id not in self.sessions:
                return {
                    "status": "error",
                    "message": "无法找到指定会话",
                    "session_id": session_id
                }

            # 获取会话状态
            session = self.sessions[session_id]

            return {
                "status": "success",
                "session_status": session.to_dict(),
                "task_status": session.task_status,
                "stage": session.current_task.get("task_type") if session.current_task else None,
                "progress": 100 if session.task_status == "completed" else (
                    0 if session.task_status == "idle" else 50
                )
            }

        # 处理帮助请求
        elif task_type == "help_request":
            return {
                "status": "success",
                "help_info": {
                    "available_commands": [
                        "查询热门话题",
                        "研究[主题]",
                        "写一篇关于[主题]的文章",
                        "用[风格]风格写一篇关于[主题]的内容",
                        "审核我的内容"
                    ],
                    "examples": [
                        "有什么热门话题推荐?",
                        "帮我研究一下元宇宙的发展",
                        "写一篇关于健康饮食的文章",
                        "用轻松幽默的风格写一篇关于旅游的文章",
                        "审核我刚才创建的内容"
                    ]
                }
            }

        # 处理取消请求
        elif task_type == "cancel_request":
            # 从参数中获取会话ID
            session_id = None
            for step in steps:
                if step.get("action") == "cancel_task":
                    session_id = step.get("parameters", {}).get("session_id")

            # 如果没有会话ID，返回错误
            if not session_id or session_id not in self.sessions:
                return {
                    "status": "error",
                    "message": "无法找到指定会话",
                    "session_id": session_id
                }

            # 更新会话状态
            session = self.sessions[session_id]
            session.set_task_status("cancelled")

            return {
                "status": "success",
                "result": "任务已取消",
                "session_id": session_id
            }

        # 对于其他类型的任务，需要与专业团队交互
        # 这部分由子类_execute_task_async处理
        return {
            "status": "pending",
            "message": "任务需要异步执行"
        }

    async def _execute_task_async(self, session: SessionState, task_plan: Dict[str, Any]):
        """异步执行任务

        Args:
            session: 会话状态
            task_plan: 任务计划
        """
        task_type = task_plan.get("task_type")
        task_id = task_plan.get("task_id")
        steps = task_plan.get("steps", [])

        try:
            logger.info(f"开始异步执行任务: {task_type}")

            # 标记任务为处理中
            session.set_task_status("processing")

            # 执行热门话题查询
            if task_type == "trending_query":
                result = await self._execute_trending_query(steps)

            # 执行研究请求
            elif task_type == "research_request":
                result = await self._execute_research_request(steps)

            # 执行写作请求
            elif task_type == "writing_request":
                result = await self._execute_writing_request(steps)

            # 执行风格调整
            elif task_type == "style_request":
                result = await self._execute_style_request(steps, session)

            # 执行审核请求
            elif task_type == "review_request":
                result = await self._execute_review_request(steps, session)

            # 执行完整内容生产
            elif task_type == "content_production":
                result = await self._execute_content_production(steps)

            # 处理未知任务类型
            else:
                result = {
                    "status": "error",
                    "message": f"不支持的任务类型: {task_type}"
                }

            # 更新会话状态和结果
            if result.get("status") == "success":
                session.set_task_status("completed")

                # 如果有生成内容，保存到会话
                if "content" in result:
                    session.set_content(result)
            else:
                session.set_task_status("failed")

            session.set_task_result(task_id, result)

            logger.info(f"任务执行完成: {task_type}")

            return result

        except Exception as e:
            logger.error(f"任务执行异常: {str(e)}")

            # 更新会话状态
            session.set_task_status("failed")

            # 保存错误信息
            error_result = {
                "status": "error",
                "message": str(e),
                "task_id": task_id,
                "task_type": task_type
            }
            session.set_task_result(task_id, error_result)

            return error_result

    async def _execute_trending_query(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行热门话题查询

        Args:
            steps: 任务步骤

        Returns:
            Dict[str, Any]: 执行结果
        """
        # 查找get_trending_topics步骤
        for step in steps:
            if step.get("action") == "get_trending_topics":
                params = step.get("parameters", {})
                category = params.get("category")
                limit = params.get("limit", 10)

                # 调用选题团队API
                topic_client = self.client_factory.get_client("topic")
                result = await topic_client.get_trending_topics(category, limit)

                # 添加状态信息
                result["status"] = "success"
                return result

        # 如果没有找到对应步骤
        return {
            "status": "error",
            "message": "任务步骤不包含获取热门话题的操作"
        }

    async def _execute_research_request(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行研究请求

        Args:
            steps: 任务步骤

        Returns:
            Dict[str, Any]: 执行结果
        """
        # 查找research_topic步骤
        for step in steps:
            if step.get("action") == "research_topic":
                params = step.get("parameters", {})
                topic = params.get("topic")
                depth = params.get("depth", "medium")
                focus_areas = params.get("focus_areas")

                if not topic:
                    return {
                        "status": "error",
                        "message": "缺少必要参数: topic"
                    }

                # 调用研究团队API
                research_client = self.client_factory.get_client("research")
                result = await research_client.research_topic(topic, depth, focus_areas)

                # 添加状态信息
                result["status"] = "success"
                return result

        # 如果没有找到对应步骤
        return {
            "status": "error",
            "message": "任务步骤不包含研究主题的操作"
        }

    async def _execute_writing_request(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行写作请求

        Args:
            steps: 任务步骤

        Returns:
            Dict[str, Any]: 执行结果
        """
        # 查找create_content步骤
        for step in steps:
            if step.get("action") == "create_content":
                params = step.get("parameters", {})
                topic = params.get("topic")
                style = params.get("style")
                structure = params.get("structure")

                if not topic:
                    return {
                        "status": "error",
                        "message": "缺少必要参数: topic"
                    }

                # 先进行研究
                research_client = self.client_factory.get_client("research")
                research_result = await research_client.research_topic(topic)

                # 调用写作团队API
                writing_client = self.client_factory.get_client("writing")
                result = await writing_client.create_content(
                    topic,
                    research_result,
                    style,
                    structure
                )

                # 添加状态信息
                result["status"] = "success"
                return result

        # 如果没有找到对应步骤
        return {
            "status": "error",
            "message": "任务步骤不包含创建内容的操作"
        }

    async def _execute_style_request(self,
                              steps: List[Dict[str, Any]],
                              session: SessionState) -> Dict[str, Any]:
        """执行风格调整请求

        Args:
            steps: 任务步骤
            session: 会话状态

        Returns:
            Dict[str, Any]: 执行结果
        """
        # 确保会话中有内容
        if not session.content:
            return {
                "status": "error",
                "message": "会话中没有可调整的内容"
            }

        # 查找adjust_style步骤
        for step in steps:
            if step.get("action") == "adjust_style":
                params = step.get("parameters", {})
                style = params.get("style")

                if not style:
                    return {
                        "status": "error",
                        "message": "缺少必要参数: style"
                    }

                # 获取会话中的内容
                content = session.content.get("content")
                topic = session.content.get("topic")

                # 调用风格团队API
                style_client = self.client_factory.get_client("style")
                result = await style_client.adjust_style(content, style)

                # 更新会话内容
                result["topic"] = topic
                result["status"] = "success"

                # 更新会话内容
                session.set_content(result)

                return result

        # 如果没有找到对应步骤
        return {
            "status": "error",
            "message": "任务步骤不包含调整风格的操作"
        }

    async def _execute_review_request(self,
                              steps: List[Dict[str, Any]],
                              session: SessionState) -> Dict[str, Any]:
        """执行审核请求

        Args:
            steps: 任务步骤
            session: 会话状态

        Returns:
            Dict[str, Any]: 执行结果
        """
        # 确保会话中有内容
        if not session.content:
            return {
                "status": "error",
                "message": "会话中没有可审核的内容"
            }

        # 查找review_content步骤
        for step in steps:
            if step.get("action") == "review_content":
                # 获取会话中的内容
                content = session.content.get("content")
                topic = session.content.get("topic")

                # 调用审核团队API
                review_client = self.client_factory.get_client("review")
                result = await review_client.review_content(topic, content)

                # 添加状态信息
                result["status"] = "success"
                return result

        # 如果没有找到对应步骤
        return {
            "status": "error",
            "message": "任务步骤不包含审核内容的操作"
        }

    async def _execute_content_production(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行完整内容生产流程

        Args:
            steps: 任务步骤

        Returns:
            Dict[str, Any]: 执行结果
        """
        # 从步骤中提取参数
        topic = None
        category = None
        style = None
        keywords = []

        for step in steps:
            action = step.get("action")
            params = step.get("parameters", {})

            if action == "select_topic" and params.get("topic"):
                topic = params.get("topic")

            elif action == "get_trending_topics" and params.get("category"):
                category = params.get("category")

            elif action in ["create_content", "adjust_style"] and params.get("style"):
                style = params.get("style")

            elif action == "specify_keywords" and params.get("keywords"):
                keywords = params.get("keywords")

        # 使用内容控制器执行完整流程
        # 初始化控制器
        await self.content_controller.initialize()

        # 生产内容
        result = await self.content_controller.produce_content(
            topic=topic,
            category=category,
            style=style,
            keywords=keywords,
            mode='auto'  # 使用自动模式
        )

        # 将结果格式化为统一接口
        return {
            "status": "success" if result.get("status") == "success" else "error",
            "topic": topic or category,
            "result": result,
            "content": result.get("final_article") or (result.get("final_articles")[0] if result.get("final_articles") else None),
            "all_contents": result.get("final_articles"),
            "progress": result.get("progress_summary", {})
        }

    # 映射类别和风格
    def map_category(self, category: Optional[str]) -> Optional[str]:
        """映射类别名称

        Args:
            category: 类别名称

        Returns:
            Optional[str]: 映射后的类别名称
        """
        if not category:
            return None

        # 类别映射表
        category_map = {
            "科技": "technology",
            "娱乐": "entertainment",
            "体育": "sports",
            "健康": "health",
            "商业": "business",
            "教育": "education",
            "旅游": "travel",
            "美食": "food",
            "生活": "lifestyle",
            "艺术": "art"
        }

        # 反向映射表
        reverse_map = {v: k for k, v in category_map.items()}

        # 尝试映射
        if category in category_map:
            return category_map[category]
        elif category in reverse_map:
            return category

        # 如果没有匹配，返回原值
        return category

    def map_style(self, style: Optional[str]) -> Optional[str]:
        """映射风格名称

        Args:
            style: 风格名称

        Returns:
            Optional[str]: 映射后的风格名称
        """
        if not style:
            return None

        # 风格映射表
        style_map = {
            "专业": "professional",
            "轻松": "casual",
            "正式": "formal",
            "幽默": "humorous",
            "严肃": "serious",
            "文学": "literary",
            "简洁": "concise",
            "详细": "detailed",
            "叙事": "narrative",
            "说明": "explanatory",
            "议论": "argumentative",
            "分析": "analytical"
        }

        # 反向映射表
        reverse_map = {v: k for k, v in style_map.items()}

        # 尝试映射
        if style in style_map:
            return style_map[style]
        elif style in reverse_map:
            return style

        # 如果没有匹配，返回原值
        return style
