# 架构设计

## 核心分层思想

本项目严格按照工业界标准后端分层架构落地。按照「职责」拆分模块

①好处：

- 逻辑解耦
- 易维护
- 易测试
- 可复用



②路由层+业务服务层+数据模型层+核心配置层：

- 路由层：负责参数接收和响应返回
- 服务层：业务逻辑
- 数据模型层：数据操作通过ORM模型层完成
- 核心配置层：核心配置、鉴权、日志等通用能力

## 完整目录结构

```python
proj_fa_Blog/
├── app/                    # 应用主代码目录
│   ├── __init__.py         # 标记为Python包
│   ├── api/                # 路由层：接口入口
│   │   ├── __init__.py
│   │   ├── dependencies.py # 全局依赖（数据库会话、当前用户）
│   │   └── v1/             # 接口版本化，规范迭代
│   │       ├── __init__.py
│   │       ├── user.py     # 用户相关接口
│   │       ├── post.py     # 文章相关接口
│   │       └── comment.py  # 评论相关接口
│   ├── core/               # 核心配置层：通用基础能力
│   │   ├── __init__.py
│   │   ├── config.py       # 环境变量加载、全局配置
│   │   ├── logger.py       # 日志配置
│   │   ├── security.py     # JWT、密码哈希
│   │   └── exceptions.py   # 全局异常处理、自定义异常
│   ├── db/                 # 数据库层
│   │   ├── __init__.py
│   │   ├── base.py         # ORM基类、数据库引擎、会话工厂
│   │   └── models/         # 数据表ORM模型
│   │       ├── __init__.py
│   │       ├── user.py
│   │       ├── post.py
│   │       └── comment.py
│   ├── schemas/            # Pydantic模型：请求/响应结构校验
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   └── comment.py
│   ├── services/           # 业务服务层：核心业务逻辑
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── post_service.py
│   │   └── comment_service.py
│   └── utils/              # 通用工具函数
│       ├── __init__.py
│       └── common.py
├── alembic/                # 数据库迁移目录
├── tests/                  # 单元测试目录
│   ├── __init__.py
│   ├── conftest.py         # pytest全局fixture
│   ├── test_user.py
│   └── test_post.py
├── .env                    # 本地环境变量（不提交git）
├── .env.example            # 环境变量示例（提交git）
├── .gitignore
├── main.py                 # 项目启动入口
├── requirements.txt        # 依赖清单
└── README.md
```

```python
# 说明：接口加 v1 版本号是行业规范，后续如果接口大改版，可以新增 v2 目录，老接口不受影响，兼容更平滑。
```

## FastAPI注释固定模板

```python
@router.get("/xxx/{xxx_id}", summary="这里写简短接口名称", description="""
这里写详细描述：
业务作用、调用限制、权限要求、特殊逻辑说明
""")
def get_xxx(xxx_id: int):
    """
    一句话简述功能

    Args:
        xxx_id: 参数含义，约束条件（例：用户ID，大于0）

    Returns:
        dict: 返回数据结构说明
            {
                "id": int,
                "name": str
            }

    Raises:
        404: 资源不存在
        400: 参数非法
        401: 未登录/token失效
    """
    pass
```

```python
@router.post("/xxx/add", summary="新增xxx数据", description="""
新增一条xxx记录
校验规则：xxx字段不可为空，xxx字段长度限制；
需要登录权限
""")
def add_xxx(data: XxxSchema):
    """
    新增xxx业务数据

    Args:
        data: 请求体json，结构参考XxxSchema

    Returns:
        dict:
            code: int 状态码
            msg: str 提示信息
            data: {"id": 新增记录id}

    Raises:
        400: 参数校验失败
        401: 身份认证失败
        409: 数据重复，已存在
    """
    pass
```

```python
@router.put("/xxx/{xxx_id}", summary="更新xxx信息", description="""
根据id更新xxx，只更新传入的字段；
必须是该数据的创建人或者管理员才能修改
""")
def update_xxx(xxx_id: int, data: XxxUpdateSchema):
    """
    更新指定id的xxx数据

    Args:
        xxx_id: 需要更新的资源id
        data: 需要更新的字段

    Returns:
        dict:
            code: int
            msg: str

    Raises:
        404: 记录不存在
        403: 无修改权限
        400: 参数错误
    """
    pass
```

```python
@router.delete("/xxx/{xxx_id}", summary="删除xxx", description="""
软删除（逻辑删除，数据库标记删除状态，不物理删除）；
管理员权限
""")
def delete_xxx(xxx_id: int):
    """
    逻辑删除xxx记录

    Args:
        xxx_id: 待删除资源id

    Returns:
        dict:
            code: int
            msg: str

    Raises:
        404: 找不到记录
        403: 权限不足
    """
    pass

```

```python
1. summary 控制在 10 个字以内，不要长句
2. description 里写**业务限制、权限、是否软删除、频率限制**
3. Raises 只写这个接口真实会抛出的状态码，不要全部复制堆砌
4. 返回样例简单写结构，不用贴一大串冗余数据
5. 如果接口有查询参数（?page=1&size=10），在 Args 里一并写上
```

## Response注释样板

```python
{
  "code": 200,
  "msg": "success",
  "data": {}
}
# - `code`：业务码（不是 HTTP 状态码！可以自己定义：200 成功、400 参数错、401 未登录、403 无权限、404 不存在、500 业务异常）
# - `msg`：可读提示文字，给前端弹窗展示
# - `data`：业务载体，成功时有数据；无返回内容时为 `null`
```

