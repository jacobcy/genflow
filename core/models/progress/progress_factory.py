from typing import Optional, Any, Dict
from uuid import UUID
from loguru import logger

from .progress_manager import ProgressManager
from .progress import ArticleProductionProgress, ProgressData # Import specific classes and base data model
from .progress_db import ProgressDB

class ProgressFactory:
    """Progress Factory

    负责创建、获取和更新不同类型的进度跟踪对象。
    协调 ProgressManager 进行持久化。
    """

    @classmethod
    def create_progress(cls, entity_id: str, operation_type: str) -> Optional[Any]:
        """创建并持久化一个新的进度对象

        Args:
            entity_id: 关联实体的ID
            operation_type: 操作类型 (e.g., 'article_production')

        Returns:
            创建的进度对象实例 (e.g., ArticleProductionProgress) 或 None
        """
        progress_instance = None
        initial_state_for_db = None

        # 1. 根据类型实例化具体的进度类
        if operation_type == "article_production":
            progress_instance = ArticleProductionProgress(entity_id=entity_id)
            initial_state_for_db = progress_instance.get_state_for_persistence()
        # Add elif blocks here for other operation_types in the future
        else:
            logger.warning(f"Unsupported operation type for progress tracking: {operation_type}")
            # Optionally create a generic progress object or return None
            return None

        # 2. 使用 Manager 持久化初始状态
        # We need the overall status and current stage for the main DB fields
        initial_db_status = initial_state_for_db.get("overall_status", "pending")
        initial_db_stage = initial_state_for_db.get("current_stage")

        progress_db = ProgressManager.create_progress(
            entity_id=entity_id,
            operation_type=operation_type,
            initial_data=initial_state_for_db # Store the full state in JSON
        )

        if not progress_db:
            logger.error(f"Failed to save initial progress state for {entity_id}, type {operation_type}")
            return None

        # 3. 更新实例的ID (虽然 ArticleProductionProgress 内部不直接使用，但 Factory 返回的对象最好有)
        # progress_instance.id = progress_db.id # ArticleProductionProgress doesn't have an id field
        # Instead, maybe return a wrapper or just the business logic object?
        # For now, returning the business logic object seems aligned with the pattern.
        # The caller can get the ID from the DB object if needed, or we add it to the instance.

        logger.info(f"Created and saved progress: id={progress_db.id}, type={operation_type}, entity={entity_id}")
        return progress_instance # Return the stateful business logic object

    @classmethod
    def get_progress(cls, progress_id: UUID) -> Optional[Any]:
        """获取进度对象

        Args:
            progress_id: 进度记录的UUID

        Returns:
            重建的进度对象实例 (e.g., ArticleProductionProgress) 或 None
        """
        # 1. 从 Manager 获取持久化数据
        progress_db = ProgressManager.get_progress_by_id(progress_id)
        if not progress_db:
            logger.warning(f"Progress record with id {progress_id} not found.")
            return None

        # 2. 根据类型重建具体的进度类实例
        operation_type = progress_db.operation_type
        entity_id = progress_db.entity_id
        initial_state = progress_db.progress_data # Load state from JSON blob

        progress_instance = None
        if operation_type == "article_production":
            progress_instance = ArticleProductionProgress(entity_id=entity_id, initial_state=initial_state)
            # Add ID if the class supports it, or handle otherwise
            # progress_instance.id = progress_id
        # Add elif blocks for other types
        else:
            logger.warning(f"Cannot reconstruct progress object: Unsupported type '{operation_type}' for id {progress_id}")
            # Optionally return a generic ProgressData object?
            # return ProgressData.from_orm(progress_db) # Use Pydantic model as fallback?
            return None

        return progress_instance

    @classmethod
    def update_progress(cls, progress_id: UUID, progress_instance: Any) -> bool:
        """使用进度对象的当前状态更新持久化记录

        Args:
            progress_id: 进度记录的UUID
            progress_instance: 当前状态的进度对象实例 (e.g., ArticleProductionProgress)

        Returns:
            True 如果更新成功, False 否则
        """
        if not hasattr(progress_instance, 'get_state_for_persistence') or not hasattr(progress_instance, 'overall_status') or not hasattr(progress_instance, 'current_stage'):
            logger.error(f"Invalid progress instance provided for update (id: {progress_id}). Missing required methods/attributes.")
            return False

        # 1. 获取当前需要持久化的状态
        state_to_save = progress_instance.get_state_for_persistence()
        current_overall_status = progress_instance.overall_status
        current_stage_enum = progress_instance.current_stage
        current_stage_value = current_stage_enum.value if current_stage_enum else None
        error_count = progress_instance.error_count
        completed_at = progress_instance.completed_at # This might be datetime or None

        # 2. 准备更新字典
        updates = {
            "progress_data": state_to_save,
            "status": current_overall_status, # Update the main status field
            "current_stage": current_stage_value,
            "error_count": error_count,
            "completed_at": completed_at # Update completion time if set
            # updated_at is handled by the DB
        }

        # 3. 调用 Manager 更新
        updated_db = ProgressManager.update_progress(progress_id, updates)

        if updated_db:
            logger.info(f"Successfully updated progress record {progress_id}")
            return True
        else:
            logger.error(f"Failed to update progress record {progress_id}")
            return False

    @classmethod
    def delete_progress(cls, progress_id: UUID) -> bool:
        """删除进度记录

        Args:
            progress_id: 进度记录的UUID

        Returns:
            True 如果成功删除, False 否则
        """
        return ProgressManager.delete_progress(progress_id)