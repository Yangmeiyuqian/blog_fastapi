from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

# 执行加载.env文件函数
load_dotenv()

# 定义Settings类，继承Pydantic基类，类属性需要和.env的配置保持对应并设置默认值
class Settings(BaseSettings):
    """全局配置类，自动从环境变量读取并做类型校验"""
    # 服务
    APP_PORT: int = 8080
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    HOST: str = "127.0.0.1"
    DEBUG: bool = True
    # 数据库
    DATABASE_URL: str = ""
    # JWT
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    # LOG
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "blog.log"

# 全局单例
settings = Settings()