```python
"""
统一返回：
Returns:
    dict: 标准响应体
        code: int, 业务状态码
        msg: str, 提示信息
        data: any, 业务数据，无数据时为null

Raises:
    内部code说明：
        400: 参数校验失败
        401: Token缺失/登录失效
        403: 权限不足
        404: 资源不存在
        500: 服务内部异常
"""

# 带 data 类型细化
"""
Args:
    xxx_id: 资源ID，大于0

Returns:
    dict: 标准统一响应
        code: int
        msg: str
        data: dict | None
            {
                "id": int,
                "name": str,
                "create_time": str
            }

Raises:
    400: 参数非法
    404: 记录不存在
    401: 未登录
"""

# data 是分页列表（list 接口专用）
"""
Args:
    page: 页码，默认1，最小1
    size: 每页数量，默认10，上限50

Returns:
    dict: 标准统一响应
        code: int
        msg: str
        data: dict | None
            {
                "total": int,       # 总条数
                "page": int,        # 当前页码
                "size": int,        # 每页大小
                "items": list[dict] # 数据列表
            }

Raises:
    400: 分页参数错误
    401: 未登录
"""

# data 为空（删除、单纯更新，不需要回传业务数据）
"""
Args:
    xxx_id: 需要删除/更新的ID

Returns:
    dict: 标准统一响应
        code: int
        msg: str
        data: None

Raises:
    404: 资源不存在
    403: 没有操作权限
"""

```

## 配套 Pydantic 响应模型注释

如果你用 `response_model`，写一个全局 Response 包裹器：

```python
'''（可选进阶，强烈建议加上，swagger 自动识别）'''
from pydantic import BaseModel
from typing import Any, Optional

class BaseResponse(BaseModel):
    code: int
    msg: str
    data: Optional[Any] = None
```

接口上声明：

```python
@router.get("/user/{user_id}", summary="获取用户详情", response_model=BaseResponse)
```

这时 docstring 里面就不用重复写外层 `code/msg`，注释可以简化，只描述 `data` 内部结构。

# 第一步：工程底座

搭建工程底座（配置 + 日志 + 数据库连接）

## 1.建目录+依赖清单

按照`完整目录结构`创建空文件夹、`__init__.py`文件。

在项目根目录新建`requirements.txt`，写入所有依赖。

```python
alembic==1.13.3
annotated-types==0.8.0
anyio==4.16.0
bcrypt==5.0.0
certifi==2026.10.23
cffi==2.1.1
click==8.5.0
colorama==0.4.6
coverage==7.17.2
cryptography==50.0.2
ecdsa==0.19.2
fastapi==0.115.0
h11==0.16.0
httpcore==1.0.9
httpx==0.27.2
idna==3.20
iniconfig==2.3.1
Mako==1.4.3
MarkupSafe==3.0.4
packaging==26.3
passlib==1.7.4
pluggy==1.7.0
pyasn1==0.6.5
pycparser==3.12
pydantic==2.14.3
pydantic-settings==2.16.2
pydantic_core==2.50.4
PyMySQL==1.1.1
pytest==8.3.3
pytest-cov==5.0.0
python-dotenv==1.2.4
python-jose==3.3.0
redis==5.2.0
rsa==4.9.1
six==1.17.0
sniffio==1.3.1
SQLAlchemy==2.0.35
starlette==0.38.6
typing-inspection==0.4.5
typing_extensions==4.16.0
uvicorn==0.30.6
```

建议项目依赖安装环境最好使用`.venv`

```
# 退出base环境
conda deactivate
# 给项目创建虚拟环境
python -m venv .venv
# 激活项目的venv环境
.venv\Scripts\Activate.ps1
```

bash执行安装

```bash
pip install -r requirements.txt
```

## 2.环境变量文件

根目录新建 `.env`，所有敏感配置、环境差异配置都放这里，不硬编码在代码里。

```python
# 服务监听地址
HOST=127.0.0.1
APP_PORT=8080
# 开发/生产环境：dev / prod
ENV=dev
DEBUG=true

# 数据库配置
DATABASE_URL=mysql + pymysql://root:123456@127.0.0.1:3306/blog_db?charset=utf8mb4

# JWT配置
SECRET_KEY=9929relentless@
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=blog.log
```

再复制一份命名为 `.env.example`，去掉真实密码密钥，作为示例模板提交到代码仓库。

```python
# ==================== 服务配置 ====================
# 服务监听地址
HOST=127.0.0.1
APP_PORT=8080
# 开发/生产环境：dev / prod
ENV=dev
DEBUG=true

# ==================== JWT 认证配置 ====================
# 【重要】部署时一定要换成随机长字符串！
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
# token 过期时间，单位分钟
ACCESS_TOKEN_EXPIRE_MINUTES=120

# ==================== 数据库 SQLAlchemy ====================
# 格式示例：mysql+pymysql://user:password@127.0.0.1:3306/blog_db
# postgres 示例：postgresql://user:password@127.0.0.1:5432/blog_db
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/blog_proj02

# ==================== 日志配置 ====================
LOG_LEVEL=INFO
LOG_FILE=blog.log
```

## 3.核心配置加载

一加载 `.env` 里的配置，用 Pydantic 做类型校验，避免手动类型转换出错。

