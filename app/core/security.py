# import sys
# from pathlib import Path
# # 先把项目根目录加到搜索路径！
# BASE_DIR = Path(__file__).parent.parent
# sys.path.insert(0, str(BASE_DIR))

# 再写别的导入！顺序不能乱
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
            return int(user_id)
    except (JWTError, ValueError):
        return None

# if __name__ == "__main__":
    # test_pw = "123456"
    # h = hash_password(test_pw)
    # print("明文：", test_pw)
    # print("哈希值：", h)B
    # print("校验：", verify_password(test_pw, h))
    #
    # # 测试JWT
    # token = create_access_token({"sub": "1001"})
    # print("token：", token)
    # uid = decode_access_token(token)
    # print("解码得到用户id：", uid)
