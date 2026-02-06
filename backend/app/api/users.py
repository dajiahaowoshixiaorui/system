"""用户API路由"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt

from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from app.schemas.common import ResponseModel, PaginatedResponse
from app.api.auth import get_current_active_user, require_admin, get_password_hash

router = APIRouter(prefix="/users", tags=["用户管理"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


@router.get("", response_model=PaginatedResponse[UserResponse])
async def get_users(
    keyword: Optional[str] = None,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query_builder = db.query(User)

    if keyword:
        query_builder = query_builder.filter(
            (User.username.ilike(f"%{keyword}%")) |
            (User.email.ilike(f"%{keyword}%")) |
            (User.full_name.ilike(f"%{keyword}%"))
        )

    if role:
        query_builder = query_builder.filter(User.role == role)

    if status:
        query_builder = query_builder.filter(User.status == status)

    total = query_builder.count()
    offset = (page - 1) * page_size
    users = query_builder.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()

    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{user_id}", response_model=ResponseModel[UserResponse])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户详情"""
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise HTTPException(status_code=403, detail="无权查看")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return ResponseModel(data=user)


@router.post("", response_model=ResponseModel[UserResponse])
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """创建用户"""
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = User(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        max_borrow_count=user_data.max_borrow_count,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return ResponseModel(data=user, message="创建成功")


@router.put("/{user_id}", response_model=ResponseModel[UserResponse])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user_data.email and user_data.email != user.email:
        if db.query(User).filter(User.email == user_data.email, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="邮箱已被注册")

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return ResponseModel(data=user, message="更新成功")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    db.delete(user)
    db.commit()

    return ResponseModel(message="删除成功")


@router.put("/{user_id}/password")
async def update_password(
    user_id: int,
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise HTTPException(status_code=403, detail="无权操作")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")

    user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return ResponseModel(message="密码修改成功")


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    status: UserStatus,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """修改用户状态"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己")

    user.status = status
    db.commit()

    return ResponseModel(message="状态更新成功")


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: UserRole,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """修改用户角色"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.role = role
    db.commit()

    return ResponseModel(message="角色更新成功")
