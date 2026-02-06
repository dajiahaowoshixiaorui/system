// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  phone?: string
  full_name?: string
  avatar_url?: string
  role: 'admin' | 'librarian' | 'user'
  status: 'active' | 'inactive' | 'suspended'
  max_borrow_count: number
  current_borrow_count: number
  last_login_at?: string
  created_at: string
  updated_at: string
}

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// 图书相关类型
export interface Book {
  id: number
  isbn: string
  title: string
  author: string
  publisher?: string
  publish_date?: string
  price: number
  category_id?: number
  category_name?: string
  summary?: string
  cover_url?: string
  total_stock: number
  available_stock: number
  borrow_count: number
  status: string
  location?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface BookCreateParams {
  isbn: string
  title: string
  author: string
  publisher?: string
  publish_date?: string
  price: number
  category_id?: number
  summary?: string
  cover_url?: string
  total_stock: number
  location?: string
}

export interface BookQuery {
  page: number
  page_size: number
  keyword?: string
  category_id?: number
  author?: string
  status?: string
  is_active?: boolean
}

// 分类相关类型
export interface Category {
  id: number
  name: string
  description?: string
  parent_id?: number
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CategoryCreateParams {
  name: string
  description?: string
  parent_id?: number
  sort_order?: number
}

// 借阅相关类型
export interface BorrowRecord {
  id: number
  user_id: number
  book_id: number
  user_name?: string
  book_title?: string
  book_isbn?: string
  borrow_date: string
  due_date: string
  return_date?: string
  status: 'borrowed' | 'returned' | 'overdue' | 'lost'
  renew_count: number
  max_renew_count: number
  overdue_days: number
  fine_amount: number
  remark?: string
  created_at: string
  updated_at: string
}

export interface BorrowCreateParams {
  user_id: number
  book_id: number
  due_days?: number
}

export interface ReturnParams {
  record_id: number
  remark?: string
}

// API响应类型
export interface Response<T> {
  code: number
  status: 'success' | 'error'
  message: string
  data?: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
