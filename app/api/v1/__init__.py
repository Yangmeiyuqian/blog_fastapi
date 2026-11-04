from fastapi import APIRouter
from app.api.v1 import user,comment
# 创建 api_router 总路由器对象，设置前缀为 /api/v1
api_router = APIRouter(prefix="/api/v1")

# 注册子路由，每个子路由的前缀会和总路由前缀拼接
api_router.include_router(user.router)