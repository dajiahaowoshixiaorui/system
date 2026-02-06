"""借阅API路由"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.database import get_db
from app.models.user import User, UserStatus, UserRole
from app.models.book import Book, BookStatus
from app.models.borrow import BorrowRecord
from app.schemas.borrow import (
    BorrowCreate, BorrowResponse, BorrowQuery, ReturnBook, RenewBook
)
from app.schemas.common import ResponseModel, PaginatedResponse
from app.api.auth import get_current_active_user, require_admin
from app.services.redis import RedisService

router = APIRouter(prefix="/borrows", tags=["借阅管理"])

redis_service = RedisService()


@router.post("")
async def create_borrow(
    borrow_data: BorrowCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """借书"""
    # 检查用户
    user = db.query(User).filter(User.id == borrow_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    if user.can_borrow is False:
        raise HTTPException(status_code=400, detail="借阅数量已达上限")

    # 检查图书
    book = db.query(Book).filter(Book.id == borrow_data.book_id, Book.is_active == True).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    if not book.is_available:
        raise HTTPException(status_code=400, detail="图书不可借")

    # 检查是否已借阅该书且未归还
    existing = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == borrow_data.user_id,
        BorrowRecord.book_id == borrow_data.book_id,
        BorrowRecord.status == "borrowed"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已借阅此书，尚未归还")

    # 计算应还日期
    due_date = datetime.utcnow() + timedelta(days=borrow_data.due_days)

    # 创建借阅记录
    record = BorrowRecord(
        user_id=borrow_data.user_id,
        book_id=borrow_data.book_id,
        due_date=due_date,
        operator_id=current_user.id,
    )
    db.add(record)

    # 更新图书库存
    book.available_stock = book.available_stock - 1
    if book.available_stock == 0:
        book.status = "borrowed"
    book.borrow_count = book.borrow_count + 1

    # 更新用户借阅数量
    user.current_borrow_count = user.current_borrow_count + 1

    db.commit()
    db.refresh(record)

    # 清除缓存
    await redis_service.delete(f"book:{book.id}")

    return ResponseModel(data=record, message="借书成功")


@router.post("/return")
async def return_book(
    return_data: ReturnBook,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """还书"""
    record = db.query(BorrowRecord).filter(BorrowRecord.id == return_data.record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="借阅记录不存在")
    if record.status == "returned":
        raise HTTPException(status_code=400, detail="该书已归还")

    # 计算逾期
    now = datetime.utcnow()
    if now > record.due_date:
        record.overdue_days = (now - record.due_date).days
        record.status = "overdue"
        # 逾期罚款：每天0.5元
        record.fine_amount = record.overdue_days * 0.5
    else:
        record.status = "returned"

    record.return_date = now
    record.operator_id = current_user.id
    record.remark = return_data.remark

    # 更新图书库存
    book = db.query(Book).filter(Book.id == record.book_id).first()
    if book:
        book.available_stock = book.available_stock + 1
        if book.status == "borrowed":
            book.status = "available"

    # 更新用户借阅数量
    user = db.query(User).filter(User.id == record.user_id).first()
    if user and user.current_borrow_count > 0:
        user.current_borrow_count = user.current_borrow_count - 1

    db.commit()
    db.refresh(record)

    # 清除缓存
    if book:
        await redis_service.delete(f"book:{book.id}")

    return ResponseModel(data=record, message="还书成功")


@router.post("/renew", response_model=ResponseModel[BorrowResponse])
async def renew_book(
    renew_data: RenewBook,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """续借"""
    record = db.query(BorrowRecord).filter(BorrowRecord.id == renew_data.record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="借阅记录不存在")
    if not record.can_renew:
        raise HTTPException(status_code=400, detail="无法续借")

    # 续借：延长应还日期14天
    record.due_date = record.due_date + timedelta(days=14)
    record.renew_count = record.renew_count + 1

    db.commit()
    db.refresh(record)

    return ResponseModel(data=record, message="续借成功")


@router.get("", response_model=PaginatedResponse[BorrowResponse])
async def get_borrows(
    query: BorrowQuery = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取借阅记录列表"""
    query_builder = db.query(BorrowRecord).join(User, BorrowRecord.user_id == User.id).join(
        Book, BorrowRecord.book_id == Book.id
    )

    # 非管理员只能查看自己的记录
    if current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        query_builder = query_builder.filter(BorrowRecord.user_id == current_user.id)

    # 日期范围筛选
    if query.start_date:
        query_builder = query_builder.filter(BorrowRecord.borrow_date >= query.start_date)
    if query.end_date:
        query_builder = query_builder.filter(BorrowRecord.borrow_date <= query.end_date)

    # 用户筛选
    if query.user_id and current_user.role in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        query_builder = query_builder.filter(BorrowRecord.user_id == query.user_id)

    # 图书筛选
    if query.book_id:
        query_builder = query_builder.filter(BorrowRecord.book_id == query.book_id)

    # 状态筛选
    if query.status:
        query_builder = query_builder.filter(BorrowRecord.status == query.status)

    total = query_builder.count()
    offset = (query.page - 1) * query.page_size
    records = query_builder.order_by(BorrowRecord.created_at.desc()).offset(offset).limit(query.page_size).all()

    # 构建响应，添加扩展字段
    items = []
    for record in records:
        item = {
            **record.__dict__,
            "user_name": record.user.username if record.user else None,
            "book_title": record.book.title if record.book else None,
            "book_isbn": record.book.isbn if record.book else None,
        }
        items.append(item)

    return PaginatedResponse(
        items=items,
        total=total,
        page=query.page,
        page_size=query.page_size,
        total_pages=(total + query.page_size - 1) // query.page_size
    )


