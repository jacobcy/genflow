"""进度跟踪模型"""
from typing import Dict, Optional, List, Any
from datetime import datetime, UTC
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
import json

# Keep enums as they define states/stages used by the progress logic
from ..infra.enums import ProductionStage, StageStatus

class ProgressData(BaseModel):
    """基础进度数据模型 (Pydantic)"""
    id: Optional[UUID] = None
    entity_id: str
    operation_type: str
    current_stage: Optional[str] = None
    status: str = "pending"
    progress_data: Dict[str, Any] = Field(default_factory=dict) # Stores detailed stage info, percentage, etc.
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
    error_count: int = 0
    error_details: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True  # Replaces orm_mode in Pydantic V2
    )

class ArticleProductionProgress:
    """文章生产进度跟踪 - 业务逻辑和状态管理

    负责跟踪文章在生产流程中的内部状态、阶段转换和进度计算。
    持久化由 ProgressManager 通过 ProgressFactory 处理。
    """

    def __init__(self, entity_id: str, initial_state: Optional[Dict] = None):
        """初始化进度跟踪

        Args:
            entity_id: 关联的文章ID
            initial_state: 从数据库加载的初始状态 (通常是 ProgressDB.progress_data)
        """
        self.entity_id = entity_id
        self.operation_type = "article_production" # Specific to this class

        if initial_state:
            # Load state from persistence
            self.current_stage = initial_state.get("current_stage", ProductionStage.TOPIC_DISCOVERY)
            self.stages = initial_state.get("stages", {})
            self.started_at = initial_state.get("started_at", datetime.now(UTC)) # Consider parsing if stored as string
            self.completed_at = initial_state.get("completed_at") # Consider parsing
            self.stage_history = initial_state.get("stage_history", [])
            self.error_count = initial_state.get("error_count", 0)
            self.paused_from_stage = initial_state.get("paused_from_stage")
            self.overall_status = initial_state.get("overall_status", "pending") # Add overall status tracking
        else:
            # Initialize new state
            self.current_stage = ProductionStage.TOPIC_DISCOVERY
            self.stages = {}
            self.started_at = datetime.now(UTC)
            self.completed_at = None
            self.stage_history = []
            self.error_count = 0
            self.paused_from_stage = None
            self.overall_status = "pending"

            # Initialize default stage structures
            for stage in ProductionStage:
                 # Exclude meta-statuses from being initialized as processable stages
                if stage not in [ProductionStage.COMPLETED, ProductionStage.FAILED, ProductionStage.PAUSED]:
                    self.stages[stage.value] = { # Use enum value for keys consistently
                        "status": StageStatus.PENDING.value,
                        "start_time": None,
                        "end_time": None,
                        "duration": 0,
                        "message": "",
                        "total_items": 0,
                        "completed_items": 0,
                        "avg_score": 0.0,
                        "error_count": 0
                    }
            # Ensure the initial stage is marked pending if creating new
            if self.current_stage.value in self.stages:
                 self.stages[self.current_stage.value]["status"] = StageStatus.PENDING.value

    def _update_timestamps(self):
        """Helper to potentially update 'updated_at' timestamp on state change."""
        # This object itself doesn't hold updated_at, the DB model does.
        # This method is a placeholder if needed in future.
        pass

    def start_stage(self, stage: ProductionStage, total_items: int = 0):
        """标记一个阶段开始 (仅更新内部状态)"""
        if stage.value not in self.stages:
            logger.warning(f"Attempted to start non-initialized stage: {stage.value}")
            # Optionally initialize it here if dynamic stages are needed
            return

        self.current_stage = stage
        stage_state = self.stages[stage.value]
        stage_state["status"] = StageStatus.IN_PROGRESS.value
        stage_state["start_time"] = datetime.now(UTC).isoformat() # Store as ISO string for JSON compatibility
        stage_state["total_items"] = total_items
        self.overall_status = "in_progress"
        self._update_timestamps()
        # --- REMOVED DB/ArticleFactory interaction ---

    def update_stage_progress(
        self,
        stage: ProductionStage,
        completed_items: Optional[int] = None,
        avg_score: Optional[float] = None,
        message: Optional[str] = None,
        error_increment: int = 0
    ):
        """更新当前活动阶段的进度详情 (仅更新内部状态)"""
        if stage.value not in self.stages:
            logger.warning(f"Attempted to update non-initialized stage: {stage.value}")
            return

        stage_state = self.stages[stage.value]

        if completed_items is not None:
            stage_state["completed_items"] = completed_items
        if avg_score is not None:
            stage_state["avg_score"] = avg_score
        if message is not None:
            stage_state["message"] = message
        if error_increment > 0:
            stage_state["error_count"] = stage_state.get("error_count", 0) + error_increment
            self.error_count = sum(s.get("error_count", 0) for s in self.stages.values())

        self._update_timestamps()

    def complete_stage(self, stage: ProductionStage):
        """标记一个阶段完成 (仅更新内部状态)"""
        if stage.value not in self.stages:
            logger.warning(f"Attempted to complete non-initialized stage: {stage.value}")
            return

        stage_state = self.stages[stage.value]
        stage_state["status"] = StageStatus.COMPLETED.value
        stage_state["end_time"] = datetime.now(UTC).isoformat()
        if stage_state["start_time"]:
            start_dt = datetime.fromisoformat(stage_state["start_time"])
            end_dt = datetime.fromisoformat(stage_state["end_time"])
            stage_state["duration"] = (end_dt - start_dt).total_seconds()

        # Determine next stage
        stages_list = list(ProductionStage) # Ensure order
        # Filter out meta-statuses before finding index
        processable_stages = [s for s in stages_list if s not in [ProductionStage.COMPLETED, ProductionStage.FAILED, ProductionStage.PAUSED]]

        try:
            current_index = processable_stages.index(stage)
            if current_index < len(processable_stages) - 1:
                next_stage = processable_stages[current_index + 1]
                self.current_stage = next_stage
                if next_stage.value in self.stages:
                    self.stages[next_stage.value]["status"] = StageStatus.PENDING.value
                else:
                    logger.warning(f"Next stage {next_stage.value} not initialized in progress state.")
            else:
                # Last processable stage completed, transition to overall completed
                self.complete_process()
        except ValueError:
            logger.error(f"Could not find stage {stage.value} in processable stages list.")
            # Consider failing the process here?
            self.fail_process("Internal error: Stage transition failed.")

        self._update_timestamps()
        # --- REMOVED DB/ArticleFactory interaction ---

    def complete_process(self):
        """标记整个流程成功完成 (仅更新内部状态)"""
        self.current_stage = ProductionStage.COMPLETED # Use the enum member
        self.overall_status = "completed"
        self.completed_at = datetime.now(UTC)
        self._update_timestamps()
        # --- REMOVED DB/ArticleFactory interaction ---

    def fail_process(self, error_message: Optional[str] = None):
        """标记整个流程失败 (仅更新内部状态)"""
        active_stage_value = self.current_stage.value if self.current_stage else "unknown"

        self.current_stage = ProductionStage.FAILED # Use the enum member
        self.overall_status = "failed"
        self.completed_at = datetime.now(UTC) # Mark completion time even on failure

        # Optionally mark the active stage as failed too
        if active_stage_value in self.stages:
            self.stages[active_stage_value]["status"] = StageStatus.FAILED.value
            self.stages[active_stage_value]["message"] = error_message or "Process failed at this stage."

        if error_message:
            self.add_error_log(self.current_stage, error_message) # Add to history

        self._update_timestamps()
        # --- REMOVED DB/ArticleFactory interaction ---

    def pause_process(self):
        """暂停流程 (仅更新内部状态)"""
        if self.overall_status not in ["in_progress", "pending"]:
            logger.warning(f"Cannot pause process in status: {self.overall_status}")
            return

        active_stage_value = self.current_stage.value

        self.paused_from_stage = active_stage_value # Store the stage value we paused from
        self.overall_status = "paused"
        # self.current_stage = ProductionStage.PAUSED # Maybe keep current_stage pointing to where it stopped? Or use PAUSED? Let's keep it pointing.

        # Mark the currently active stage state as paused
        if active_stage_value in self.stages:
            self.stages[active_stage_value]["status"] = StageStatus.PAUSED.value

        self._update_timestamps()
        # --- REMOVED DB/ArticleFactory interaction ---

    def resume_process(self):
        """恢复流程 (仅更新内部状态)"""
        if self.overall_status != "paused":
            logger.warning(f"Cannot resume process from status: {self.overall_status}")
            return

        if self.paused_from_stage and self.paused_from_stage in self.stages:
            resume_stage_value = self.paused_from_stage
            # Find the corresponding enum member
            try:
                self.current_stage = ProductionStage(resume_stage_value)
                self.stages[resume_stage_value]["status"] = StageStatus.IN_PROGRESS.value
                self.overall_status = "in_progress"
                self.paused_from_stage = None # Clear pause marker
            except ValueError:
                logger.error(f"Cannot resume: Invalid stage value '{resume_stage_value}' stored.")
                # Fallback or fail? Let's try to find the first non-completed stage
                self._find_and_resume_first_pending()
        else:
            # Fallback: Find the first non-completed stage if pause state is inconsistent
            self._find_and_resume_first_pending()

        self._update_timestamps()
        # --- REMOVED DB/ArticleFactory interaction ---

    def _find_and_resume_first_pending(self):
        """Helper to find the first stage not completed and resume from there."""
        processable_stages = [s for s in ProductionStage if s not in [ProductionStage.COMPLETED, ProductionStage.FAILED, ProductionStage.PAUSED]]
        resumed = False
        for stage in processable_stages:
            if stage.value in self.stages and self.stages[stage.value]["status"] != StageStatus.COMPLETED.value:
                self.current_stage = stage
                self.stages[stage.value]["status"] = StageStatus.IN_PROGRESS.value
                self.overall_status = "in_progress"
                self.paused_from_stage = None
                resumed = True
                logger.info(f"Resuming process at first non-completed stage: {stage.value}")
                break
        if not resumed:
            logger.warning("Could not find a stage to resume from. Process might be completed or in an inconsistent state.")
            # Decide on fallback: maybe mark as failed or completed?
            # For now, just log. The overall_status remains 'paused' if not resumed.

    def add_error_log(self, stage: Optional[ProductionStage], error: str):
        """添加错误日志到历史记录 (仅更新内部状态)"""
        # Ensure stage_history is initialized
        if not hasattr(self, 'stage_history') or self.stage_history is None:
            self.stage_history = []

        self.stage_history.append({
            "time": datetime.now(UTC).isoformat(),
            "stage": stage.value if stage else self.current_stage.value, # Use value
            "error": error
        })
        self.error_count = sum(s.get("error_count", 0) for s in self.stages.values()) # Recalculate total errors
        # Also increment stage-specific error if stage is provided and valid
        if stage and stage.value in self.stages:
            self.stages[stage.value]["error_count"] = self.stages[stage.value].get("error_count", 0) + 1

    @property
    def total_duration(self) -> float:
        """总耗时(秒)"""
        # Recalculate based on stored start/end times if available
        start = self.started_at
        end = self.completed_at or datetime.now(UTC)

        # Ensure start is datetime object
        if isinstance(start, str):
            try:
                start = datetime.fromisoformat(start)
            except ValueError: return 0 # Cannot calculate if start time is invalid

        # Ensure end is datetime object
        if isinstance(end, str):
            try:
                end = datetime.fromisoformat(end)
            except ValueError: end = datetime.now(UTC) # Default to now if end is invalid string

        if not start:
            return 0

        return (end - start).total_seconds()

    @property
    def progress_percentage(self) -> float:
        """总进度百分比 (基于文章生产阶段权重)"""
        # Recalculate based on current stage states
        stage_weights = {
            ProductionStage.TOPIC_DISCOVERY.value: 0.1,
            ProductionStage.TOPIC_RESEARCH.value: 0.2,
            ProductionStage.ARTICLE_WRITING.value: 0.3,
            ProductionStage.STYLE_ADAPTATION.value: 0.2,
            ProductionStage.ARTICLE_REVIEW.value: 0.2
        }

        total_progress = 0
        for stage_value, progress_details in self.stages.items():
            if stage_value in stage_weights:
                status = progress_details.get("status")
                if status == StageStatus.COMPLETED.value:
                    stage_progress = 1.0
                elif status == StageStatus.IN_PROGRESS.value and progress_details.get("total_items", 0) > 0:
                    stage_progress = progress_details.get("completed_items", 0) / progress_details["total_items"]
                else:
                    stage_progress = 0 # Pending or failed stages contribute 0 progress here
                total_progress += stage_progress * stage_weights[stage_value]

        # Ensure progress doesn't exceed 100 if weights are slightly off or logic changes
        return min(total_progress * 100, 100.0)

    def get_state_for_persistence(self) -> Dict[str, Any]:
        """获取需要持久化的内部状态 (用于 ProgressDB.progress_data)"""
        # Convert datetime objects to ISO strings if they exist
        started_at_iso = self.started_at.isoformat() if isinstance(self.started_at, datetime) else self.started_at
        completed_at_iso = self.completed_at.isoformat() if isinstance(self.completed_at, datetime) else self.completed_at

        # Deep copy stages to avoid modifying internal state if caller messes with the dict
        import copy
        stages_copy = copy.deepcopy(self.stages)

        return {
            "current_stage": self.current_stage.value if self.current_stage else None,
            "stages": stages_copy, # Contains stage-specific status, times, progress
            "started_at": started_at_iso,
            "completed_at": completed_at_iso,
            "stage_history": getattr(self, 'stage_history', []), # Ensure history exists
            "error_count": self.error_count,
            "paused_from_stage": self.paused_from_stage, # Store value
            "overall_status": self.overall_status, # Persist the overall status derived by methods
            # Optionally add percentage here if needed directly in DB JSON, though it's calculated
            # "progress_percentage": self.progress_percentage
        }

    def get_summary(self) -> Dict:
        """获取人类可读的进度摘要 (不用于持久化)"""
        state = self.get_state_for_persistence()
        # Enhance with calculated fields
        state["entity_id"] = self.entity_id
        state["operation_type"] = self.operation_type
        state["progress_percentage"] = self.progress_percentage
        state["duration"] = self.total_duration
        # Convert stage keys back to enum members for readability if desired? Or keep as strings.
        # state["stages"] = {ProductionStage(k): v for k, v in state["stages"].items()}
        return state

# Example usage (for testing/illustration - would normally be called by Factory/Service):
# progress_instance = ArticleProductionProgress(entity_id="article-123")
# print(progress_instance.get_summary())
# progress_instance.start_stage(ProductionStage.TOPIC_DISCOVERY, total_items=5)
# progress_instance.update_stage_progress(ProductionStage.TOPIC_DISCOVERY, completed_items=2)
# print(progress_instance.get_summary())
# state_to_save = progress_instance.get_state_for_persistence()
# print(json.dumps(state_to_save, indent=2))

# # Simulate loading
# loaded_state = state_to_save
# loaded_progress = ArticleProductionProgress(entity_id="article-123", initial_state=loaded_state)
# print("Loaded:")
# print(loaded_progress.get_summary())

# Need logger instance if running standalone tests
from loguru import logger
# logger.add("file.log") # Configure logger as needed
