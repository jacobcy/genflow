"""
GenFlow API - 内容生产系统的API接口

提供内容生产系统的Web API，用于与前端或其他系统进行交互。
"""

import asyncio
import uuid
import random
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from core.controllers.content_controller import ContentController
from core.agents.topic_crew import TopicCrew
from core.agents.research_crew import ResearchCrew
from core.agents.writing_crew import WritingCrew
from core.agents.style_crew import StyleCrew
from core.agents.review_crew import ReviewCrew
from core.models.platform.platform import get_default_platform
from core.controllers.team_adapter import (
    ResearchTeamAdapter,
    TopicTeamAdapter,
    WritingTeamAdapter,
    ReviewTeamAdapter,
    StyleTeamAdapter
)
from src.schemas.crews import TeamRequest, InitializeRequest
from src.schemas.common import APIResponse
from core.models.topic.topic import Topic

# 配置日志
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="GenFlow API",
    description="内容生产系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 辅助函数
def get_random_category() -> str:
    """获取随机分类"""
    categories = ["技术", "商业", "健康", "娱乐", "教育", "科学", "艺术", "文化"]
    return random.choice(categories)

def get_random_style() -> str:
    """获取随机风格"""
    styles = ["专业", "轻松", "正式", "幽默", "严肃", "文学", "简洁", "详细", "叙事"]
    return random.choice(styles)

# 请求模型
class ContentProductionRequest(BaseModel):
    """内容生产请求"""
    topic: Optional[str] = Field(None, description="内容主题，如不提供则由系统自动选题")
    category: Optional[str] = Field(None, description="内容分类，如设置为random则随机选择")
    style: Optional[str] = Field(None, description="写作风格，如设置为random则随机选择")

    @field_validator('category')
    def validate_category(cls, v):
        """验证类别"""
        if v == "random":
            return get_random_category()
        return v

    @field_validator('style')
    def validate_style(cls, v):
        """验证风格"""
        if v == "random":
            return get_random_style()
        return v

# 任务状态
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# 任务存储
tasks = {}

# 依赖项
async def get_content_controller():
    controller = ContentController()
    await controller.initialize()
    return controller

async def get_topic_crew():
    return TopicCrew()

async def get_research_crew():
    return ResearchCrew()

async def get_writing_crew():
    return WritingCrew()

async def get_style_crew():
    return StyleCrew()

async def get_review_crew():
    return ReviewCrew()

# 添加团队适配器依赖
def get_research_adapter() -> ResearchTeamAdapter:
    """获取研究团队适配器"""
    return ResearchTeamAdapter()

def get_topic_adapter() -> TopicTeamAdapter:
    """获取选题团队适配器"""
    return TopicTeamAdapter()

def get_writing_adapter() -> WritingTeamAdapter:
    """获取写作团队适配器"""
    return WritingTeamAdapter()

def get_review_adapter() -> ReviewTeamAdapter:
    """获取审核团队适配器"""
    return ReviewTeamAdapter()

def get_style_adapter() -> StyleTeamAdapter:
    """获取风格团队适配器"""
    return StyleTeamAdapter()

# 路由
@app.get("/")
async def root():
    """API根路径"""
    return {"message": "欢迎使用GenFlow API"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

@app.post("/produce-content", response_model=APIResponse)
async def produce_content(
    request: ContentProductionRequest,
    background_tasks: BackgroundTasks,
    content_controller: ContentController = Depends(get_content_controller)
):
    """启动内容生产流程

    自动执行完整内容生产流程：选题 -> 研究 -> 写作 -> 风格化 -> 审核

    - 如果提供了topic，将直接使用该主题
    - 如果未提供topic，则自动选择热门话题
    - 可以指定分类和风格，或设置为random进行随机选择
    """
    try:
        # 处理分类
        category = request.category
        if not category or category == "random":
            category = get_random_category()

        # 处理风格
        style = request.style
        if not style or style == "random":
            style = get_random_style()

        # 创建任务ID
        task_id = f"task_{len(tasks) + 1}"

        # 注册任务
        tasks[task_id] = {
            "status": TaskStatus.PENDING,
            "result": None,
            "error": None
        }

        # 准备任务参数
        production_params = {
            "topic": request.topic,
            "category": category,
            "style": style,
            "platform": get_default_platform()  # 使用默认平台配置
        }

        # 在后台运行任务
        background_tasks.add_task(
            run_content_production,
            task_id,
            content_controller,
            **production_params
        )

        return APIResponse(
            success=True,
            message="内容生产任务已启动",
            task_id=task_id,
            data={"parameters": production_params}
        )

    except Exception as e:
        logger.error(f"启动内容生产失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动内容生产失败: {str(e)}"
        )

@app.get("/task/{task_id}", response_model=APIResponse)
async def get_task_status(task_id: str):
    """获取任务状态

    查询指定任务ID的执行状态和结果
    """
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到任务: {task_id}"
        )

    task = tasks[task_id]

    return APIResponse(
        success=True,
        message=f"任务状态: {task['status']}",
        task_id=task_id,
        data={
            "status": task["status"],
            "result": task["result"],
            "error": task["error"]
        }
    )

