# FastAPI 博客后端项目开发手册

## 一、架构设计

### 1.1 核心分层思想

本项目严格按照工业界标准后端分层架构落地，按「职责」拆分模块，实现逻辑解耦、易维护、易测试、可复用。

**分层单向依赖规则**：只能上层导入下层，下层禁止反向导入上层，避免循环依赖，保证架构清晰。 层级从低到高：

- **core 核心层**：系统级基础设施，包含全局配置、日志、鉴权、异常处理，是项目运行的地基
- **db 数据库层**：ORM 表模型、数据库连接、会话管理，描述数据如何存储
- **schemas 结构层**：Pydantic 请求/响应模型，描述接口收什么、返回什么，自动做参数校验
- **services 业务服务层**：封装核心业务逻辑，承上启下，可被多接口复用
- **api 路由层**：接口入口，仅负责接收参数、返回响应、处理 HTTP 状态码

### 1.2 完整目录结构

```
proj_fa_Blog/
├── app/                     # 应用主代码目录
│   ├── __init__.py          # 标记为 Python 包
│   ├── api/                 # 路由层：接口入口
│   │   ├── __init__.py
│   │   ├── dependencies.py  # 全局通用依赖（鉴权、数据库会话）
│   │   └── v1/              # v1 版本业务接口
│   │       ├── __init__.py
│   │       ├── user.py      # 用户模块接口
│   │       ├── post.py      # 文章模块接口
│   │       └── comment.py   # 评论模块接口
│   ├── core/                # 核心基础设施层
│   │   ├── __init__.py
│   │   ├── config.py        # 全局配置加载
│   │   ├── logger.py        # 统一日志配置
│   │   ├── security.py      # 密码哈希、JWT 令牌管理
│   │   └── exceptions.py    # 全局异常处理
│   ├── db/                  # 数据库层
│   │   ├── __init__.py
│   │   ├── base.py          # ORM 基类、引擎、会话工厂
│   │   └── models/          # 数据表 ORM 模型
│   │       ├── __init__.py
│   │       ├── user.py
│   │       ├── post.py
│   │       └── comment.py
│   ├── schemas/             # 结构校验层：请求/响应模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   └── comment.py
│   ├── services/            # 业务服务层：核心业务逻辑
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── post_service.py
│   │   └── comment_service.py
│   └── utils/               # 工具层：通用辅助函数
│       ├── __init__.py
│       └── common.py
├── alembic/                 # 数据库迁移目录
├── tests/                   # 单元测试目录
│   ├── __init__.py
│   └── conftest.py          # pytest 全局 fixture
├── docs/                    # 项目文档与资源
├── .env                     # 本地环境变量（不提交代码仓库）
├── .env.example             # 环境变量示例模板（提交仓库）
├── .gitignore               # Git 提交忽略规则
├── main.py                  # 项目启动入口
├── requirements.txt         # 第三方依赖清单
└── README.md                # 项目说明文档
```

> 接口采用 v1 版本化管理是行业通用规范，后续接口大改版可新增 v2 目录，老接口不受影响，迭代更平滑。

### 1.3 技术栈

| 类别       | 技术选型                             | 说明                                            |
| ---------- | ------------------------------------ | ----------------------------------------------- |
| Web 框架   | FastAPI + Uvicorn                    | 高性能 ASGI 后端框架 + 运行服务器               |
| ORM 框架   | SQLAlchemy 2.0                       | 数据库对象关系映射                              |
| 数据库     | MySQL + PyMySQL                      | 关系型数据库 + Python 驱动                      |
| 数据库迁移 | Alembic                              | 自动对比模型差异，生成/执行迁移脚本             |
| 参数校验   | Pydantic                             | 自动校验请求响应格式，过滤敏感字段              |
| 安全鉴权   | JWT（python-jose） + Argon2 密码哈希 | 行业标准鉴权方案，Argon2 为当前密码哈希首选算法 |
| 配置管理   | python-dotenv                        | 环境变量抽离，敏感配置不硬编码                  |
| 单元测试   | Pytest + pytest-cov                  | 自动化测试 + 覆盖率统计                         |

## 二、快速启动

### 2.1 环境要求

- Python 3.10 ~ 3.11（稳定兼容全量依赖）
- MySQL 5.7+ / 8.0+（提前创建空数据库 `blog_db`）
- 推荐使用项目独立虚拟环境，避免依赖混乱

### 2.2 安装依赖

```
# 创建虚拟环境
python -m venv .venv

# Windows PowerShell 激活虚拟环境
.venv\Scripts\Activate.ps1

# 安装全部依赖
pip install -r requirements.txt
```

`requirements.txt` 核心依赖清单：

