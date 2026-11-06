"""
    用户表
    前置统一规则：
        1. 所有模型都继承 `app.db.base` 里的 `Base` 类
        2. 用 `__tablename__` 指定数据库里的真实表名
        3. 字段全部用 `Column(类型, 约束)` 定义
"""
"""
    字段名           类型	                    约束
    id	            整数	                    主键、自增
    username	    字符串 (最长 50)	        唯一、非空、加索引
    password_hash	字符串 (最长 255)	        非空
    email	        字符串 (最长 100)	        唯一、可为空
    is_active	    布尔值	                默认值 True
    created_at	    时间	                    默认当前时间
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base, get_db
from datetime import datetime

# 用户表定义
class User(Base):
    __tablename__ = "users" #数据库里真实的表名（用户表）

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)