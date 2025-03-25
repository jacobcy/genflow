from typing import List
from datetime import datetime
from app.models.platform import PlatformAccount
from app.extensions import db

class PlatformService:
    def get_user_platforms(self, user_id: int) -> List[PlatformAccount]:
        """获取用户的平台账号列表"""
        return PlatformAccount.query.filter_by(user_id=user_id).all()
    
    def bind_platform(self, 
                     user_id: int,
                     platform: str,
                     access_token: str,
                     refresh_token: str = None,
                     expires_at: datetime = None) -> PlatformAccount:
        """绑定平台账号"""
        # 检查是否已绑定
        existing = PlatformAccount.query.filter_by(
            user_id=user_id,
            platform=platform
        ).first()
        
        if existing:
            # 更新令牌
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.expires_at = expires_at
            account = existing
        else:
            # 创建新绑定
            account = PlatformAccount(
                user_id=user_id,
                platform=platform,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at
            )
            db.session.add(account)
        
        db.session.commit()
        return account