@router.get("/my", response_model=PaginatedResponse[BorrowResponse])
async def get_my_borrows(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的借阅记录"""
    query_builder = db.query(BorrowRecord).filter(BorrowRecord.user_id == current_user.id)

    if status:
        query_builder = query_builder.filter(BorrowRecord.status == status)

    total = query_builder.count()
    offset = (page - 1) * page_size
    records = query_builder.order_by(BorrowRecord.created_at.desc()).offset(offset).limit(page_size).all()

    return PaginatedResponse(
        items=records,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/user/{user_id}", response_model=PaginatedResponse[BorrowResponse])
async def get_user_borrows(
    user_id: int,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户借阅记录"""
    # 非管理员只能查看自己的
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise HTTPException(status_code=403, detail="无权查看")

    query_builder = db.query(BorrowRecord).filter(BorrowRecord.user_id == user_id)

    if status:
        query_builder = query_builder.filter(BorrowRecord.status == status)

    total = query_builder.count()
    offset = (page - 1) * page_size
    records = query_builder.order_by(BorrowRecord.created_at.desc()).offset(offset).limit(page_size).all()

    return PaginatedResponse(
        items=records,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/overdue", response_model=PaginatedResponse[BorrowResponse])
async def get_overdue_borrows(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取逾期记录"""
    query_builder = db.query(BorrowRecord).filter(
        BorrowRecord.status == "overdue"
    )

    total = query_builder.count()
    offset = (page - 1) * page_size
    records = query_builder.order_by(BorrowRecord.due_date).offset(offset).limit(page_size).all()

    return PaginatedResponse(
        items=records,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/statistics")
async def get_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取借阅统计"""
    total_borrow = db.query(BorrowRecord).filter(BorrowRecord.status != "returned").count()
    total_returned = db.query(BorrowRecord).filter(BorrowRecord.status == "returned").count()
    total_overdue = db.query(BorrowRecord).filter(BorrowRecord.status == "overdue").count()
    total_fine = db.query(BorrowRecord).with_entities(
        func.coalesce(func.sum(BorrowRecord.fine_amount), 0)
    ).scalar()

    # 热门图书TOP10
    popular_books = db.query(Book).order_by(Book.borrow_count.desc()).limit(10).all()

    # 活跃用户TOP10
    active_users = db.query(User).order_by(User.current_borrow_count.desc()).limit(10).all()

    return ResponseModel(data={
        "total_borrow_count": total_borrow,
        "total_return_count": total_returned,
        "total_overdue_count": total_overdue,
        "total_fine_amount": float(total_fine),
        "popular_books": [{"id": b.id, "title": b.title, "borrow_count": b.borrow_count} for b in popular_books],
        "active_users": [{"id": u.id, "username": u.username, "borrow_count": u.current_borrow_count} for u in active_users],
    })