```python
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()

class Settings(BaseModel):
    """全局配置类，自动从环境变量读取并做类型校验"""
    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    # 日志
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "blog.log")

# 全局单例，项目里直接导入使用
settings = Settings()
```

## 4.全局日志配置

封装统一的日志工具，项目所有地方共用一套日志格式、输出目标。

```python
import logging
from .config import settings

def setup_logger(name: str = "blog") -> logging.Logger:
    """初始化并返回日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出
    file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# 全局日志实例
logger = setup_logger()
```

## 5.数据库连接底座

创建 ORM 基类、数据库引擎、会话工厂，项目所有数据库操作都基于这里。

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# 1. 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 2. 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. ORM模型基类，所有数据表模型都继承它
class Base(DeclarativeBase):
    pass

# 4. 数据库会话依赖，后面接口里用Depends注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 6.项目入口

创建 FastAPI 实例，后面注册路由、全局异常都在这里挂载。

```python
from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import logger

# 创建应用实例
app = FastAPI(
    title="博客系统接口",
    version="1.0.0",
    description="基于FastAPI的标准后端博客系统"
)

@app.get("/health")
def health_check():
    """健康检查接口，验证服务是否正常"""
    logger.info("健康检查调用")
    return {"code": 0, "message": "服务运行正常", "version": "1.0.0"}
```

# 第二步：数据库层地基

## 1.编写ORM数据模型

编写三张表的 ORM 模型，三个模型文件分别放在 `app/db/models/` 目录下：`user.py`、`post.py`、`comment.py`。

前置统一规则：

1. 所有模型都继承 `app.db.base` 里的 `Base` 类
2. 用 `__tablename__` 指定数据库里的真实表名
3. 字段全部用 `Column(类型, 约束)` 定义

字段清单与约束要求：

①用户表`users`

| 字段名        | 类型              | 约束               |
| ------------- | ----------------- | ------------------ |
| id            | 整数              | 主键、自增         |
| username      | 字符串 (最长 50)  | 唯一、非空、加索引 |
| password_hash | 字符串 (最长 255) | 非空               |
| email         | 字符串 (最长 100) | 唯一、可为空       |
| is_active     | 布尔值            | 默认值 True        |
| created_at    | 时间              | 默认当前时间       |

②文章表`posts`

| 字段名     | 类型              | 约束                         |
| ---------- | ----------------- | ---------------------------- |
| id         | 整数              | 主键、自增                   |
| title      | 字符串 (最长 200) | 非空、加索引                 |
| content    | 长文本            | 非空                         |
| author_id  | 整数              | 外键关联 `users.id`、非空    |
| created_at | 时间              | 默认当前时间                 |
| updated_at | 时间              | 默认当前时间、更新时自动刷新 |

③评论表`comments`

| 字段名     | 类型              | 约束                      |
| ---------- | ----------------- | ------------------------- |
| id         | 整数              | 主键、自增                |
| content    | 字符串 (最长 500) | 非空                      |
| post_id    | 整数              | 外键关联 `posts.id`、非空 |
| author_id  | 整数              | 外键关联 `users.id`、非空 |
| created_at | 时间              | 默认当前时间              |

```
### 新手必看的踩坑提示

1. **导入路径**
   - 基类：`from app.db.base import Base`
   - 字段工具：`from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey`
   - 时间：`from datetime import datetime`
2. **时间默认值不要加括号**
写 `default=datetime.now`，不要写 `default=datetime.now()`。加了括号会在类定义时就固定死时间，不是插入数据时的当前时间。
3. **更新时间自动刷新**`updated_at` 字段要加参数 `onupdate=datetime.now`，数据更新时自动刷新时间。
4. **外键写法**`ForeignKey("表名.字段名")`，表名是数据库里的真实表名（`__tablename__` 的值），比如 `ForeignKey("users.id")`。
5. **最后一步别漏**
三个模型都写完后，在 `app/db/models/__init__.py` 里把三个模型都 import 进去，不然后面 Alembic 识别不到模型，生成不了迁移脚本。
```

## 2.导出模型

三个模型都写完后，编辑 `app/db/models/__init__.py`，把三个模型都导入进去，不然迁移工具扫描不到模型，生成不了表。

```
from app.db.models.user import User
from app.db.models.post import Post
from app.db.models.comment import Comment
```

## 3.Alembic 数据库迁移

①初始化迁移目录

在项目根目录执行命令，会自动生成 `alembic` 文件夹和配置文件：

```bash
alembic init alembic
```

②修改两个配置文件

修改 `alembic.ini`（在项目根目录下，和main.py同级）；

找到 `sqlalchemy.url` 这一行，改成你的数据库连接地址，和 `.env` 里保持一致：

```python
sqlalchemy.url = mysql+pymysql://root:123456@127.0.0.1:3306/blog_db?charset=utf8mb4
```

修改 `alembic/env.py`；

找到 `target_metadata` 相关的代码，改成导入我们的 `Base` 元数据，这样 Alembic 才能自动对比模型和数据表的差异：

```python
from app.db.base import Base  # 导入我们的ORM基类
target_metadata = Base.metadata
```

> 提示：文件里原本有 `target_metadata = None`，把它替换成上面的写法。

③生成首次迁移脚本

执行命令，自动对比模型和数据库，生成建表的迁移脚本：

```bash
alembic revision --autogenerate -m "init tables"
```