# 团队单独API
@app.post("/team/topic", response_model=APIResponse)
async def run_topic_team(
    request: TeamRequest,
    topic_crew: TopicCrew = Depends(get_topic_crew)
):
    """运行选题团队

    获取热门话题建议或验证话题价值
    """
    try:
        # 获取参数
        auto_mode = request.parameters.get("auto_mode", False)

        # 调用选题团队
        if auto_mode:
            result = await asyncio.to_thread(
                topic_crew.run_workflow,
                request.topic,
                auto_mode=True
            )
        else:
            result = await asyncio.to_thread(
                topic_crew.run_workflow,
                request.topic
            )

        return APIResponse(
            success=True,
            message="选题团队执行成功",
            data={"result": result}
        )

    except Exception as e:
        logger.error(f"运行选题团队失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"运行选题团队失败: {str(e)}"
        )

@app.post("/team/research", response_model=APIResponse)
async def run_research_team(
    request: TeamRequest,
    research_adapter: ResearchTeamAdapter = Depends(get_research_adapter)
):
    """运行研究团队

    收集话题相关资料
    """
    try:
        # 获取参数
        depth = request.parameters.get("depth", "medium")

        # 调用研究团队适配器
        result = await research_adapter.research_topic(
            topic=request.topic,
            depth=depth,
            options=request.parameters
        )

        return APIResponse(
            success=True,
            message="研究团队执行成功",
            data={"result": result}
        )

    except Exception as e:
        logger.error(f"运行研究团队失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"运行研究团队失败: {str(e)}"
        )

@app.get("/team/research/{topic_id}/status", response_model=APIResponse)
async def get_research_status(
    topic_id: str,
    research_adapter: ResearchTeamAdapter = Depends(get_research_adapter)
):
    """获取研究团队状态

    Args:
        topic_id: 话题ID
    """
    try:
        status = await research_adapter.get_research_status(topic_id)
        return APIResponse(
            success=True,
            message="获取研究状态成功",
            data={"status": status}
        )
    except Exception as e:
        logger.error(f"获取研究状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取研究状态失败: {str(e)}"
        )

@app.post("/team/research/initialize", response_model=APIResponse)
async def initialize_research_team(
    request: InitializeRequest,
    research_adapter: ResearchTeamAdapter = Depends(get_research_adapter)
):
    """初始化研究团队

    Args:
        request: 初始化参数
    """
    try:
        await research_adapter.initialize(**request.parameters)
        return APIResponse(
            success=True,
            message="研究团队初始化成功"
        )
    except Exception as e:
        logger.error(f"初始化研究团队失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化研究团队失败: {str(e)}"
        )

@app.get("/team/research/progress", response_model=APIResponse)
async def get_research_progress(
    research_adapter: ResearchTeamAdapter = Depends(get_research_adapter)
):
    """获取研究团队进度"""
    try:
        progress = research_adapter.get_progress()
        return APIResponse(
            success=True,
            message="获取进度成功",
            data={"progress": progress}
        )
    except Exception as e:
        logger.error(f"获取进度失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取进度失败: {str(e)}"
        )

@app.post("/team/writing", response_model=APIResponse)
async def run_writing_team(
    request: TeamRequest,
    writing_crew: WritingCrew = Depends(get_writing_crew)
):
    """运行写作团队

    撰写内容
    """
    try:
        # 获取参数
        style = request.parameters.get("style")

        # 获取研究资料
        research_data = request.parameters.get("research_data")

        # 如果没有提供研究资料，尝试先进行研究
        if not research_data:
            research_crew = await get_research_crew()
            research_data = await asyncio.to_thread(
                research_crew.run_workflow,
                request.topic,
                depth="medium"
            )

        # 调用写作团队
        result = await asyncio.to_thread(
            writing_crew.run_workflow,
            request.topic,
            research_data=research_data,
            style=style
        )

        return APIResponse(
            success=True,
            message="写作团队执行成功",
            data={"result": result}
        )

    except Exception as e:
        logger.error(f"运行写作团队失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"运行写作团队失败: {str(e)}"
        )

