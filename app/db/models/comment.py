"""
    评论表
    前置统一规则：
        1. 所有模型都继承 `app.db.base` 里的 `Base` 类
        2. 用 `__tablename__` 指定数据库里的真实表名
        3. 字段全部用 `Column(类型, 约束)` 定义
"""
"""
    字段名	    类型	                约束
    id	        整数	                主键、自增
    content	    字符串 (最长 500)	    非空
    post_id	    整数	                外键关联 posts.id、非空
    author_id	整数	                外键关联 users.id、非空
    created_at	时间	                默认当前时间
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base import Base
from datetime import datetime


class Comment(Base):
    __tablename__ = "comments" #数据库里真实的表名（评论表）

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
