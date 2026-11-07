from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password
"""
    get_user_by_username(db: Session, username: str) -> User | None
    - 作用：根据用户名查询用户对象
    - 用途：注册时查重、登录时查询用户
"""
def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

"""
    create_user(db: Session, user_in: UserCreate) -> User | None
    - 作用：创建新用户
    - 业务流程：
      1. 先查询用户名是否已存在，存在则返回 None
      2. 将传入的明文密码转为哈希值
      3. 创建 User 数据库对象，加入会话、提交、刷新后返回
    - 注意：数据库存储的是 `password_hash`，不是明文 password
"""
def create_user(db: Session, user_in: UserCreate) -> User | None:
    is_user_exist: User | None = get_user_by_username(db, user_in.username)
    if is_user_exist:
        return None
    hashed_password = hash_password(user_in.password)
    new_user = User(
        username=user_in.username,
        password_hash=hashed_password,
        email=user_in.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

"""
    authenticate_user(db: Session, username: str, password: str) -> User | None
    - 作用：校验用户名密码是否正确，登录专用
    - 业务流程：
      1. 先按用户名查用户，不存在直接返回 None
      2. 用户存在则校验密码，密码错误返回 None
      3. 都正确则返回用户对象
"""
def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user: User | None = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user