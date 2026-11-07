from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.core.security import create_access_token

router = APIRouter(tags=["用户模块"]) #需要汇总到init总路由 #子模块路由不加前缀，在总路由注册时统一加模块前缀。

"""
    1. 用户注册接口 `POST /register`
    - **入参**：请求体 `UserCreate`（用户名、密码、可选邮箱）
    - **业务流程**：
      1. 注入数据库会话依赖
      2. 调用 `user_service.create_user` 创建用户
      3. 创建失败（用户名重复）→ 抛出 400 错误，提示「用户名已存在」
      4. 创建成功 → 返回 `UserResponse` 格式的用户信息（UserResponse模型会自动过滤密码哈希字段）
    - **状态码**：成功 200，参数错误 / 重复 400
"""
@router.post("/register", response_model=UserResponse, summary="用户注册")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    new_user = user_service.create_user(db, user_in)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    return new_user

"""
    2. 用户登录接口 `POST /login`
    - **入参**：使用 OAuth2 标准表单格式 `OAuth2PasswordRequestForm`（FastAPI 内置），对应 username 和 password 字段
    - **业务流程**：
      1. 注入数据库会话依赖
      2. 调用 `user_service.authenticate_user` 校验用户名密码
      3. 校验失败 → 抛出 401 未授权错误，提示「用户名或密码错误」
      4. 校验成功 → 生成 JWT 令牌，返回标准格式 `{"access_token": "xxx", "token_type": "bearer"}`
    - **状态码**：成功 200，校验失败 401
"""
@router.post("/login", summary="用户登录")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}