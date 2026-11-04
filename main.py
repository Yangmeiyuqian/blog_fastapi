"""项目启动入口"""
from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import logger
from app.api.v1 import api_router
import uvicorn

# 创建app实例
app = FastAPI(
    title="博客系统接口",
    version="v1.0.0",
    description="基于FastAPI标准后端博客系统"
)

# 挂载路由
app.include_router(api_router)

@app.get("/health", summary="健康检查接口", description="检查接口，验证服务是否正常")
def health_check():
    """
    Returns:
        dict: 标准响应体
            code: int, 业务状态码
            msg: str, 提示信息
            version: str, 应用版本

    Raises:
        内部code说明：
            400: 参数校验失败
            401: Token缺失/登录失效
            403: 权限不足
            404: 资源不存在
            500: 服务内部异常
    """
    logger.info("健康检查调用")
    return { "code": 0,"version": "v1.0.0","message": "服务运行正常" }

if __name__ == "__main__":
    # main.py 末尾
    if __name__ == "__main__":
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.APP_PORT,
            reload=settings.DEBUG,  # 开启热加载
            reload_dirs=["."]
        )
