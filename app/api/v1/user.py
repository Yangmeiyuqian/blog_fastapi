from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["用户模块"])

@router.get("/register")
def register():
    pass