"""图书API路由"""
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.user import User, UserRole
from app.models.book import Book, Category
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookQuery
from app.schemas.common import ResponseModel, PaginatedResponse
from app.api.auth import get_current_active_user, require_admin
from app.services.search import SearchService
from app.services.redis import RedisService

router = APIRouter(prefix="/books", tags=["图书管理"])

redis_service = RedisService()


@router.get("", response_model=PaginatedResponse[BookResponse])
async def get_books(
    query: BookQuery = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取图书列表"""
    # 构建查询
    query_builder = db.query(Book).join(Category, Book.category_id == Category.id, isouter=True)

    # 关键词搜索
    if query.keyword:
        search_pattern = f"%{query.keyword}%"
        query_builder = query_builder.filter(
            or_(
                Book.title.ilike(search_pattern),
                Book.author.ilike(search_pattern),
                Book.isbn.ilike(search_pattern)
            )
        )

    # 分类筛选
    if query.category_id:
        query_builder = query_builder.filter(Book.category_id == query.category_id)

    # 作者筛选
    if query.author:
        query_builder = query_builder.filter(Book.author.ilike(f"%{query.author}%"))

    # 状态筛选
    if query.status:
        query_builder = query_builder.filter(Book.status == query.status)

    # 启用状态
    if query.is_active is not None:
        query_builder = query_builder.filter(Book.is_active == query.is_active)

    # 计算总数
    total = query_builder.count()

    # 分页
    offset = (query.page - 1) * query.page_size
    books = query_builder.order_by(Book.created_at.desc()).offset(offset).limit(query.page_size).all()

    # 构建响应
    items = []
    for book in books:
        book_dict = {
            **book.__dict__,
            "category_name": book.category.name if book.category else None
        }
        items.append(book_dict)

    return PaginatedResponse(
        items=items,
        total=total,
        page=query.page,
        page_size=query.page_size,
        total_pages=(total + query.page_size - 1) // query.page_size
    )


@router.get("/{book_id}")
async def get_book(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取图书详情"""
    # 尝试从缓存获取
    cache_key = f"book:{book_id}"
    cached_data = await redis_service.get(cache_key)
    if cached_data:
        return ResponseModel(data=cached_data)

    book = db.query(Book).filter(Book.id == book_id, Book.is_active == True).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")

    book_dict = {
        **book.__dict__,
        "category_name": book.category.name if book.category else None
    }

    # 缓存数据
    await redis_service.set(cache_key, book_dict, expire=300)

    return ResponseModel(data=book_dict)


@router.post("")
async def create_book(
    book_data: BookCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """创建图书"""
    # 检查ISBN唯一性
    if db.query(Book).filter(Book.isbn == book_data.isbn).first():
        raise HTTPException(status_code=400, detail="ISBN已存在")

    # 检查分类
    if book_data.category_id:
        category = db.query(Category).filter(Category.id == book_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="分类不存在")

    # 创建图书
    book = Book(
        isbn=book_data.isbn,
        title=book_data.title,
        author=book_data.author,
        publisher=book_data.publisher,
        publish_date=book_data.publish_date,
        price=book_data.price,
        category_id=book_data.category_id,
        summary=book_data.summary,
        cover_url=book_data.cover_url,
        total_stock=book_data.total_stock,
        available_stock=book_data.total_stock,
        location=book_data.location,
    )
    db.add(book)
    db.commit()
    db.refresh(book)

    # 同步到Elasticsearch
    SearchService.index_book(book)

    # 清除缓存
    await redis_service.delete_pattern("books:*")

    return ResponseModel(data=book, message="创建成功")


@router.put("/{book_id}")
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """更新图书"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")

    # 检查ISBN唯一性
    if book_data.isbn and book_data.isbn != book.isbn:
        if db.query(Book).filter(Book.isbn == book_data.isbn, Book.id != book_id).first():
            raise HTTPException(status_code=400, detail="ISBN已存在")

    # 更新字段
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)

    # 同步到Elasticsearch
    SearchService.index_book(book)

    # 清除缓存
    await redis_service.delete(f"book:{book_id}")
    await redis_service.delete_pattern("books:*")

    return ResponseModel(data=book, message="更新成功")


@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除图书（软删除）"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")

    book.is_active = False
    db.commit()

    # 从Elasticsearch删除
    SearchService.delete_book(book_id)

    # 清除缓存
    await redis_service.delete(f"book:{book_id}")
    await redis_service.delete_pattern("books:*")

    return ResponseModel(message="删除成功")


@router.get("/search/elasticsearch", response_model=PaginatedResponse[BookResponse])
async def search_books_es(
    keyword: str = Query(..., description="搜索关键词"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """使用Elasticsearch搜索图书"""
    result = SearchService.search(
        keyword=keyword,
        category_id=category_id,
        page=page,
        page_size=page_size
    )
    return PaginatedResponse(
        items=result["hits"],
        total=result["total"],
        page=page,
        page_size=page_size,
        total_pages=(result["total"] + page_size - 1) // page_size
    )


@router.post("/{book_id}/cover")
async def upload_cover(
    book_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """上传图书封面"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")

    # 简化的文件保存逻辑
    # 实际项目中需要验证文件类型、保存到存储服务等
    import os
    from app.config import settings

    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"book_{book_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # 更新封面URL
    cover_url = f"/uploads/{filename}"
    book.cover_url = cover_url
    db.commit()

    return ResponseModel(data={"cover_url": cover_url}, message="上传成功")
