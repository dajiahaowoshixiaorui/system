"""分类Pydantic模式"""
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.common import BaseQuery


class CategoryCreate(BaseModel):
    """分类创建请求"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: int = Field(0, ge=0, description="排序")


class CategoryUpdate(BaseModel):
    """分类更新请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: Optional[int] = Field(None, ge=0, description="排序")
    is_active: Optional[bool] = Field(None, description="是否启用")


class CategoryResponse(BaseModel):
    """分类响应"""
    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    sort_order: int
    is_active: bool
    created_at: object  # datetime
    updated_at: object  # datetime

    class Config:
        from_attributes = True


class CategoryQuery(BaseQuery):
    """分类查询参数"""
    name: Optional[str] = Field(None, description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    is_active: Optional[bool] = Field(None, description="是否启用")
