"""借阅相关数据模型"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class BorrowStatus(PyEnum):
    """借阅状态枚举"""
    BORROWED = "borrowed"       # 借出中
    RETURNED = "returned"       # 已归还
    OVERDUE = "overdue"         # 逾期
    LOST = "lost"               # 丢失


class BorrowRecord(Base):
    """借阅记录模型"""
    __tablename__ = "borrow_records"
    __table_args__ = (
        {"comment": "借阅记录表"},
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, comment="图书ID")

    borrow_date = Column(DateTime, default=datetime.utcnow, comment="借出日期")
    due_date = Column(DateTime, nullable=False, comment="应还日期")
    return_date = Column(DateTime, nullable=True, comment="实际归还日期")

    status = Column(String(20), default="borrowed", comment="状态")
    renew_count = Column(Integer, default=0, comment="续借次数")
    max_renew_count = Column(Integer, default=2, comment="最大续借次数")

    overdue_days = Column(Integer, default=0, comment="逾期天数")
    fine_amount = Column(Numeric(10, 2), default=0.00, comment="罚款金额")

    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="操作员ID")
    remark = Column(Text, nullable=True, comment="备注")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="borrow_records", foreign_keys=[user_id])
    book = relationship("Book", back_populates="borrow_records")
    operator = relationship("User", foreign_keys=[operator_id])

    def __repr__(self):
        return f"<BorrowRecord(id={self.id}, user_id={self.user_id}, book_id={self.book_id}, status='{self.status}')>"

    @property
    def is_overdue(self) -> bool:
        """检查是否逾期"""
        if self.status == "returned":
            return False
        from datetime import datetime
        return datetime.utcnow() > self.due_date

    @property
    def can_renew(self) -> bool:
        """检查是否可以续借"""
        return (
            self.status == "borrowed"
            and self.renew_count < self.max_renew_count
        )
