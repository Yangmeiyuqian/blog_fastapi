import logging
from .config import settings

def setup_logger(name: str = "blog") -> logging.Logger:
    # 创建logger实例，设置日志级别
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # 如果logger有handler就返回实例，避免重复添加
    if logger.handlers:
        return logger

    # 定义统一的日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 添加两个输出渠道
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

# 调用setup_logger函数，生成全局实例
logger = setup_logger()