from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from typing import Dict, Any
from datetime import datetime, timezone
import time

from core.models.db.session import Base
from core.models.db.utils import JSONEncodedDict

class PlatformDB(Base):
    """平台配置的数据库存储模型"""
    __tablename__ = "platform"
    __table_args__ = {'extend_existing': True}

    # Use 'id' as primary key to match Pydantic model and config files
    id = Column(String(100), primary_key=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True) # Consider removing if config is static

    # Platform characteristics (simplified)
    platform_type = Column(String(50), nullable=True) # Corresponds to category?
    url = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True) # Might be better stored elsewhere or in config

    # Store complex constraints and technical details as JSON
    # This avoids complex table structures for potentially changing static config
    constraints = Column(JSONEncodedDict, nullable=True)
    technical = Column(JSONEncodedDict, nullable=True)
    # Removed individual constraint/technical columns like max_title_length, etc.
    # Removed api_config (now part of technical)
    # Removed allowed_media_types, max_content_length (part of constraints)

    # Timestamps using timezone-aware UTC
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PlatformDB {self.id}>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 (仅基本字段)

        Note: This might not be needed if data access goes via Manager+Pydantic

        Returns:
            Dict[str, Any]: 字典表示
        """
        # Process timestamps carefully
        def format_dt(dt):
            if dt and isinstance(dt, datetime):
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.isoformat()
            return None

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_enabled": self.is_enabled,
            "platform_type": self.platform_type,
            "url": self.url,
            "logo_url": self.logo_url,
            "constraints": self.constraints, # Keep as is from JSON column
            "technical": self.technical,   # Keep as is from JSON column
            "created_at": format_dt(self.created_at),
            "updated_at": format_dt(self.updated_at)
        }
