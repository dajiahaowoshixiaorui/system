import request from './request'
import { LoginParams, LoginResponse, User } from '../types'

export const authApi = {
  login: (data: LoginParams) =>
    request.post<LoginResponse>('/auth/login', data),

  register: (data: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => request.post('/auth/register', data),

  getMe: () =>
    request.get<{ id: number; username: string; email: string; role: string }>('/auth/me'),
}