执行成功后，去 `alembic/versions/` 目录下能看到生成的迁移文件，打开可以看到自动生成的建表语句。

④执行迁移，数据库建表

```bash
alembic upgrade head
```

执行完成后，去 MySQL 里查看，就能看到 `users`、`posts`、`comments` 三张表已经创建好了。

# 第三步：结构校验层

schemas 层、它和数据库 ORM 模型不是一回事，职责完全不同：

- **ORM 模型（db/models）**：对应数据库里的表，描述数据怎么存
- **Pydantic 模型（schemas）**：对应接口的输入输出，描述接口收什么、返回什么
  - 请求模型：自动校验入参，字段缺了、类型错了直接报错，不用手动写判断
  - 响应模型：统一返回格式，自动过滤敏感字段（比如密码哈希绝对不能返回给前端）

> 项目采用 ORM 模型和 Pydantic 模型分离的设计：数据层模型对应数据库表结构，接口层模型对应请求响应结构。既保证了数据校验和输出格式统一，也避免了数据库敏感字段泄露到接口返回中。

------

## 1.编写请求/响应模型

三个文件分别放在 `app/schemas/` 目录下：`user.py`、`post.py`、`comment.py`。

统一规则：

1. 所有模型都继承 `pydantic.BaseModel`
2. **响应模型必须加** `from_attributes = True` 配置，支持直接从 ORM 数据库对象转换
3. 响应模型里绝对不能出现 `password_hash` 这类敏感字段
4. 可选字段标注类型为 `Optional[str]` 或者 `str | None`

------

①用户模块 `user.py`

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

------

②文章模块 `post.py`

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

------

③评论模块 `comment.py`

请求模型：CommentCreate（发布评论用）

- `content`：字符串，必填
- `post_id`：整数，必填

响应模型：CommentResponse（返回评论用）

- `id`：整数
- `content`：字符串
- `post_id`：整数
- `author_id`：整数
- `created_at`：时间

------

小提示

- 导入：`from pydantic import BaseModel`，时间类型用 `datetime.datetime`，可选类型用 `Optional` 或者 `| None`

- 响应模型的 Config 写法：

  ```
  class Config:
      from_attributes = True
  ```

  这个配置的作用是：允许直接把数据库查出来的 ORM 对象，自动转成 Pydantic 响应模型，不用手动一个个字段赋值。

## 2.核心安全工具

属于 core 核心层的系统级基础设施，是整个鉴权体系的底层底座，负责密码安全处理和 JWT 令牌管理，所有登录、鉴权逻辑都依赖它。

```markdown
依赖项：

- 全局配置 `settings`
- `passlib`：密码哈希加密
- `python-jose`：JWT 生成与校验
- 时间处理相关工具
-----------------------------------------------------
**Argon2 是现在业界首选的密码哈希算法（Memory-Hard 内存困难函数），是 2015 密码哈希大赛的冠军，OWASP 推荐首选，用来存用户密码，代替老旧的 bcrypt、md5、sha256**argon2-cff...。

> 
> 重点区分：
> SHA256 只是摘要，**不能直接存密码**，GPU 一秒跑几十亿次爆破；
> Argon2 故意设计成**吃内存 + 吃CPU**，GPU/ASIC 爆破成本极高，很难跑字典暴力破解。

## 三个版本（你只用记 Argon2id）
1. **Argon2d**：依赖数据访问内存，抗 GPU 强，但是容易受计时侧信道攻击 → 适合挖矿，**不适合网站密码**
2. **Argon2i**：不依赖数据访问，防侧信道，但是抗 GPU 弱一点
3. **Argon2id（你现在用的）**：前半段 i、后半段 d，两者优点合并，**Web 后端、登录系统标准选择**，RFC9106 标准推荐IETF

## 它有 3 个可调参数（你哈希串里那串数字就是）
拿你这条举例：
`$argon2id$v=19$m=65536,t=3,p=4$...`

- `m=65536`：内存成本，单位 KB → 这里是 64MB
- `t=3`：迭代次数（时间成本）
- `p=4`：并行度、线程数

上线的时候，你可以根据服务器性能调高，越慢越安全；开发环境用默认值就行。

## 和你之前纠结的 bcrypt 对比
- bcrypt：老经典，有 72 字节硬上限（就是我们刚才踩坑的根源！）、参数调节空间小
- Argon2id：无 72 字节限制、可自由调内存 / 时间、安全性更强，现在新项目优先选它

## 工作流程（和你代码对应）
1. 用户输入密码 `123456`
2. argon2 自动**生成随机盐**（不用你自己管）
3. 按照 m/t/p 参数做大量内存计算
4. 返回一串包含：算法版本、参数、盐、哈希结果的字符串
5. 校验的时候：把明文 + 同一份盐，跑一遍同样计算，对比结果，**不会反向解密**

> 
> 哈希≠加密：**不能解密回原始密码，只能比对**。

## 你项目里的好处
✅ 不再被 72 字节卡死，用户随便输长密码、中文密码
✅ 现代标准，安全等级高于 bcrypt
✅ passlib/argon2-cffi 库封装好，代码极简
```