```
# Web 框架与运行服务器
fastapi==0.115.0
uvicorn==0.30.6
python-multipart==0.0.33

# 数据库相关
sqlalchemy==2.0.35
pymysql==1.1.1
alembic==1.13.3

# 安全鉴权
python-jose==3.3.0
passlib==1.7.4
argon2-cffi==25.1.0

# 配置与工具
python-dotenv==1.2.4
redis==5.2.0

# 测试相关
pytest==8.3.3
pytest-cov==5.0.0
```

### 2.3 配置环境变量

复制 `.env.example` 为 `.env`，填入对应配置：

```
# 服务配置
HOST=127.0.0.1
APP_PORT=8080
ENV=dev
DEBUG=true

# JWT 鉴权配置（部署时务必替换为随机长字符串）
SECRET_KEY=your-custom-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# 数据库连接地址
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/blog_db?charset=utf8mb4

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=blog.log
```

> ⚠️ 注意：`mysql+pymysql` 中间不能有空格，否则会连接失败。

### 2.4 数据库迁移

```
# 生成迁移脚本
alembic revision --autogenerate -m "init tables"

# 执行迁移，创建数据表
alembic upgrade head
```

### 2.5 启动服务

```
# 开发环境（热重载，推荐日常调试）
uvicorn main:app --reload --port 8080

# 生产环境（无热重载、对外访问）
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

### 2.6 访问接口文档

- 交互式调试文档：http://127.0.0.1:8080/docs
- OpenAPI 规范：http://127.0.0.1:8080/openapi.json

## 三、分步开发指南

### 第一步：工程底座搭建

目标：搭建分层目录结构、完成底层基础设施，跑通服务启动与健康检查。

#### 1.1 创建目录与依赖清单

1. 按 1.2 的目录结构创建所有文件夹与 `__init__.py` 标记文件
2. 在 `requirements.txt` 中写入全部第三方依赖
3. 创建 `.env` 与 `.env.example` 环境变量文件

#### 1.2 全局配置加载 `app/core/config.py`

统一加载环境变量，Pydantic 自动做类型校验，全局单例使用。

```
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()


class Settings(BaseModel):
    """全局配置类，自动从环境变量读取并做类型校验"""
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "blog.log")


# 全局单例，项目其他地方直接导入使用
settings = Settings()
```

#### 1.3 全局日志配置 `app/core/logger.py`

全项目共用一套日志格式与输出渠道。

```
import logging
from .config import settings


