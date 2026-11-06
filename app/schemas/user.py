"""
    用户模块`user.py`的请求/响应模型

    请求模型：UserCreate（注册用）
    - `username`：字符串，必填
    - `password`：字符串，必填（明文，接口收到后在服务层转哈希）
    - `email`：字符串，可选

    响应模型：UserResponse（返回用户信息用）
    - `id`：整数
    - `username`：字符串
    - `email`：字符串 / 空
    - `is_active`：布尔值
    - `created_at`：时间

    ### 统一规则
    1. 所有模型都继承 `pydantic.BaseModel`
    2. **响应模型必须加** `from_attributes = True` 配置，支持直接从 ORM 数据库对象转换
        `from_attributes` 是 Pydantic 的模型配置项，必须放在**内部的 Config 类**里，不能直接作为模型的字段属性写在外面。
    3. 响应模型里绝对不能出现 `password_hash` 这类敏感字段
    4. 可选字段标注类型为 `Optional[str]` 或者 `str | None`
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True