"""通用Pydantic模式"""
from datetime import datetime
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


T = TypeVar("T")


class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token载荷数据"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None


class StatusEnum(str, Enum):
    """状态枚举"""
    SUCCESS = "success"
    ERROR = "error"


class ResponseModel(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 200
    status: StatusEnum = StatusEnum.SUCCESS
    message: str = "操作成功"
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "status": "success",
                "message": "操作成功",
                "data": None
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10
            }
        }


class BaseQuery(BaseModel):
    """基础查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class DateRangeQuery(BaseModel):
    """日期范围查询"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