def setup_logger(name: str = "blog") -> logging.Logger:
    """初始化并返回统一配置的日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    # 避免重复添加 handler 导致日志重复
    if logger.handlers:
        return logger
    
    # 统一日志格式
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

#### 1.4 数据库连接底座 `app/db/base.py`

创建引擎、会话工厂、ORM 基类、会话依赖。

```
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

# 3. ORM 基类，所有数据表模型继承它
class Base(DeclarativeBase):
    pass


# 4. 数据库会话依赖，接口中通过 Depends 注入使用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### 1.5 v1 版本总路由 `app/api/v1/__init__.py`

汇总业务模块路由，统一加版本前缀。

```
from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# 后续写完子模块路由后在此注册
# api_router.include_router(user.router, prefix="/users", tags=["用户模块"])
# api_router.include_router(post.router, prefix="/posts", tags=["文章模块"])
# api_router.include_router(comment.router, prefix="/comments", tags=["评论模块"])
```

#### 1.6 项目入口 `main.py`

创建 FastAPI 应用，挂载路由，提供健康检查。

```
from fastapi import FastAPI
from app.core.logger import logger
from app.api.v1 import api_router

app = FastAPI(
    title="博客系统接口",
    version="1.0.0",
    description="基于FastAPI的标准后端博客系统",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 0  # 接口文档Schemas默认收起
    }
)

# 挂载 v1 版本总路由
app.include_router(api_router)


@app.get("/health", summary="健康检查")
def health_check():
    """服务探活接口，验证服务是否正常运行"""
    logger.info("健康检查接口被调用")
    return {"code": 0, "message": "服务运行正常", "version": "1.0.0"}
```

------

### 第二步：数据库层落地

目标：完成 ORM 数据模型编写，通过 Alembic 迁移在数据库创建对应数据表。

#### 2.1 编写 ORM 数据模型

三个模型文件位于 `app/db/models/`，全部继承 `Base` 类，用 `__tablename__` 指定真实表名。

**统一规则**：

- 时间默认值写 `default=datetime.now`，不加括号，避免类定义时固定时间
- 更新时间加 `onupdate=datetime.now`，数据更新时自动刷新
- 外键写法：`ForeignKey("表名.字段名")`，使用数据库真实表名

##### 用户表 `app/db/models/user.py`

```
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
```

##### 文章表 `app/db/models/post.py`

```
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.db.base import Base
from datetime import datetime


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

##### 评论表 `app/db/models/comment.py`

```
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base import Base
from datetime import datetime


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
```

#### 2.2 导出模型

编辑 `app/db/models/__init__.py`，统一导出所有模型，供 Alembic 扫描识别。

```
from app.db.models.user import User
from app.db.models.post import Post
from app.db.models.comment import Comment
```

#### 2.3 Alembic 数据库迁移

1. **初始化迁移工具**

   ```
   alembic init alembic
   ```

2. **修改配置文件**

   - `alembic.ini`：修改 `sqlalchemy.url` 为数据库连接地址

   - `alembic/env.py`：替换 `target_metadata` 为项目 ORM 元数据

     ```
     from app.db.base import Base
     target_metadata = Base.metadata
     ```

3. **生成迁移脚本**

   ```
   alembic revision --autogenerate -m "init tables"
   ```

4. **执行迁移建表**

   ```
   alembic upgrade head
   ```

------

### 第三步：结构校验层（Schemas）

#### 3.1 分层意义

- **ORM 模型（db/models）**：对应数据库表，描述数据怎么存
- **Pydantic 模型（schemas）**：对应接口输入输出，描述接口收什么、返什么
  - 请求模型：自动校验入参，字段缺失、类型错误直接报错
  - 响应模型：统一返回格式，自动过滤敏感字段（如密码哈希）

#### 3.2 统一编写规则

1. 所有模型继承 `pydantic.BaseModel`
2. 响应模型配置 `class Config: from_attributes = True`，支持直接从 ORM 对象转换
3. 响应模型禁止出现 `password_hash` 等敏感字段
4. 可选字段标注 `Optional[类型]` 或 `类型 | None`

#### 3.3 各模块模型实现

##### 用户模块 `app/schemas/user.py`

```
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """用户注册请求模型"""
    username: str
    password: str
    email: Optional[str] = None


class UserResponse(BaseModel):
    """用户信息响应模型，自动过滤敏感字段"""
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

##### 文章模块 `app/schemas/post.py`

```
from pydantic import BaseModel
from datetime import datetime


class PostCreate(BaseModel):
    """发布文章请求模型"""
    title: str
    content: str


class PostResponse(BaseModel):
    """文章详情响应模型"""
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

##### 评论模块 `app/schemas/comment.py`

```
from pydantic import BaseModel
from datetime import datetime


class CommentCreate(BaseModel):
    """发布评论请求模型"""
    content: str
    post_id: int


class CommentResponse(BaseModel):
    """评论信息响应模型"""
    id: int
    content: str
    post_id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

------

### 第四步：核心安全工具 + 业务服务层

#### 4.1 核心安全工具 `app/core/security.py`

**模块定位**：系统级鉴权基础设施，属于 core 核心层，提供密码哈希与 JWT 令牌管理。

##### 密码算法说明

采用 **Argon2id** 作为密码哈希算法，是当前行业标准首选：

- 内存困难型设计，抗 GPU/ASIC 暴力破解能力远强于 bcrypt
- 无 72 字节密码长度限制，支持任意长度密码
- RFC9106 标准推荐，Web 后端登录系统通用方案

##### 完整实现

```
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings


# 全局密码上下文，使用 argon2 算法，全局只初始化一次
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """将明文密码哈希化，用于数据库存储"""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希值是否匹配，用于登录验证"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成 JWT 访问令牌
    :param data: 标准载荷 {"sub": "用户ID字符串"}
    """
    to_encode = data.copy()
    # 使用 UTC 时区计算过期时间，避免时区差异
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # 使用配置的密钥和算法签名
    encoded_jwt = jwt.encode(
        to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[int]:
    """
    解析校验 JWT 令牌
    有效返回用户 ID，失效/篡改/过期均返回 None
    """
    try:
        payload = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id_str = payload.get("sub")
        return int(user_id_str) if user_id_str else None
    except (JWTError, ValueError):
        return None
```

#### 4.2 用户业务服务 `app/services/user_service.py`

**模块定位**：承上启下，封装所有用户相关业务逻辑，接口层不直接操作数据库。 **分层规则**：服务层只处理业务逻辑，不抛 HTTP 异常，通过返回值传递结果。

```
from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password


def get_user_by_username(db: Session, username: str) -> User | None:
    """根据用户名查询用户对象，用于注册查重、登录校验"""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_in: UserCreate) -> User | None:
    """
    创建新用户
    用户名重复返回 None，成功返回用户对象
    """
    existing_user = get_user_by_username(db, user_in.username)
    if existing_user:
        return None

    # 明文密码转哈希后再入库
    hashed_password = hash_password(user_in.password)
    new_user = User(
        username=user_in.username,
        password_hash=hashed_password,
        email=user_in.email,
    )

    # 数据库入库三步：add -> commit -> refresh
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    校验用户名密码，登录专用
    用户不存在、密码错误均返回 None
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
```

------

### 第五步：接口层落地（用户模块）

#### 5.1 用户模块接口 `app/api/v1/user.py`

**职责**：接收请求、注入依赖、调用服务层、处理状态码、返回结果。

```
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.core.security import create_access_token


