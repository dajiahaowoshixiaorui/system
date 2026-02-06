"""用户Pydantic模式"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

from app.models.user import UserRole, UserStatus


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserCreate(BaseModel):
    """用户创建请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    full_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    role: UserRole = UserRole.USER
    max_borrow_count: int = Field(5, ge=1, le=20, description="最大借阅数量")


class UserUpdate(BaseModel):
    """用户更新请求"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    full_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    status: Optional[UserStatus] = None
    max_borrow_count: Optional[int] = Field(None, ge=1, le=20, description="最大借阅数量")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    phone: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: UserRole
    status: UserStatus
    max_borrow_count: int
    current_borrow_count: int
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPasswordUpdate(BaseModel):
    """密码更新请求"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
