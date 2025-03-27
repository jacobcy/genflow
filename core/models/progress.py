"""进度跟踪模型"""
from typing import Dict, Optional, List
from datetime import datetime
from .article import Article
from .enums import ProductionStage, StageStatus

# 导入ArticleService，使用try-except块避免循环导入
try:
    from .article_service import ArticleService
except ImportError:
    # 如果在导入时发生循环导入，将在方法中动态导入
    ArticleService = None

class ArticleProductionProgress:
    """文章生产进度跟踪

    跟踪文章在生产流程中的进度和状态
    """

    def __init__(self, article: Article = None, article_id: str = None):
        """初始化进度跟踪

        Args:
            article: 文章对象，可选
            article_id: 文章ID，如果未提供article则使用
        """
        self.article = article
        self.article_id = article_id if article_id else (article.id if article else None)
        self.current_stage = ProductionStage.TOPIC_DISCOVERY
        self.stages = {}
        self.started_at = datetime.now()
        self.completed_at = None
        self.stage_history = []
        self.error_count = 0
        self.paused_from_stage = None

        # 初始化各阶段状态
        for stage in ProductionStage:
            self.stages[stage] = {
                "status": StageStatus.PENDING,
                "start_time": None,
                "end_time": None,
                "duration": 0,
                "message": "",
                "total_items": 0,
                "completed_items": 0,
                "avg_score": 0.0,
                "error_count": 0
            }

        # 设置第一阶段为待处理
        self.stages[self.current_stage]["status"] = StageStatus.PENDING

    def start_stage(self, stage: ProductionStage, total_items: int):
        """开始阶段

        Args:
            stage: 阶段
            total_items: 总项目数
        """
        self.current_stage = stage
        self.stages[stage]["status"] = StageStatus.IN_PROGRESS
        self.stages[stage]["start_time"] = datetime.now()
        self.stages[stage]["total_items"] = total_items

        # 同步文章状态并保存到数据库
        if self.article:
            if ArticleService:
                new_status = ProductionStage.to_article_status(stage)
                ArticleService.update_article_status(self.article, new_status)

    def update_progress(
        self,
        stage: ProductionStage,
        completed_items: int,
        avg_score: float,
        error_count: int = 0
    ):
        """更新进度

        Args:
            stage: 阶段
            completed_items: 已完成项目数
            avg_score: 平均评分
            error_count: 错误数
        """
        stage_progress = self.stages[stage]
        stage_progress["completed_items"] = completed_items
        stage_progress["avg_score"] = avg_score
        stage_progress["error_count"] = error_count
        self.error_count = sum(s["error_count"] for s in self.stages.values())

    def complete_stage(self, stage: ProductionStage):
        """完成阶段

        Args:
            stage: 阶段
        """
        stage_progress = self.stages[stage]
        stage_progress["status"] = StageStatus.COMPLETED
        stage_progress["end_time"] = datetime.now()

        # 确定下一个阶段
        stages = list(ProductionStage)
        current_index = stages.index(stage)
        if current_index < len(stages) - 4:  # 排除 COMPLETED, FAILED, PAUSED
            next_stage = stages[current_index + 1]
            self.current_stage = next_stage
            self.stages[next_stage]["status"] = StageStatus.PENDING
            # 同步文章状态到下一阶段并保存到数据库
            if self.article:
                if ArticleService:
                    new_status = ProductionStage.to_article_status(next_stage)
                    ArticleService.update_article_status(self.article, new_status)

    def complete(self):
        """完成生产"""
        self.current_stage = ProductionStage.COMPLETED
        self.stages[self.current_stage]["status"] = StageStatus.COMPLETED
        self.completed_at = datetime.now()

        # 同步文章状态并保存到数据库
        if self.article:
            if ArticleService:
                ArticleService.update_article_status(self.article, "completed")

    def fail(self):
        """生产失败"""
        self.current_stage = ProductionStage.FAILED
        self.stages[self.current_stage]["status"] = StageStatus.FAILED
        self.completed_at = datetime.now()

        # 同步文章状态并保存到数据库
        if self.article:
            if ArticleService:
                ArticleService.update_article_status(self.article, "failed")

    def pause(self):
        """暂停生产"""
        # 记录当前活动阶段
        active_stage = self.current_stage

        # 记录被暂停的阶段（用于恢复）
        self.paused_from_stage = active_stage

        # 设置当前阶段为PAUSED
        self.current_stage = ProductionStage.PAUSED
        self.stages[ProductionStage.PAUSED]["status"] = StageStatus.PAUSED

        # 将之前的活动阶段标记为暂停
        if active_stage != ProductionStage.PAUSED and active_stage in self.stages:
            self.stages[active_stage]["status"] = StageStatus.PAUSED

        # 同步文章状态并保存到数据库
        if self.article:
            if ArticleService:
                ArticleService.update_article_status(self.article, "paused")

    def resume(self):
        """恢复生产"""
        # 优先恢复到之前暂停的活动阶段
        if hasattr(self, 'paused_from_stage') and self.paused_from_stage in self.stages:
            resume_stage = self.paused_from_stage
            self.current_stage = resume_stage
            self.stages[resume_stage]["status"] = StageStatus.IN_PROGRESS

            # 同步文章状态并保存到数据库
            if self.article and ArticleService:
                new_status = ProductionStage.to_article_status(resume_stage)
                ArticleService.update_article_status(self.article, new_status)

            # 清除暂停记录
            delattr(self, 'paused_from_stage')
            return

        # 如果没有记录暂停前的阶段，则找到第一个未完成的阶段
        for stage in ProductionStage:
            if stage in self.stages and self.stages[stage]["status"] != StageStatus.COMPLETED:
                self.current_stage = stage
                self.stages[stage]["status"] = StageStatus.IN_PROGRESS
                # 同步文章状态并保存到数据库
                if self.article and ArticleService:
                    new_status = ProductionStage.to_article_status(stage)
                    ArticleService.update_article_status(self.article, new_status)
                break

    def add_error(self, stage: ProductionStage, error: str):
        """添加错误日志

        Args:
            stage: 阶段
            error: 错误信息
        """
        self.stage_history.append({
            "time": datetime.now(),
            "stage": stage,
            "error": error
        })

    @property
    def duration(self) -> float:
        """总耗时(秒)"""
        if not self.started_at:
            return 0
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()

    @property
    def progress_percentage(self) -> float:
        """总进度百分比"""
        stage_weights = {
            ProductionStage.TOPIC_DISCOVERY: 0.1,
            ProductionStage.TOPIC_RESEARCH: 0.2,
            ProductionStage.ARTICLE_WRITING: 0.3,
            ProductionStage.STYLE_ADAPTATION: 0.2,
            ProductionStage.ARTICLE_REVIEW: 0.2
        }

        total_progress = 0
        for stage, progress in self.stages.items():
            if stage in stage_weights:
                if progress["status"] == StageStatus.COMPLETED:
                    stage_progress = 1.0
                elif progress["total_items"] > 0:
                    stage_progress = progress["completed_items"] / progress["total_items"]
                else:
                    stage_progress = 0
                total_progress += stage_progress * stage_weights[stage]

        return total_progress * 100

    def get_summary(self) -> Dict:
        """获取进度摘要

        Returns:
            Dict: 进度摘要
        """
        return {
            "article_id": self.article_id,
            "current_stage": self.current_stage.value,
            "stage_status": self.stages[self.current_stage]["status"].value,
            "progress_percentage": self.progress_percentage,
            "duration": self.duration,
            "stage_history": self.stage_history,
            "stages": {
                stage.value: progress
                for stage, progress in self.stages.items()
            }
        }
