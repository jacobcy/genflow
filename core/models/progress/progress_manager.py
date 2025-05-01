from typing import Optional, Dict, Any
from uuid import UUID
from loguru import logger

from ..infra.base_manager import BaseManager
from .progress_db import ProgressDB
from sqlalchemy.exc import SQLAlchemyError
from ..db.session import get_db

class ProgressManager(BaseManager):
    """Progress Manager

    负责进度数据的数据库 CRUD 操作。
    """

    @classmethod
    def create_progress(cls, entity_id: str, operation_type: str, initial_data: Optional[Dict[str, Any]] = None) -> Optional[ProgressDB]:
        """创建新的进度记录

        Args:
            entity_id: 关联的实体ID
            operation_type: 操作类型
            initial_data: 初始进度数据 (JSON)

        Returns:
            创建的 ProgressDB 对象或 None (如果出错)
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法创建进度记录")
            return None

        progress = ProgressDB(
            entity_id=entity_id,
            operation_type=operation_type,
            status="pending",
            progress_data=initial_data or {}
        )
        try:
            with get_db() as db:
                db.add(progress)
                db.commit()
                db.refresh(progress)
            logger.info(f"Progress record created for entity {entity_id}, type {operation_type}, id {progress.id}")
            return progress
        except SQLAlchemyError as e:
            logger.error(f"Failed to create progress record for entity {entity_id}: {e}")
            # TODO: Consider rollback if needed, although commit might handle it
            return None

    @classmethod
    def get_progress_by_id(cls, progress_id: UUID) -> Optional[ProgressDB]:
        """通过ID获取进度记录

        Args:
            progress_id: 进度记录的UUID

        Returns:
            ProgressDB 对象或 None
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法获取进度记录")
            return None

        try:
            with get_db() as db:
                return db.query(ProgressDB).filter(ProgressDB.id == progress_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get progress record by id {progress_id}: {e}")
            return None

    @classmethod
    def get_progress_by_entity_id(cls, entity_id: str) -> Optional[ProgressDB]:
        """通过实体ID获取进度记录

        Args:
            entity_id: 关联的实体ID（如文章ID）

        Returns:
            ProgressDB 对象或 None
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法获取进度记录")
            return None

        try:
            with get_db() as db:
                return db.query(ProgressDB).filter(ProgressDB.entity_id == entity_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get progress record by entity_id {entity_id}: {e}")
            return None

    @classmethod
    def update_progress(cls, progress_id: UUID, updates: Dict[str, Any]) -> Optional[ProgressDB]:
        """更新进度记录

        Args:
            progress_id: 进度记录的UUID
            updates: 包含要更新字段的字典

        Returns:
            更新后的 ProgressDB 对象或 None (如果记录不存在或出错)
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法更新进度记录")
            return None

        try:
            with get_db() as db:
                progress = db.query(ProgressDB).filter(ProgressDB.id == progress_id).first()
                if not progress:
                    logger.warning(f"Progress record with id {progress_id} not found for update.")
                    return None

                # Update fields
                for key, value in updates.items():
                    if hasattr(progress, key):
                        setattr(progress, key, value)
                    else:
                        logger.warning(f"Attempted to update non-existent field '{key}' on ProgressDB {progress_id}")

                db.commit()
                db.refresh(progress)
            logger.info(f"Progress record {progress_id} updated successfully.")
            return progress
        except SQLAlchemyError as e:
            logger.error(f"Failed to update progress record {progress_id}: {e}")
            # TODO: Rollback consideration
            return None

    @classmethod
    def delete_progress(cls, progress_id: UUID) -> bool:
        """删除进度记录

        Args:
            progress_id: 进度记录的UUID

        Returns:
            True 如果成功删除，False 如果记录不存在或出错
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法删除进度记录")
            return False

        try:
            with get_db() as db:
                progress = db.query(ProgressDB).filter(ProgressDB.id == progress_id).first()
                if not progress:
                    logger.warning(f"Progress record with id {progress_id} not found for deletion.")
                    return False
                db.delete(progress)
                db.commit()
            logger.info(f"Progress record {progress_id} deleted successfully.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete progress record {progress_id}: {e}")
            # TODO: Rollback consideration
            return False