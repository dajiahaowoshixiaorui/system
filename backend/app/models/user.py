"""用户相关数据模型"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(PyEnum):
    """用户角色枚举"""
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    USER = "user"


class UserStatus(PyEnum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    __table_args__ = (
        {"comment": "用户信息表"},
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")

    full_name = Column(String(50), nullable=True, comment="真实姓名")
    avatar_url = Column(String(500), nullable=True, comment="头像URL")

    role = Column(Enum(UserRole), default=UserRole.USER, comment="角色")
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, comment="状态")

    max_borrow_count = Column(Integer, default=5, comment="最大借阅数量")
    current_borrow_count = Column(Integer, default=0, comment="当前借阅数量")

    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    borrow_records = relationship("BorrowRecord", back_populates="user", lazy="dynamic", foreign_keys="[BorrowRecord.user_id]")
    operated_records = relationship("BorrowRecord", foreign_keys="[BorrowRecord.operator_id]")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    @property
    def can_borrow(self) -> bool:
        """检查是否可以借书"""
        return (
            self.status == UserStatus.ACTIVE
            and self.current_borrow_count < self.max_borrow_count
        )
