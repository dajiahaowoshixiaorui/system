"""图书Pydantic模式"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

from app.schemas.common import BaseQuery


class BookCreate(BaseModel):
    """图书创建请求"""
    isbn: str = Field(..., min_length=10, max_length=20, description="ISBN")
    title: str = Field(..., min_length=1, max_length=200, description="书名")
    author: str = Field(..., min_length=1, max_length=100, description="作者")
    publisher: Optional[str] = Field(None, max_length=100, description="出版社")
    publish_date: Optional[str] = Field(None, max_length=20, description="出版日期")
    price: Decimal = Field(0.00, ge=0, description="价格")

    category_id: Optional[int] = Field(None, description="分类ID")
    summary: Optional[str] = Field(None, description="图书简介")
    cover_url: Optional[str] = Field(None, max_length=500, description="封面URL")

    total_stock: int = Field(1, ge=0, description="总库存")
    location: Optional[str] = Field(None, max_length=100, description="馆藏位置")

    @field_validator("isbn")
    @classmethod
    def isbn_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("ISBN不能为空")
        return v.strip()

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("书名不能为空")
        return v.strip()


class BookUpdate(BaseModel):
    """图书更新请求"""
    isbn: Optional[str] = Field(None, min_length=10, max_length=20, description="ISBN")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="书名")
    author: Optional[str] = Field(None, min_length=1, max_length=100, description="作者")
    publisher: Optional[str] = Field(None, max_length=100, description="出版社")
    publish_date: Optional[str] = Field(None, max_length=20, description="出版日期")
    price: Optional[Decimal] = Field(None, ge=0, description="价格")

    category_id: Optional[int] = Field(None, description="分类ID")
    summary: Optional[str] = Field(None, description="图书简介")
    cover_url: Optional[str] = Field(None, max_length=500, description="封面URL")

    total_stock: Optional[int] = Field(None, ge=0, description="总库存")
    location: Optional[str] = Field(None, max_length=100, description="馆藏位置")
    status: Optional[str] = Field(None, description="状态")


class BookResponse(BaseModel):
    """图书响应"""
    id: int
    isbn: str
    title: str
    author: str
    publisher: Optional[str]
    publish_date: Optional[str]
    price: Decimal
    category_id: Optional[int]
    summary: Optional[str]
    cover_url: Optional[str]
    total_stock: int
    available_stock: int
    borrow_count: int
    status: str
    location: Optional[str]
    created_at: datetime
    updated_at: datetime

    # 扩展字段
    category_name: Optional[str] = None

    class Config:
        from_attributes = True


class BookQuery(BaseQuery):
    """图书查询参数"""
    keyword: Optional[str] = Field(None, description="关键词搜索")
    category_id: Optional[int] = Field(None, description="分类ID")
    author: Optional[str] = Field(None, description="作者")
    status: Optional[str] = Field(None, description="状态")
    is_active: Optional[bool] = Field(None, description="是否启用")


class BookBulkCreate(BaseModel):
    """批量创建图书"""
    books: List[BookCreate]