@app.post("/team/style", response_model=APIResponse)
async def run_style_team(
    request: TeamRequest,
    style_crew: StyleCrew = Depends(get_style_crew)
):
    """运行风格团队

    调整内容风格
    """
    try:
        # 获取参数
        style = request.parameters.get("style")
        content = request.parameters.get("content")

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少必要参数: content"
            )

        # 如果没有提供风格，使用默认风格
        if not style:
            style = "professional"

        # 调用风格团队
        result = await asyncio.to_thread(
            style_crew.run_workflow,
            request.topic,
            content=content,
            style=style
        )

        return APIResponse(
            success=True,
            message="风格团队执行成功",
            data={"result": result}
        )

    except Exception as e:
        logger.error(f"运行风格团队失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"运行风格团队失败: {str(e)}"
        )

@app.post("/team/review", response_model=APIResponse)
async def run_review_team(
    request: TeamRequest,
    review_crew: ReviewCrew = Depends(get_review_crew)
):
    """运行审核团队

    审核内容质量
    """
    try:
        # 获取参数
        content = request.parameters.get("content")

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少必要参数: content"
            )

        # 调用审核团队
        result = await asyncio.to_thread(
            review_crew.run_workflow,
            request.topic,
            content=content
        )

        return APIResponse(
            success=True,
            message="审核团队执行成功",
            data={"result": result}
        )

    except Exception as e:
        logger.error(f"运行审核团队失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"运行审核团队失败: {str(e)}"
        )

# 后台任务处理
async def run_content_production(
    task_id: str,
    content_controller: ContentController,
    **kwargs
):
    """执行内容生产过程

    Args:
        task_id: 任务ID
        content_controller: 内容控制器
        **kwargs: 内容生产参数
    """
    try:
        # 更新任务状态
        tasks[task_id]["status"] = TaskStatus.RUNNING

        # 执行内容生产
        result = await content_controller.produce_content(**kwargs)

        # 更新任务信息
        tasks[task_id]["status"] = TaskStatus.COMPLETED
        tasks[task_id]["result"] = result

        logger.info(f"任务 {task_id} 完成")

    except Exception as e:
        logger.error(f"任务 {task_id} 失败: {str(e)}")

        # 更新任务状态
        tasks[task_id]["status"] = TaskStatus.FAILED
        tasks[task_id]["error"] = str(e)

# 选题团队 API
@app.post("/team/topic/generate", response_model=APIResponse)
async def generate_topics(
    request: TeamRequest,
    topic_adapter: TopicTeamAdapter = Depends(get_topic_adapter)
):
    """生成话题建议"""
    try:
        category = request.parameters.get("category")
        count = request.parameters.get("count", 5)

        topics = await topic_adapter.generate_topics(
            category=category,
            count=count,
            options=request.parameters
        )

        return APIResponse(
            success=True,
            message="生成话题成功",
            data={"topics": topics}
        )
    except Exception as e:
        logger.error(f"生成话题失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成话题失败: {str(e)}"
        )

@app.post("/team/topic/evaluate", response_model=APIResponse)
async def evaluate_topic(
    request: TeamRequest,
    topic_adapter: TopicTeamAdapter = Depends(get_topic_adapter)
):
    """评估话题价值"""
    try:
        result = await topic_adapter.evaluate_topic(
            topic=request.topic,
            options=request.parameters
        )

        return APIResponse(
            success=True,
            message="评估话题成功",
            data={"evaluation": result}
        )
    except Exception as e:
        logger.error(f"评估话题失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评估话题失败: {str(e)}"
        )

# 写作团队 API
@app.post("/team/writing", response_model=APIResponse)
async def write_content(
    request: TeamRequest,
    writing_adapter: WritingTeamAdapter = Depends(get_writing_adapter)
):
    """写作内容"""
    try:
        research_data = request.parameters.get("research_data", {})
        style = request.parameters.get("style")

        result = await writing_adapter.write_content(
            topic=request.topic,
            research_data=research_data,
            style=style,
            options=request.parameters
        )

        return APIResponse(
            success=True,
            message="写作内容成功",
            data={"content": result}
        )
    except Exception as e:
        logger.error(f"写作内容失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"写作内容失败: {str(e)}"
        )

@app.get("/team/writing/{topic_id}/status", response_model=APIResponse)
async def get_writing_status(
    topic_id: str,
    writing_adapter: WritingTeamAdapter = Depends(get_writing_adapter)
):
    """获取写作状态"""
    try:
        status = await writing_adapter.get_writing_status(topic_id)
        return APIResponse(
            success=True,
            message="获取写作状态成功",
            data={"status": status}
        )
    except Exception as e:
        logger.error(f"获取写作状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取写作状态失败: {str(e)}"
        )