router = APIRouter(tags=["用户模块"])


@router.post("/register", response_model=UserResponse, summary="用户注册")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    新用户注册
    - 用户名重复返回 400 错误
    - 密码自动哈希后入库
    - 响应模型自动过滤密码哈希等敏感字段
    """
    new_user = user_service.create_user(db, user_in)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    return new_user


@router.post("/login", summary="用户登录")
def login(form_data: OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
    """
    用户登录，使用 OAuth2 标准表单格式
    校验成功返回 JWT 访问令牌
    """
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 标准载荷：sub 存储用户 ID 字符串
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
```

#### 5.2 注册到总路由

编辑 `app/api/v1/__init__.py`，注册用户模块路由，前缀自动拼接。

```
from fastapi import APIRouter
from app.api.v1 import user, post, comment

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(user.router, prefix="/users", tags=["用户模块"])
# 后续文章、评论模块依次注册
# api_router.include_router(post.router, prefix="/posts", tags=["文章模块"])
# api_router.include_router(comment.router, prefix="/comments", tags=["评论模块"])
```

#### 5.3 验证方式

启动服务后访问 `[http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)`，在交互式文档中：

1. 调用注册接口，测试正常注册、用户名重复报错
2. 调用登录接口，测试密码错误报错、正确返回令牌

------

## 四、开发辅助指南

### 4.1 排错核心技巧

#### 1. 区分 Warning 与 Error

- **Warning（警告）**：黄色/白色提示，仅为不规范提醒，不影响运行，新手可直接忽略
- **Error（错误）**：伴随 `Traceback (most recent call last)`，是导致程序崩溃的真正原因，仅需关注此类信息

#### 2. 报错正确读法：从下往上看

1. **最底部一行**：错误类型 + 直接原因
2. **往上找第一个自己写的文件**：定位出错的文件与行号
3. **对应行检查**：拼写、导入、语法、参数，90% 低级错误可直接定位

#### 3. 常见错误快速定位

| 报错关键词            | 排查方向                                             |
| --------------------- | ---------------------------------------------------- |
| `ModuleNotFoundError` | 模块名拼写错误、执行目录不在项目根目录、导入路径错误 |
| `NameError`           | 变量/函数名拼写错误，或忘记导入                      |
| `AttributeError`      | 对象属性名拼写错误                                   |
| `OperationalError`    | 数据库未启动、连接地址/账号密码错误                  |

### 4.2 接口文档 Schema 说明

接口文档底部的 `HTTPValidationError`、`ValidationError` 是 FastAPI 自动注入的 422 校验结构，无法彻底移除，属于框架自带机制。通过 `defaultModelsExpandDepth: 0` 可默认折叠，保持页面整洁。

### 4.3 Git 版本控制

#### 提交规范

常用提交类型：

- `init:` 项目初始化
- `feat:` 新增功能、接口
- `fix:` 修复 bug
- `refactor:` 代码重构，不改变功能
- `docs:` 更新文档、注释
- `chore:` 调整依赖、配置等杂项

示例：`git commit -m "feat(user): 新增用户注册登录接口"`

#### 多仓库同步

可通过配置多个推送地址，实现一次 push 同时同步到 Gitee、GitHub 两个仓库。

------

## 五、常见问题记录

1. **Alembic 无法生成迁移脚本**：检查数据库地址是否有空格、模型是否在 `__init__.py` 导出、`target_metadata` 配置是否正确
2. **bcrypt 密码长度报错**：新版 bcrypt 取消静默截断，超过 72 字节直接报错，推荐切换为 Argon2 算法
3. **JWT 参数名报错**：新版 `python-jose` 密钥参数为 `key=`，不是 `secret_key=`
4. **`datetime.utcnow()` 弃用**：替换为 `datetime.now(timezone.utc)`，全版本兼容且无时区问题

------

## 六、项目剩余待推进内容

项目0当前已完成约 60%，剩余待落地：

1. 鉴权依赖封装：`get_current_user` 全局依赖，实现接口登录校验
2. 文章、评论模块：服务层 + 接口层全量落地，含增删改查、分页、权限校验
3. 全局异常处理：统一错误返回格式
4. 单元测试：核心接口测试，覆盖率达标
5. 项目文档整理与完整复盘