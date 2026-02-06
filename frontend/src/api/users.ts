import request from './request'
import { User, PaginatedResponse } from '../types'

export const usersApi = {
  getList: (params?: {
    page?: number
    page_size?: number
    keyword?: string
    role?: string
    status?: string
  }) =>
    request.get<PaginatedResponse<User>>('/users', { params }),

  getDetail: (id: number) =>
    request.get<User>(`/users/${id}`),

  create: (data: {
    username: string
    email: string
    password: string
    phone?: string
    full_name?: string
    role: string
    max_borrow_count?: number
  }) =>
    request.post<User>('/users', data),

  update: (id: number, data: Partial<{
    email: string
    phone: string
    full_name: string
    status: string
    max_borrow_count: number
  }>) =>
    request.put<User>(`/users/${id}`, data),

  delete: (id: number) =>
    request.delete(`/users/${id}`),

  updatePassword: (id: number, data: {
    old_password: string
    new_password: string
  }) =>
    request.put(`/users/${id}/password`, data),

  updateStatus: (id: number, status: string) =>
    request.put(`/users/${id}/status`, { status }),

  updateRole: (id: number, role: string) =>
    request.put(`/users/${id}/role`, { role }),
}
