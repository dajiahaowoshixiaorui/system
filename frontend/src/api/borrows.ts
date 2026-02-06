import request from './request'
import { BorrowRecord, BorrowCreateParams, ReturnParams, PaginatedResponse } from '../types'

export const borrowsApi = {
  getList: (params?: {
    page?: number
    page_size?: number
    user_id?: number
    book_id?: number
    status?: string
    start_date?: string
    end_date?: string
  }) =>
    request.get<PaginatedResponse<BorrowRecord>>('/borrows', { params }),

  getMyBorrows: (params?: {
    page?: number
    page_size?: number
    status?: string
  }) =>
    request.get<PaginatedResponse<BorrowRecord>>('/borrows/my', { params }),

  getOverdue: (params?: {
    page?: number
    page_size?: number
  }) =>
    request.get<PaginatedResponse<BorrowRecord>>('/borrows/overdue', { params }),

  getStatistics: () =>
    request.get<{
      total_borrow_count: number
      total_return_count: number
      total_overdue_count: number
      total_fine_amount: number
      popular_books: { id: number; title: string; borrow_count: number }[]
      active_users: { id: number; username: string; borrow_count: number }[]
    }>('/borrows/statistics'),

  borrow: (data: BorrowCreateParams) =>
    request.post<BorrowRecord>('/borrows', data),

  return: (data: ReturnParams) =>
    request.post<BorrowRecord>('/borrows/return', data),

  renew: (record_id: number) =>
    request.post<BorrowRecord>('/borrows/renew', { record_id }),
}
