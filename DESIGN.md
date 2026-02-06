# 图书管理系统 - 关键设计说明

## 一、数据表关系说明

### 1. ER图关系

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    users    │       │    books    │       │  categories │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ username    │       │ isbn        │◄──────│ name        │
│ email       │       │ title       │       │ parent_id   │
│ password    │       │ author      │       │ ...         │
│ role        │       │ category_id │──────►│             │
│ ...         │       │ ...         │       │             │
└─────────────┘       └─────────────┘       └─────────────┘
       │                     │
       │                     │
       └─────────┬───────────┘
                 │
                 ▼
       ┌─────────────────────┐
       │  borrow_records     │
       ├─────────────────────┤
       │ id (PK)             │
       │ user_id (FK)        │
       │ book_id (FK)        │
       │ borrow_date         │
       │ due_date            │
       │ return_date         │
       │ status              │
       │ fine_amount         │
       └─────────────────────┘
```

### 2. 关系说明

| 关系类型 | 说明 |
|---------|------|
| **User - BorrowRecord** | 一对多关系。用户可以有多个借阅记录 |
| **Book - BorrowRecord** | 一对多关系。图书可以有多个借阅记录 |
| **Category - Book** | 一对多关系。分类下可以有多个图书 |
| **Category - Category** | 自关联。分类可以有父分类（无限层级） |
| **User - User (operator)** | 自关联。借阅记录的操作员也是用户 |

### 3. 外键约束

- `books.category_id` -> `categories.id` (可空，支持无分类图书)
- `borrow_records.user_id` -> `users.id` (必须)
- `borrow_records.book_id` -> `books.id` (必须)
- `categories.parent_id` -> `categories.id` (可空，支持顶级分类)
- `borrow_records.operator_id` -> `users.id` (可空，记录创建时赋值)

---

## 二、搜索与缓存使用原则

### 1. 缓存策略

#### 缓存分层

```
┌─────────────────────────────────────────────┐
│             应用层 (Zustand/Redux)           │
│  - 用户状态、会话信息、UI状态                │
├─────────────────────────────────────────────┤
│           Redis 缓存层                       │
│  - 热点数据（图书详情、分类列表）            │
│  - 接口响应缓存                              │
│  - Token/JWT                                │
├─────────────────────────────────────────────┤
│           MySQL 数据库层                     │
│  - 持久化存储                               │
│  - 精确查询、事务操作                        │
├─────────────────────────────────────────────┤
│         Elasticsearch 搜索层                 │
│  - 全文搜索                                 │
│  - 模糊匹配                                 │
│  - 多条件复合查询                           │
└─────────────────────────────────────────────┘
```

#### 缓存Key设计

| Key Pattern | 说明 | 过期时间 |
|-------------|------|----------|
| `book:{id}` | 图书详情 | 5分钟 |
| `books:list:{hash}` | 图书列表 | 2分钟 |
| `category:all` | 全部分类列表 | 30分钟 |
| `user:{id}` | 用户信息 | 30分钟 |
| `stats:*` | 统计数据 | 1小时 |

#### 缓存更新策略

1. **Cache-Aside模式（旁路缓存）**
   - 读取：先查Redis，MISS后查MySQL并回填Redis
   - 写入：先更新MySQL，再删除Redis缓存

2. **写操作时**
   ```python
   # 更新图书
   db.update(book)
   await redis.delete(f"book:{book_id}")
   await redis.delete_pattern("books:list:*")
   SearchService.index_book(book)  # 同步ES
   ```

3. **缓存穿透防护**
   - 空结果也缓存（设置短过期时间）
   - 使用布隆过滤器（可选）

### 2. 搜索策略

#### Elasticsearch使用场景

| 场景 | 方案 | 说明 |
|------|------|------|
| 书名/作者模糊搜索 | ES多字段匹配 | 支持错别字、拼音 |
| 分类筛选 | ES精确过滤 | 高性能 |
| 综合排序 | ES相关度+统计排序 | borrow_count降序 |
| 搜索建议 | ES前缀匹配 | 实时补全 |

#### 查询示例

```python
# 复合查询
GET /library_books/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "Python编程",
            "fields": ["title^3", "author^2", "summary"],
            "fuzziness": "AUTO"
          }
        }
      ],
      "filter": [
        {"term": {"category_id": 1}},
        {"term": {"is_active": true}}
      ]
    }
  },
  "sort": [
    {"_score": "desc"},
    {"borrow_count": "desc"}
  ]
}
```

#### 数据同步

- **写入同步**：CRUD操作后实时同步到ES
- **批量同步**：支持Excel导入时批量索引
- **全量同步**：支持重建索引

---

## 三、权限模型说明（RBAC）

### 1. 角色定义

| 角色 | 标识符 | 权限级别 | 说明 |
|------|--------|----------|------|
| 管理员 | admin | Lv.3 | 全部权限 |
| 图书管理员 | librarian | Lv.2 | 业务操作权限 |
| 普通用户 | user | Lv.1 | 基础使用权限 |

### 2. 权限矩阵

| 功能 | admin | librarian | user |
|------|-------|-----------|------|
| **图书管理** | | | |
| 查看图书列表 | ✓ | ✓ | ✓ |
| 查看图书详情 | ✓ | ✓ | ✓ |
| 新增图书 | ✓ | ✓ | ✗ |
| 编辑图书 | ✓ | ✓ | ✗ |
| 删除图书 | ✓ | ✗ | ✗ |
| **分类管理** | | | |
| 查看分类 | ✓ | ✓ | ✓ |
| 新增分类 | ✓ | ✓ | ✗ |
| 编辑分类 | ✓ | ✓ | ✗ |
| 删除分类 | ✓ | ✗ | ✗ |
| **用户管理** | | | |
| 查看用户列表 | ✓ | ✓* | ✗ |
| 新增用户 | ✓ | ✗ | ✗ |
| 编辑用户 | ✓ | ✗ | ✗ |
| 删除用户 | ✓ | ✗ | ✗ |
| **借阅管理** | | | |
| 借书 | ✓ | ✓ | ✗ |
| 还书 | ✓ | ✓ | ✗ |
| 续借 | ✓ | ✓ | ✓** |
| 查看借阅记录(全部) | ✓ | ✓ | ✗ |
| 查看个人借阅 | ✓ | ✓ | ✓ |
| **系统功能** | | | |
| 导出报表 | ✓ | ✗ | ✗ |
| 系统配置 | ✓ | ✗ | ✗ |

*图书管理员只能查看用户基本信息
**普通用户只能为自己续借

### 3. 接口级权限控制

#### 后端实现

```python
# 方式1: 依赖注入
def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

# 方式2: 中间件
class AuthMiddleware:
    async def dispatch(self, request: Request, call_next):
        # 验证Token
        # 检查角色权限
```

#### 前端实现

```typescript
// 路由守卫
function PrivateRoute({ children, requiredRole }: Props) {
  const { user } = useAuthStore()
  if (!user) return <Navigate to="/login" />
  if (requiredRole && !requiredRole.includes(user.role)) {
    return <Navigate to="/" />
  }
  return children
}

// 菜单过滤
const menuItems = [
  { key: '/users', roles: ['admin', 'librarian'] },
  { key: '/borrows', roles: ['admin', 'librarian'] },
]
```

### 4. JWT Token设计

```json
{
  "sub": 1,           // 用户ID
  "username": "admin",
  "role": "admin",
  "exp": 1704067200,  // 过期时间
  "iat": 1703980800   // 签发时间
}
```

#### Token安全策略

| 策略 | 说明 |
|------|------|
| 过期时间 | 24小时自动过期 |
| 刷新Token | 支持无感刷新（可选） |
| 单点登录 | 登录后旧Token失效 |
| HTTPS传输 | 防止中间人攻击 |
