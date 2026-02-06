import request from './request'
import { Category, CategoryCreateParams, PaginatedResponse } from '../types'

export const categoriesApi = {
  getList: (params?: {
    page?: number
    page_size?: number
    name?: string
    parent_id?: number
    is_active?: boolean
  }) =>
    request.get<PaginatedResponse<Category>>('/categories', { params }),

  getAll: () =>
    request.get<Category[]>('/categories/all'),

  getDetail: (id: number) =>
    request.get<Category>(`/categories/${id}`),

  create: (data: CategoryCreateParams) =>
    request.post<Category>('/categories', data),

  update: (id: number, data: Partial<CategoryCreateParams>) =>
    request.put<Category>(`/categories/${id}`, data),

  delete: (id: number) =>
    request.delete(`/categories/${id}`),
}
