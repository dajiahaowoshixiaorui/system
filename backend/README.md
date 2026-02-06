# 图书管理系统后端

## 技术栈
- FastAPI + SQLAlchemy + MySQL
- JWT认证 + Redis缓存 + Elasticsearch搜索
- openpyxl + Pandas Excel处理

## 目录结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # 应用入口
│   ├── config.py                  # 配置管理
│   ├── database.py                # 数据库连接
│   ├── models/                    # 数据模型
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── user.py
│   │   └── borrow.py
│   ├── schemas/                   # Pydantic模式
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── user.py
│   │   └── borrow.py
│   ├── api/                       # API路由
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── categories.py
│   │   ├── borrows.py
│   │   └── users.py
│   ├── services/                  # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── search.py
│   │   └── excel.py
│   ├── middleware/                # 中间件
│   │   ├── __init__.py
│   │   └── auth.py
│   └── utils/                     # 工具
│       ├── __init__.py
│       └── constants.py
├── requirements── .env.example.txt
└
```



