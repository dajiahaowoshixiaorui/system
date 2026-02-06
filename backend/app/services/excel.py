"""Excel导入导出服务"""
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.book import Book, Category
from app.models.user import User
from app.schemas.book import BookCreate


class ExcelService:
    """Excel服务"""

    # 导入模板
    IMPORT_TEMPLATE = [
        {"field": "isbn", "header": "ISBN", "required": True, "max_length": 20},
        {"field": "title", "header": "书名", "required": True, "max_length": 200},
        {"field": "author", "header": "作者", "required": True, "max_length": 100},
        {"field": "publisher", "header": "出版社", "required": False, "max_length": 100},
        {"field": "publish_date", "header": "出版日期", "required": False, "max_length": 20},
        {"field": "price", "header": "价格", "required": False},
        {"field": "category_name", "header": "分类名称", "required": False, "max_length": 50},
        {"field": "summary", "header": "简介", "required": False},
        {"field": "total_stock", "header": "库存数量", "required": False},
        {"field": "location", "header": "馆藏位置", "required": False, "max_length": 100},
    ]

    # 导出字段映射
    EXPORT_FIELDS = {
        "ISBN": "isbn",
        "书名": "title",
        "作者": "author",
        "出版社": "publisher",
        "出版日期": "publish_date",
        "价格": "price",
        "分类": "category_name",
        "简介": "summary",
        "总库存": "total_stock",
        "可借": "available_stock",
        "借阅次数": "borrow_count",
        "状态": "status",
        "馆藏位置": "location",
    }

    @classmethod
    async def import_books(
        cls,
        file: UploadFile,
        db: Session,
        category_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """导入图书"""
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))

        # 标准化列名
        df.columns = df.columns.str.strip()

        # 验证必要字段
        required_fields = ["ISBN", "书名", "作者"]
        for field in required_fields:
            if field not in df.columns:
                raise ValueError(f"缺少必要字段: {field}")

        # 数据转换与验证
        books_data = []
        errors = []

        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel行号（包含表头）

            try:
                # 必填字段验证
                if pd.isna(row["ISBN"]) or str(row["ISBN"]).strip() == "":
                    errors.append(f"第{row_num}行: ISBN不能为空")
                    continue

                if pd.isna(row["书名"]) or str(row["书名"]).strip() == "":
                    errors.append(f"第{row_num}行: 书名不能为空")
                    continue

                if pd.isna(row["作者"]) or str(row["作者"]).strip() == "":
                    errors.append(f"第{row_num}行: 作者不能为空")
                    continue

                # 检查ISBN唯一性
                isbn = str(row["ISBN"]).strip()
                if db.query(Book).filter(Book.isbn == isbn).first():
                    errors.append(f"第{row_num}行: ISBN '{isbn}' 已存在")
                    continue

                # 处理分类
                book_category_id = category_id
                if "分类名称" in df.columns and pd.notna(row.get("分类名称")):
                    category_name = str(row["分类名称"]).strip()
                    category = db.query(Category).filter(
                        Category.name == category_name,
                        Category.is_active == True
                    ).first()
                    if category:
                        book_category_id = category.id

                # 处理价格
                price = 0.0
                if "价格" in df.columns and pd.notna(row.get("价格")):
                    try:
                        price = float(str(row["价格"]).replace(",", ""))
                    except (ValueError, TypeError):
                        pass

                # 处理库存
                total_stock = 1
                if "库存数量" in df.columns and pd.notna(row.get("库存数量")):
                    try:
                        total_stock = int(str(row["库存数量"]).replace(",", ""))
                    except (ValueError, TypeError):
                        pass

                book = BookCreate(
                    isbn=isbn,
                    title=str(row["书名"]).strip(),
                    author=str(row["作者"]).strip(),
                    publisher=str(row["publisher"]).strip() if pd.notna(row.get("出版社")) else None,
                    publish_date=str(row["publish_date"]).strip() if pd.notna(row.get("出版日期")) else None,
                    price=Decimal(str(price)),
                    category_id=book_category_id,
                    summary=str(row["summary"]).strip() if pd.notna(row.get("简介")) else None,
                    total_stock=total_stock,
                    location=str(row["location"]).strip() if pd.notna(row.get("馆藏位置")) else None,
                )
                books_data.append(book)

            except Exception as e:
                errors.append(f"第{row_num}行: 处理失败 - {str(e)}")

        # 批量保存
        if books_data:
            books = []
            for book_data in books_data:
                book = Book(
                    isbn=book_data.isbn,
                    title=book_data.title,
                    author=book_data.author,
                    publisher=book_data.publisher,
                    publish_date=book_data.publish_date,
                    price=book_data.price,
                    category_id=book_data.category_id,
                    summary=book_data.summary,
                    total_stock=book_data.total_stock,
                    available_stock=book_data.total_stock,
                    location=book_data.location,
                )
                db.add(book)
                books.append(book)

            db.commit()
            for book in books:
                db.refresh(book)

        return {
            "success_count": len(books_data),
            "error_count": len(errors),
            "errors": errors[:100],  # 最多返回100条错误
        }

    @classmethod
    def export_books(
        cls,
        books: List[Book],
        fields: Optional[List[str]] = None
    ) -> io.BytesIO:
        """导出图书"""
        if fields is None:
            fields = list(cls.EXPORT_FIELDS.keys())

        data = []
        for book in books:
            row = {}
            for header, field in cls.EXPORT_FIELDS.items():
                if header in fields:
                    value = getattr(book, field, None)
                    if field == "category_name":
                        value = book.category.name if book.category else None
                    elif isinstance(value, Decimal):
                        value = float(value)
                    elif isinstance(value, datetime):
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                    row[header] = value
            data.append(row)

        df = pd.DataFrame(data)

        # 按字段顺序排列
        df = df[fields]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="图书列表")

        output.seek(0)
        return output

    @classmethod
    def export_template(cls) -> io.BytesIO:
        """导出导入模板"""
        template_data = []
        for item in cls.IMPORT_TEMPLATE:
            row = {
                "字段名": item["field"],
                "列名": item["header"],
                "必填": "是" if item["required"] else "否",
                "最大长度": item.get("max_length", ""),
                "示例": "",
            }
            template_data.append(row)

        df = pd.DataFrame(template_data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="导入模板")

        # 添加示例Sheet
        example_data = []
        example_data.append({
            "ISBN": "978-7-111-12345-6",
            "书名": "示例图书",
            "作者": "示例作者",
            "出版社": "示例出版社",
            "出版日期": "2024-01",
            "价格": "59.00",
            "分类名称": "文学",
            "简介": "这是一本示例图书的简介",
            "库存数量": "10",
            "馆藏位置": "A-1-1",
        })

        example_df = pd.DataFrame(example_data)
        with pd.ExcelWriter(output, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
            example_df.to_excel(writer, index=False, sheet_name="示例数据")

        output.seek(0)
        return output

    @classmethod
    def export_borrow_records(
        cls,
        records: List,
        fields: Optional[List[str]] = None
    ) -> io.BytesIO:
        """导出借阅记录"""
        data = []
        for record in records:
            row = {
                "借阅ID": record.id,
                "用户": record.user.username if record.user else "",
                "图书": record.book.title if record.book else "",
                "ISBN": record.book.isbn if record.book else "",
                "借出日期": record.borrow_date.strftime("%Y-%m-%d") if record.borrow_date else "",
                "应还日期": record.due_date.strftime("%Y-%m-%d") if record.due_date else "",
                "归还日期": record.return_date.strftime("%Y-%m-%d") if record.return_date else "",
                "状态": record.status,
                "续借次数": record.renew_count,
                "逾期天数": record.overdue_days,
                "罚款金额": float(record.fine_amount) if record.fine_amount else 0,
            }
            data.append(row)

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="借阅记录")

        output.seek(0)
        return output
