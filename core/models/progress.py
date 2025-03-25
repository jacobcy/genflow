"""进度跟踪模型"""
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum

class ProductionStage(str, Enum):
    """生产阶段"""
    TOPIC_DISCOVERY = "topic_discovery"  # 话题发现
    TOPIC_RESEARCH = "topic_research"    # 话题研究
    ARTICLE_WRITING = "article_writing"  # 文章写作
    STYLE_ADAPTATION = "style_adaptation"  # 风格适配
    ARTICLE_REVIEW = "article_review"    # 文章审核
    COMPLETED = "completed"              # 已完成
    FAILED = "failed"                    # 失败
    PAUSED = "paused"                    # 暂停

class StageStatus(str, Enum):
    """阶段状态"""
    PENDING = "pending"      # 等待中
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    PAUSED = "paused"        # 暂停

class StageProgress:
    """阶段进度"""
    def __init__(self, stage: ProductionStage):
        self.stage = stage
        self.status = StageStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.total_items: int = 0
        self.completed_items: int = 0
        self.avg_score: float = 0.0
        self.error_count: int = 0
    
    @property
    def duration(self) -> float:
        """阶段耗时(秒)"""
        if not self.start_time:
            return 0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_items == 0:
            return 0
        return (self.completed_items - self.error_count) / self.total_items
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "status": self.status.value,
            "duration": self.duration,
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "success_rate": self.success_rate,
            "avg_score": self.avg_score,
            "error_count": self.error_count
        }

class ProductionProgress:
    """生产进度"""
    def __init__(self, production_id: str):
        self.production_id = production_id
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.current_stage = ProductionStage.TOPIC_DISCOVERY
        self.stage_status = StageStatus.PENDING
        self.total_topics = 0
        self.completed_topics = 0
        self.error_count = 0
        self.error_logs: List[Dict] = []
        self.stages: Dict[ProductionStage, StageProgress] = {
            stage: StageProgress(stage)
            for stage in ProductionStage
            if stage not in [
                ProductionStage.COMPLETED,
                ProductionStage.FAILED,
                ProductionStage.PAUSED
            ]
        }
    
    def start_stage(self, stage: ProductionStage, total_items: int):
        """开始阶段
        
        Args:
            stage: 阶段
            total_items: 总项目数
        """
        self.current_stage = stage
        self.stage_status = StageStatus.IN_PROGRESS
        stage_progress = self.stages[stage]
        stage_progress.status = StageStatus.IN_PROGRESS
        stage_progress.start_time = datetime.now()
        stage_progress.total_items = total_items
    
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
        stage_progress.completed_items = completed_items
        stage_progress.avg_score = avg_score
        stage_progress.error_count = error_count
        self.error_count = sum(s.error_count for s in self.stages.values())
    
    def complete_stage(self, stage: ProductionStage):
        """完成阶段
        
        Args:
            stage: 阶段
        """
        stage_progress = self.stages[stage]
        stage_progress.status = StageStatus.COMPLETED
        stage_progress.end_time = datetime.now()
        
        # 确定下一个阶段
        stages = list(ProductionStage)
        current_index = stages.index(stage)
        if current_index < len(stages) - 4:  # 排除 COMPLETED, FAILED, PAUSED
            self.current_stage = stages[current_index + 1]
            self.stage_status = StageStatus.PENDING
    
    def complete(self):
        """完成生产"""
        self.current_stage = ProductionStage.COMPLETED
        self.stage_status = StageStatus.COMPLETED
        self.end_time = datetime.now()
    
    def fail(self):
        """生产失败"""
        self.current_stage = ProductionStage.FAILED
        self.stage_status = StageStatus.FAILED
        self.end_time = datetime.now()
    
    def pause(self):
        """暂停生产"""
        self.current_stage = ProductionStage.PAUSED
        self.stage_status = StageStatus.PAUSED
        # 暂停当前阶段
        if self.current_stage in self.stages:
            self.stages[self.current_stage].status = StageStatus.PAUSED
    
    def resume(self):
        """恢复生产"""
        # 找到上一个未完成的阶段
        for stage in ProductionStage:
            if stage in self.stages and self.stages[stage].status != StageStatus.COMPLETED:
                self.current_stage = stage
                self.stage_status = StageStatus.IN_PROGRESS
                self.stages[stage].status = StageStatus.IN_PROGRESS
                break
    
    def add_error(self, stage: ProductionStage, error: str):
        """添加错误日志
        
        Args:
            stage: 阶段
            error: 错误信息
        """
        self.error_logs.append({
            "time": datetime.now(),
            "stage": stage,
            "error": error
        })
    
    @property
    def duration(self) -> float:
        """总耗时(秒)"""
        if not self.start_time:
            return 0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
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
                if progress.status == StageStatus.COMPLETED:
                    stage_progress = 1.0
                elif progress.total_items > 0:
                    stage_progress = progress.completed_items / progress.total_items
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
            "production_id": self.production_id,
            "current_stage": self.current_stage.value,
            "stage_status": self.stage_status.value,
            "progress_percentage": self.progress_percentage,
            "duration": self.duration,
            "total_topics": self.total_topics,
            "completed_topics": self.completed_topics,
            "error_count": self.error_count,
            "stages": {
                stage.value: progress.to_dict()
                for stage, progress in self.stages.items()
            }
        } 