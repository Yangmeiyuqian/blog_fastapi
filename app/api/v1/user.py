from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["用户模块"])

@router.get("/register", summary="用户注册")
def register():
    pass