```python
from app.core.config import settings
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

#密码上下文，bcrypt算法使用
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 新版的底层 bcrypt 库，**不再自动静默截断，超过 72 字节直接抛错**; plain_password.encode("utf-8")[:72]
# passlib 拿到 bytes 之后，**它内部又会再做一次 utf-8 编码**！
# `b"123456"` 再 utf8 编码一遍，直接变成更长的字节流，触发 72 字节限制！

# ✅ 方案 B（最简单，直接换成 argon2，不用处理长度，新项目首选）
"""
    hash_password(plain_password: str) -> str
    - 作用：将明文密码转为不可逆的哈希字符串，用户注册时使用
    - 提示：使用 bcrypt 算法，初始化全局密码上下文
"""
# def hash_password(plain_password: str) -> str:
#     plain_bytes = plain_password.encode("utf-8")[:72]
#     return pwd_context.hash(plain_bytes)
def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

"""
    verify_password(plain_password: str, hashed_password: str) -> bool
    - 作用：比对明文密码和数据库中的哈希值是否一致，用户登录时校验使用
"""
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     plain_bytes = plain_password.encode("utf-8")[:72]
#     return pwd_context.verify(plain_bytes, hashed_password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

"""
    create_access_token(data: dict) -> str
    - 作用：生成 JWT 访问令牌，登录成功后颁发给客户端
    - 关键逻辑：
      - 拷贝传入的数据，追加 `exp` 过期时间（当前时间 + 配置的有效期分钟数）
      - 使用配置中的密钥和 HS256 算法签名生成令牌
      - 标准用法：`data` 里传入 `{"sub": "用户ID字符串"}`，`sub` 是 JWT 标准的主体字段
"""
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # 设置过期时间
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # 生成签名token
    encoded_jwt = jwt.encode(to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

"""
    decode_access_token(token: str) -> int | None
    - 作用：解析校验令牌，有效则返回用户 ID，失效 / 篡改则返回 None
    - 关键逻辑：
      - 用同一密钥和算法解码，自动校验签名和过期时间
      - 捕获所有 `JWTError` 异常，统一返回 None
      - 从载荷中取出 `sub` 字段，转成整数用户 ID 返回
"""
def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        else:
            return user_id
    except JWTError:
        return None
```

# 第四步：用户业务服务

属于 services 业务服务层，承上启下：向上被接口层调用，向下操作数据库；所有用户相关的业务逻辑都封装在这里，接口层不直接写业务逻辑。

```markdown
### 依赖项
- 数据库会话 `Session`
- 用户 ORM 模型 `User`
- 用户请求模型 `UserCreate`
- 安全工具里的密码哈希、校验函数
--------------------------------------------------------------------

### 需要实现的 3 个核心函数
1. **`get_user_by_username(db: Session, username: str) -> User | None`**
   - 作用：根据用户名查询用户对象
   - 用途：注册时查重、登录时查询用户
2. **`create_user(db: Session, user_in: UserCreate) -> User | None`**
   - 作用：创建新用户
   - 业务流程：
     1. 先查询用户名是否已存在，存在则返回 None
     2. 将传入的明文密码转为哈希值
     3. 创建 User 数据库对象，加入会话、提交、刷新后返回
   - 注意：数据库存储的是 `password_hash`，不是明文 password
3. **`authenticate_user(db: Session, username: str, password: str) -> User | None`**
   - 作用：校验用户名密码是否正确，登录专用
   - 业务流程：
     1. 先按用户名查用户，不存在直接返回 None
     2. 用户存在则校验密码，密码错误返回 None
     3. 都正确则返回用户对象

### 分层规则提醒
- 服务层只处理业务逻辑，不抛 HTTP 异常、不处理请求参数
- 异常、状态码统一放到接口层处理，服务层用返回值（None / 对象）表示结果
```



# 启动项目

### ✅ 开发环境（带热重载，日常就用这个）

```
uvicorn main:app --reload --port 8080
```

- `main`：main.py 文件
- `app`：文件里 `app = FastAPI()` 这个实例
- `--reload`：改代码自动重启（开发用，线上不要开）
- `--port 8080`：指定端口8080，就是你之前配置的端口，不加默认8000

如果要允许别的设备访问：

```
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### ✅ 如果你main.py里面写了启动代码（if **name** == "**main**"）

直接：

```
python main.py
```

### ✅ 线上正式启动（不要--reload）

```
uvicorn main:app --host 0.0.0.0 --port 8080
```

> ⚠️ 前提：先激活 `.venv`，uvicorn已经装好 访问文档地址： http://127.0.0.1:8080/docs



# Schema

![](D:\A_PythonAI\Coding_my\blog_fastapi\docs\images\schemas01.png)

先说重点：**这个不是bug，删不掉，只能默认折叠起来眼不见为净** 只要你的接口带参数校验（Query、Path、Pydantic模型），FastAPI自动注入这两个422错误Schema，代码层面没法直接移除定义。

## 方案

打开文档的时候自动折叠Schemas栏（推荐，一行配置搞定）

在你初始化 `FastAPI` 的地方加上 `swagger_ui_parameters`：

```python
app = FastAPI(
    title="博客系统接口",
    version="v1.0.0",
    description="基于FastAPI标准后端博客系统",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 0  # 0 = Schemas默认收起
    }
)
```

改完重启服务，刷新 `/docs` 👉 Schemas 板块默认就是收起来的，不挡你的视线，要用的时候再点开看。

------

## Schema区别

- `HTTPValidationError`：是**返回给前端**的422响应结构（接口抛出去的）
- `ValidationError`：是Pydantic内部用的校验异常结构

> ❌ 网上有些偏方想彻底删掉它，非常麻烦，还要改OpenAPI原始字典，不适合你现在练项目，容易把文档搞崩。



# 排错技巧

## 核心技巧

warning 和 error 根本不是一回事

```python
# Warning（警告）：黄色 / 白色，完全不用管
终端里一大堆的 `WARNING`、`DeprecationWarning`、`UserWarning`，全部都是**警告**，意思是「这么写不太规范 / 未来版本可能变，但现在不影响运行」。

