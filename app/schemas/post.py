"""
    文章模块`post.py`的请求/响应模型

    请求模型：PostCreate（发布文章用）
    - `title`：字符串，必填
    - `content`：字符串，必填

    响应模型：PostResponse（返回文章详情用）
    - `id`：整数
    - `title`：字符串
    - `content`：字符串
    - `author_id`：整数
    - `created_at`：时间
    - `updated_at`：时间

    ### 统一规则
    1. 所有模型都继承 `pydantic.BaseModel`
    2. **响应模型必须加** `from_attributes = True` 配置，支持直接从 ORM 数据库对象转换
    3. 响应模型里绝对不能出现 `password_hash` 这类敏感字段
    4. 可选字段标注类型为 `Optional[str]` 或者 `str | None`
"""
from pydantic import BaseModel
from datetime import datetime

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True