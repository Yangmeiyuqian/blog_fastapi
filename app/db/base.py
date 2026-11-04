"""数据库引擎+会话工厂+ORM基类+会话依赖"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# 创建 engine 引擎对象
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 创建SessionLocal会话工厂
SessionLocal = sessionmaker(autocommit=False, autoFlush=False, bind=engine)

# ORM基类，后期所有的数据表模型都继承它
class Base(DeclarativeBase):
    pass

# 数据会话依赖，后面用Depends依赖注入
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()