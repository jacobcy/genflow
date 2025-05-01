"""定义 SQLAlchemy 关联表"""

from sqlalchemy import Table, Column, String, ForeignKey
from .session import Base

# 关联 ArticleStyle 和 ContentTypeName
content_type_style = Table(
    'content_type_style', # Table name
    Base.metadata,
    Column('style_name', String(100), ForeignKey('article_style.name', ondelete='CASCADE'), primary_key=True),
    Column('content_type_name', String(100), ForeignKey('content_type_name.name', ondelete='CASCADE'), primary_key=True)
    # Assuming ArticleStyle table is 'article_style' with pk 'name'
    # Assuming ContentTypeName table is 'content_type_name' with pk 'name'
    # Added ondelete='CASCADE' for potentially better data integrity if desired
)

# Add other association tables here as needed

# Association table for Article and Category (Many-to-Many)
article_category_association = Table(
    'article_category_association',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
    # Assuming ArticleDB table is 'articles' with pk 'id'
    # Assuming Category table is 'categories' with pk 'id'
)

# Association table for Article and Topic (Many-to-Many)
article_topic_association = Table(
    'article_topic_association',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topics.id', ondelete='CASCADE'), primary_key=True)
    # Assuming ArticleDB table is 'articles' with pk 'id'
    # Assuming Topic table is 'topics' with pk 'id'
)