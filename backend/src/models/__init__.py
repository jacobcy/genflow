# 导入所有模型，确保 SQLAlchemy 能够找到它们
from .base import Base
from .user import User
from .article import Article, Tag, article_tag