# 风格团队 API
@app.post("/team/style/apply", response_model=APIResponse)
async def apply_style(
    request: TeamRequest,
    style_adapter: StyleTeamAdapter = Depends(get_style_adapter)
):
    """应用风格"""
    try:
        content = request.parameters.get("content")
        style = request.parameters.get("style")

        if not content:
            raise ValueError("缺少内容参数")
        if not style:
            raise ValueError("缺少风格参数")

        result = await style_adapter.apply_style(
            topic=request.topic,
            content=content,
            style=style,
            options=request.parameters
        )

        return APIResponse(
            success=True,
            message="应用风格成功",
            data={"content": result}
        )
    except Exception as e:
        logger.error(f"应用风格失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"应用风格失败: {str(e)}"
        )

@app.get("/team/style/available", response_model=APIResponse)
async def get_available_styles(
    style_adapter: StyleTeamAdapter = Depends(get_style_adapter)
):
    """获取可用风格列表"""
    try:
        styles = await style_adapter.get_available_styles()
        return APIResponse(
            success=True,
            message="获取风格列表成功",
            data={"styles": styles}
        )
    except Exception as e:
        logger.error(f"获取风格列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取风格列表失败: {str(e)}"
        )

# 审核团队 API
@app.post("/team/review", response_model=APIResponse)
async def review_content(
    request: TeamRequest,
    review_adapter: ReviewTeamAdapter = Depends(get_review_adapter)
):
    """审核内容"""
    try:
        content = request.parameters.get("content")
        if not content:
            raise ValueError("缺少内容参数")

        result = await review_adapter.review_content(
            topic=request.topic,
            content=content,
            options=request.parameters
        )

        return APIResponse(
            success=True,
            message="审核内容成功",
            data={"review": result}
        )
    except Exception as e:
        logger.error(f"审核内容失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审核内容失败: {str(e)}"
        )

@app.get("/team/review/{topic_id}/result", response_model=APIResponse)
async def get_review_result(
    topic_id: str,
    review_adapter: ReviewTeamAdapter = Depends(get_review_adapter)
):
    """获取审核结果"""
    try:
        result = await review_adapter.get_review_result(topic_id)
        if result is None:
            raise ValueError("未找到审核结果")

        return APIResponse(
            success=True,
            message="获取审核结果成功",
            data={"review": result}
        )
    except Exception as e:
        logger.error(f"获取审核结果失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取审核结果失败: {str(e)}"
        )

# 通用团队操作
@app.post("/team/{team_type}/initialize", response_model=APIResponse)
async def initialize_team(
    team_type: str,
    request: InitializeRequest,
    topic_adapter: TopicTeamAdapter = Depends(get_topic_adapter),
    research_adapter: ResearchTeamAdapter = Depends(get_research_adapter),
    writing_adapter: WritingTeamAdapter = Depends(get_writing_adapter),
    style_adapter: StyleTeamAdapter = Depends(get_style_adapter),
    review_adapter: ReviewTeamAdapter = Depends(get_review_adapter)
):
    """初始化指定团队

    Args:
        team_type: 团队类型(topic/research/writing/style/review)
    """
    try:
        adapters = {
            "topic": topic_adapter,
            "research": research_adapter,
            "writing": writing_adapter,
            "style": style_adapter,
            "review": review_adapter
        }

        adapter = adapters.get(team_type)
        if not adapter:
            raise ValueError(f"未知的团队类型: {team_type}")

        await adapter.initialize(**request.parameters)

        return APIResponse(
            success=True,
            message=f"初始化{team_type}团队成功"
        )
    except Exception as e:
        logger.error(f"初始化团队失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化团队失败: {str(e)}"
        )

@app.get("/team/{team_type}/progress", response_model=APIResponse)
async def get_team_progress(
    team_type: str,
    topic_adapter: TopicTeamAdapter = Depends(get_topic_adapter),
    research_adapter: ResearchTeamAdapter = Depends(get_research_adapter),
    writing_adapter: WritingTeamAdapter = Depends(get_writing_adapter),
    style_adapter: StyleTeamAdapter = Depends(get_style_adapter),
    review_adapter: ReviewTeamAdapter = Depends(get_review_adapter)
):
    """获取指定团队的进度

    Args:
        team_type: 团队类型(topic/research/writing/style/review)
    """
    try:
        adapters = {
            "topic": topic_adapter,
            "research": research_adapter,
            "writing": writing_adapter,
            "style": style_adapter,
            "review": review_adapter
        }

        adapter = adapters.get(team_type)
        if not adapter:
            raise ValueError(f"未知的团队类型: {team_type}")

        progress = adapter.get_progress()

        return APIResponse(
            success=True,
            message="获取进度成功",
            data={"progress": progress}
        )
    except Exception as e:
        logger.error(f"获取进度失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取进度失败: {str(e)}"
        )

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