# Error（错误）：一般带红色高亮，才是你要找的
只有出现 `Error` 结尾的关键词、`Traceback (most recent call last)` 这句话，才是**真正导致程序崩、服务起不来的致命错误**。
你所有的排错注意力，只需要放在这一块，其他全部跳过。
```

报错从下往上看，别从上往下读

```bash
# 标准报错结构（固定套路）

Traceback (most recent call last):
  File "xxx/xxx/库文件.py", line 123, in 某个函数
    ...（库里面的代码堆栈，不用看）
  File "app/core/config.py", line 15, in <module>
    SECRET_KEY = settings.SECRET_KEY
NameError: name 'settings' is not defined

#### 你只需要看三行，其他全部跳过：
1. **最底部一行：错误类型 + 原因**
比如 `NameError: name 'settings' is not defined`
直接告诉你：这是变量名错误，`settings` 这个名字没定义，大概率是拼错了、或者忘了导入。

2. **往上找第一个「你自己写的文件」**
堆栈里会列很多文件路径，大部分是第三方库的，不用看。
找到第一个路径里带 `app/`、`main.py` 的，就是你自己写的代码出错的地方，后面会标清楚第几行。
比如上面的 `File "app/core/config.py", line 15`，就是你写的 config.py 第 15 行出的问题。

3. **对应到那一行代码，检查拼写、导入、语法**
90% 的低级错误，到这一步就解决了：变量名拼错、导入路径写错、少写个括号、漏了冒号。
```

关键词定位

```python
### 导入 / 路径类错误
**关键词**：`ModuleNotFoundError: No module named 'xxx'`
**直接排查三个点**：

- 是不是文件名 / 模块名拼错了（比如把 `uvicorn` 写成 `unicorn`）
- 是不是执行命令的目录不对，不在项目根目录，识别不到 `app` 包
- 是不是导入路径写错了，比如相对导入用乱了、绝对导入层级不对


### 2. 名字 / 属性拼错类错误
**关键词 1**：`NameError: name 'xxx' is not defined`
→ 变量名 / 函数名拼错了，或者忘了导入这个变量。

