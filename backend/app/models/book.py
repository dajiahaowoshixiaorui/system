"""图书相关数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Integer, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum


class BookStatus(str, Enum):
    """图书状态枚举"""
    AVAILABLE = "available"
    BORROWED = "borrowed"
    MAINTENANCE = "maintenance"
    LOST = "lost"


class Category(Base):
    """图书分类模型"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="分类名称")
    description = Column(Text, nullable=True, comment="分类描述")
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True, comment="父分类ID")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    parent = relationship("Category", remote_side=[id], backref="children")
    books = relationship("Book", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Book(Base):
    """图书模型"""
    __tablename__ = "books"
    __table_args__ = (
        {"comment": "图书信息表"},
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    isbn = Column(String(20), unique=True, nullable=False, index=True, comment="ISBN")
    title = Column(String(200), nullable=False, comment="书名")
    author = Column(String(100), nullable=False, comment="作者")
    publisher = Column(String(100), nullable=True, comment="出版社")
    publish_date = Column(String(20), nullable=True, comment="出版日期")
    price = Column(Numeric(10, 2), default=0.00, comment="价格")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, comment="分类ID")
    summary = Column(Text, nullable=True, comment="图书简介")
    cover_url = Column(String(500), nullable=True, comment="封面图片URL")

    total_stock = Column(Integer, default=1, comment="总库存")
    available_stock = Column(Integer, default=1, comment="可借库存")
    borrow_count = Column(Integer, default=0, comment="借阅次数")

    status = Column(String(20), default="available", comment="状态: available/borrowed/maintenance")
    location = Column(String(100), nullable=True, comment="馆藏位置")

    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    category = relationship("Category", back_populates="books")
    borrow_records = relationship("BorrowRecord", back_populates="book", lazy="dynamic")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', isbn='{self.isbn}')>"

    @property
    def is_available(self) -> bool:
        """检查是否可借"""
        return self.available_stock > 0 and self.status == "available"
