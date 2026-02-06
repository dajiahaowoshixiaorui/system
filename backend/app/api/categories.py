"""分类API路由"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.book import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryQuery
from app.schemas.common import ResponseModel, PaginatedResponse
from app.api.auth import get_current_active_user, require_admin

router = APIRouter(prefix="/categories", tags=["分类管理"])


@router.get("", response_model=PaginatedResponse[CategoryResponse])
async def get_categories(
    query: CategoryQuery = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    query_builder = db.query(Category)

    # 名称筛选
    if query.name:
        query_builder = query_builder.filter(Category.name.ilike(f"%{query.name}%"))

    # 父分类筛选
    if query.parent_id is not None:
        query_builder = query_builder.filter(Category.parent_id == query.parent_id)

    # 启用状态
    if query.is_active is not None:
        query_builder = query_builder.filter(Category.is_active == query.is_active)

    total = query_builder.count()
    offset = (query.page - 1) * query.page_size
    categories = query_builder.order_by(Category.sort_order, Category.id).offset(offset).limit(query.page_size).all()

    return PaginatedResponse(
        items=categories,
        total=total,
        page=query.page,
        page_size=query.page_size,
        total_pages=(total + query.page_size - 1) // query.page_size
    )


@router.get("/all", response_model=ResponseModel[List[CategoryResponse]])
async def get_all_categories(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取所有分类（下拉选择用）"""
    categories = db.query(Category).filter(Category.is_active == True).order_by(Category.sort_order).all()
    return ResponseModel(data=categories)


@router.get("/{category_id}", response_model=ResponseModel[CategoryResponse])
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取分类详情"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return ResponseModel(data=category)


@router.post("", response_model=ResponseModel[CategoryResponse])
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """创建分类"""
    # 检查名称唯一性
    if db.query(Category).filter(Category.name == category_data.name).first():
        raise HTTPException(status_code=400, detail="分类名称已存在")

    # 检查父分类
    if category_data.parent_id:
        parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="父分类不存在")

    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)

    return ResponseModel(data=category, message="创建成功")


@router.put("/{category_id}", response_model=ResponseModel[CategoryResponse])
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    # 检查名称唯一性
    if category_data.name and category_data.name != category.name:
        if db.query(Category).filter(Category.name == category_data.name, Category.id != category_id).first():
            raise HTTPException(status_code=400, detail="分类名称已存在")

    # 检查父分类
    if category_data.parent_id is not None:
        if category_data.parent_id == category_id:
            raise HTTPException(status_code=400, detail="不能设置自己为父分类")
        if category_data.parent_id:
            parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
            if not parent:
                raise HTTPException(status_code=400, detail="父分类不存在")

    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return ResponseModel(data=category, message="更新成功")


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    # 检查是否有子分类
    if db.query(Category).filter(Category.parent_id == category_id).first():
        raise HTTPException(status_code=400, detail="该分类下存在子分类，无法删除")

    # 检查是否有图书
    if category.books.count() > 0:
        raise HTTPException(status_code=400, detail="该分类下存在图书，无法删除")

    category.is_active = False
    db.commit()

    return ResponseModel(message="删除成功")
