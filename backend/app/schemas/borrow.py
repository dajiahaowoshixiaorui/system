"""借阅Pydantic模式"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.schemas.common import BaseQuery, DateRangeQuery


class BorrowCreate(BaseModel):
    """借阅创建请求"""
    user_id: int = Field(..., description="用户ID")
    book_id: int = Field(..., description="图书ID")
    due_days: int = Field(30, ge=1, le=60, description="借阅天数，默认30天")


class BorrowResponse(BaseModel):
    """借阅响应"""
    id: int
    user_id: int
    book_id: int
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: str
    renew_count: int
    overdue_days: int
    fine_amount: float
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    # 扩展字段
    user_name: Optional[str] = None
    book_title: Optional[str] = None
    book_isbn: Optional[str] = None

    class Config:
        from_attributes = True


class BorrowQuery(BaseQuery, DateRangeQuery):
    """借阅查询参数"""
    user_id: Optional[int] = Field(None, description="用户ID")
    book_id: Optional[int] = Field(None, description="图书ID")
    status: Optional[str] = Field(None, description="状态")


class ReturnBook(BaseModel):
    """还书请求"""
    record_id: int = Field(..., description="借阅记录ID")
    remark: Optional[str] = Field(None, description="备注")


class RenewBook(BaseModel):
    """续借请求"""
    record_id: int = Field(..., description="借阅记录ID")


class BorrowStatistics(BaseModel):
    """借阅统计"""
    total_borrow_count: int = 0
    total_return_count: int = 0
    total_overdue_count: int = 0
    total_fine_amount: float = 0.0
    popular_books: list = []
    active_users: list = []