**关键词 2**：`AttributeError: 'xxx' object has no attribute 'yyy'`
→ 对象的属性名拼错了，比如把 `settings.DATABASE_URL` 写成了 `settings.DATABSE_URL`，少了一个字母。
```

# GitHub提交示例

> 前提：电脑已经装好了 git，并且在 GitHub 网页登录账号

## GitHub 创建仓库

1. 打开 github.com，右上角点 **+ → New repository**

2. 填写信息：

   - Repository name：`proj_fa_Blog`（和你本地文件夹同名，方便管理）

   - Description（可选）：FastAPI博客后端项目

   - ✅ Public（公开仓库，免费） / Private私有

   - ❗**不要勾选：Add a README file、Add .gitignore、Choose a license**

     > 重点！如果你勾了，后面推送会报冲突，咱们本地自己初始化

3. 点 `Create repository`

4. 创建成功页面，复制 HTTPS 地址，类似： `[https://github.com/](https://github.com/)你的用户名/proj_fa_Blog.git`

## 本地终端操作

> 确认：终端路径是项目根目录，里面能看到 app、.venv、requirements.txt

1. 初始化git（只执行一次）

```
git init
```

1. 创建 `.gitignore`（Python项目必备！**不要把.venv、缓存、环境变量提交上去**） 在项目根新建文件，名字 `.gitignore`，粘贴下面内容：

```
# 虚拟环境
.venv/
venv/
env/

# 环境变量
.env

# python缓存
__pycache__/
*.pyc
*.pyo
*.pyd

# 日志
logs/
*.log

# 数据库
*.db
*.sqlite3

# pycharm配置文件夹
.idea/

# 测试、打包
.pytest_cache/
htmlcov/
dist/
build/
```

1. 把所有文件加入暂存

```
git add .
```

> `git add .` = 添加当前目录全部文件，.gitignore里面写的会自动跳过，不会上传

1. 第一次提交（初始化commit）

```
git commit -m "init: 初始化fastapi博客项目，基础结构、配置、依赖"
```

> `-m` 后面是提交说明，规范一点写，以后好找版本

1. 绑定远程github仓库地址（换成你刚才复制的链接）

```
git remote add origin [https://github.com/](https://github.com/)你的用户名/proj_fa_Blog.git
```

1. 推送到github远程主分支

```
git push -u origin main
```

> 旧版本仓库默认分支叫master，如果main报错，换成 `git push -u origin master`

### 第一次推送弹窗验证

第一次推送会弹出登录：

- HTTPS方式：现在**不支持密码登录**，需要去github生成 **Personal access token（token）** 教程简版： GitHub头像 → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token 勾选 `repo` 权限，生成，复制token，弹窗密码位置粘贴这个token。

### ✅ 后续日常提交

```
git add .
git commit -m "feat: 新增xxx接口"
git push
```

### 📌 规范提交注释模板

- `init:` 项目初始化
- `feat:` 新增功能、新增接口
- `fix:` 修复bug
- `refactor:` 代码重构，不改功能
- `docs:` 修改注释、文档
- `chore:` 调整依赖、配置

### ⚠️ 高频踩坑提醒

1. **绝对不要提交 .venv 文件夹、.env 文件**（里面有数据库密码、JWT密钥！），.gitignore已经帮你过滤
2. 如果你刚才建仓库时手滑勾选了README，推送会报错：

```
git pull origin main --rebase
```

​		拉取远程readme合并之后再push 

3. PyCharm自带Git图形化：右侧Git面板，也可以点按钮add/commit/push，不用敲命令

# Gitee提交示例

> 优势：国内访问快；逻辑和GitHub大体一致，但是验证、界面有区别。 前提：已经注册登录 gitee.com，本地装好git，终端在项目根目录 `D:\proj_fa_Blog`

## Gitee新建仓库

1. 登录 gitee.com，右上角 **+ → 新建仓库**

2. 填写表单：

   - 仓库名称：`proj_fa_Blog`（和本地文件夹同名，推荐）
   - 仓库介绍：FastAPI博客后端项目
   - 仓库类型：**公开 / 私有**（私有免费）
   - ✅ 初始化仓库：**不要勾选 README、.gitignore、开源许可证**（重点！避免后续冲突）

3. 点击「创建」

4. 创建成功页面，复制仓库地址，选 HTTPS：

   ```
   [https://gitee.com/](https://gitee.com/)你的用户名/proj_fa_Blog.git
   ```

## 本地终端

（PyCharm Terminal）执行命令

> 确认路径是项目根目录，能看到 app 文件夹、requirements.txt、.env

### git初始化（只跑一次）

```
git init
```

在项目根新建 `.gitignore` 文件（Python FastAPI专用，直接复制下面内容）

```
# 虚拟环境，禁止上传
.venv/
venv/
env/

# 私密环境变量（数据库、密钥！非常重要）
.env

# Python缓存
__pycache__/
*.pyc
*.pyo
*.pyd

# 日志文件
logs/
*.log

# 数据库文件
*.db
*.sqlite3

# PyCharm配置
.idea/

# pytest测试缓存
.pytest_cache/
htmlcov/

# 打包产物
dist/
build/
*.egg-info
```

添加全部文件到暂存区（.gitignore里的内容会自动忽略不上传）

```
git add .
```

本地第一次提交

```
git commit -m "init: 初始化fastapi博客项目，基础目录结构、配置、依赖"
```

绑定远程Gitee仓库（链接换成你刚才复制的）

```
git remote add origin [https://gitee.com/](https://gitee.com/)你的用户名/proj_fa_Blog.git
```

推送到Gitee远程

```
git push -u origin master
```

> ⚠️ Gitee 默认主分支名字是 **master**（不是github的main！这个是最容易踩坑的点）

### 第一次推送账号验证

（HTTPS方式）

执行push之后弹出账号密码输入框：

- 用户名：你的Gitee账号
- 密码：**不是登录密码！！Gitee现在推送需要【私人令牌】**

生成Gitee私人令牌步骤：

1. Gitee右上角头像 → 设置 → 安全设置 → **私人令牌**
2. 点击「生成新令牌」
3. 描述：`git推送代码`
4. 权限勾选：`projects`（仓库读写权限，必选）
5. 提交，**复制生成的token（只显示一次，保存好）**
6. 弹窗密码位置，粘贴这个token

### ✅ 后续日常提交

```
git add .
git commit -m "feat: 新增xxx接口"
git push
```

提交注释规范：

- `init:` 项目初始化
- `feat:` 新增接口/功能
- `fix:` 修复bug
- `refactor:` 重构代码，功能不变
- `docs:` 更新注释文档
- `chore:` 修改依赖、配置

### 📌 高频踩坑清单

1. 分支名字：Gitee默认 `master`，不要写成main，否则推送失败
2. ❌ 严禁提交 `.env`，里面存数据库密码、JWT密钥，泄露非常危险，.gitignore已经屏蔽
3. 如果建仓库时不小心勾选了README，推送会报错，先执行这句拉取合并：

```
git pull origin master --rebase
```

再执行 push

PyCharm图形化操作：右侧Git面板，也可以图形化 add / commit / push，不用敲命令

# 同时推送Gitee、GitHub

## 1.先配置（只做一次）

```bash
#先绑定gitee的ssh地址到origin的推送url
git remote add origin git@gitee.com:你的名字/xxx.git

#追加github的ssh地址到origin的推送url
git remote set-url --add origin git@github.com:你的名字/你的仓库.git
```

✅ 切换dev分支：

```bash
git checkout dev
```

## 2.提交代码到本地仓库

```bash
git add .
git commit -m "feat:新增XX功能"
```

场景1：commit之后，你**又改了文件，想把新修改塞进刚才这一次commit里**

这时候才需要 add + 追加提交：

```
git add .
git commit --amend --no-edit
```

- `--amend`：修改上一次commit，把新加的文件合并进去

- `--no-edit`：**不修改commit备注，继续用 "提交README"**

  > ⚠️ 注意：如果这个commit已经推到远程了，千万别amend！现在还没push，随便用没问题。

场景2：你又改了文件，想做成**新的一次commit（保留N条记录）**

那就正常走：

```
git add .
git commit -m "补充xxx内容"
```

## 3.推送到远程仓库

> 这一句**同时推Gitee + GitHub**
>
> `-u`：建立本地 dev 和远程 origin/dev 的追踪关系，**只第一次用**，之后就可以简写 `git push`

```bash
#第一次推送dev
git push -u origin dev
```

查看是否配置成功：

```bash
git remote -v
```

你会看到 origin 有两行 push 地址

```
origin  git@gitee.com:xxx/xxx.git (fetch)
origin  git@gitee.com:xxx/xxx.git (push)
origin  git@github.com:xxx/xxx.git (push)
```

## 查看状态

看看有没有红色未跟踪 / 修改文件

```
git status
```

- 如果输出：`nothing to commit, working tree clean` 👉 说明工作区干净，直接 `git push` 就把刚才【提交README】这条记录推到Gitee+GitHub

## 4.配置同时推送

配置both分组：

```bash
git config remotes.both "github origin"
```

配置完，再校验一下：

```bash
git config --list | Select-String remotes
```

之后一键推送命令：

```bash
git push both dev
```

这条命令等价于依次执行：

```bash
git push github dev
git push origin dev
```

补充：

- 以后切到 main 分支，就 `git push both main`

- 如果哪天想删掉这个分组：

- ```bash
  git config --unset remotes.both
  ```


# git操作

## commit type

常用 type：

- feat：新增可对外使用的功能（接口）
- refactor：重构 / 搭建基础代码结构，不新增可运行功能
- fix：修复 bug
- docs：文档
- chore：依赖、gitignore、配置文件这类杂活

```bash
# ✅ 推荐
git commit -m "feat(schemas): 新增用户模块请求响应模型"

# ✅ 更严谨一点（纯结构、还没写接口逻辑）
git commit -m "refactor(schemas): 编写用户schema请求响应模型"
```

# 问题记录

## 1. 创建Class还是Function？

✅ 选 Class：

- 多个方法共用一堆内部变量
- 语义上是一个独立组件（日志器、数据库管理、缓存管理、权限校验器）
- 需要继承扩展

✅ 选 函数：

- 纯转换、计算工具（加密、格式化）
- 工厂获取实例（get_db、get_redis，FastAPI Depends 最常用）
- 只有一两行逻辑，写类纯属增加代码量

## 2. alembic建表迁徙脚本

1.生成建表的迁徙脚本命令不成功？

运行`alembic revision --autogenerate -m "init tables"`命令，无法成功生成建表迁徙脚本；

注意：.env文件中的`mysql+pymysql://root:XXX@127.0.0.1:XXX/blog_db?charset=utf8mb4`格式不对；`mysql + pymysql`之间需要去掉空格； 修改.env文件需要重启项目。

## 3. 新版bcrypt库不支持自动静默截断

找到了根源！现在新版的底层bcrypt库，**不再自动静默截断，超过72字节直接抛错**。 哪怕你传的是很短的`123456`，你现在的写法：

```
plain_bytes = plain_password.encode("utf-8")[:72]
return pwd_context.hash(plain_bytes)
```

❌ 问题：传给 `pwd_context.hash` 的是 **bytes**，passlib拿到bytes之后，**它内部又会再做一次utf-8编码**！ `b"123456"` 再utf8编码一遍，直接变成更长的字节流，触发72字节限制！

✅ 正确方案A（推荐，bcrypt+sha256，行业标准绕过72字节限制） 不用手动切字节，先sha256摘要，再丢给bcrypt，完美解决长度限制，而且安全：

```
import hashlib
import base64

def hash_password(plain_password: str) -> str:
    # 先sha256，再base64，输出永远固定长度，不会超72字节
    raw = hashlib.sha256(plain_password.encode("utf-8")).digest()
    safe_pw = base64.b64encode(raw).decode("utf-8")
    return pwd_context.hash(safe_pw)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    raw = hashlib.sha256(plain_password.encode("utf-8")).digest()
    safe_pw = base64.b64encode(raw).decode("utf-8")
    return pwd_context.verify(safe_pw, hashed_password)
```

✅ 方案B（最简单，直接换成argon2，不用处理长度，新项目首选）

1. 安装

```
pip install argon2-cffi
```

1. 修改pwd_context

```
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
```

1. 函数变回原版，干净清爽：

```
def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

## 4. pyjwt 新版本参数名字改变

pyjwt 新版本参数名字变了： 老版本：`secret_key=` 新版本：**`key=`**

```python
# 原来（报错）
encoded_jwt = jwt.encode(to_encode, secret_key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# 改成
encoded_jwt = jwt.encode(to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

## 5. `datetime.utcnow()` 被弃用

```python
# 旧
expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
# 新
expire = datetime.now(datetime.UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
```

## 6. `datetime.UTC`

> 报错根源：`datetime.UTC` = 3.12新增常量；你当前Python版本 ≤3.11，识别不到。

方案1｜标准兼容写法（生产首选，无警告、全版本兼容，推荐你直接用）

导入 `timezone`，用 `timezone.utc`，这是官方在3.12之前的标准UTC对象，**3.8~3.11、3.12+全都能跑**

```
# 顶部导入
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

✅ 优点：

- 没有弃用警告
- 时区感知datetime（JWT的exp校验严格要求时区感知，**utnow()是无时区，有安全隐患**）
- 不用升级Python，不改环境 ❌ 缺点：就多导入一个 `timezone`，几乎没代价

