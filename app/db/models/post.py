"""
    文章表
    前置统一规则：
        1. 所有模型都继承 `app.db.base` 里的 `Base` 类
        2. 用 `__tablename__` 指定数据库里的真实表名
        3. 字段全部用 `Column(类型, 约束)` 定义
"""
"""
    字段名	    类型	                约束
    id	        整数	                主键、自增
    title	    字符串 (最长 200)	    非空、加索引
    content	    长文本	            非空
    author_id	整数	                外键关联 users.id、非空
    created_at	时间	                默认当前时间
    updated_at	时间	                默认当前时间、更新时自动刷新
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.db.base import Base
from datetime import datetime


class Post(Base):
    __tablename__ = "posts" #数据库里真实的表名（文章表）

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
