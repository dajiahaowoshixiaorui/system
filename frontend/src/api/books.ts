import request from './request'
import { Book, BookCreateParams, BookQuery, PaginatedResponse } from '../types'

export const booksApi = {
  getList: (params: BookQuery) =>
    request.get<PaginatedResponse<Book>>('/books', { params }),

  getDetail: (id: number) =>
    request.get<Book>(`/books/${id}`),

  create: (data: BookCreateParams) =>
    request.post<Book>('/books', data),

  update: (id: number, data: Partial<BookCreateParams>) =>
    request.put<Book>(`/books/${id}`, data),

  delete: (id: number) =>
    request.delete(`/books/${id}`),

  search: (params: {
    keyword: string
    category_id?: number
    page?: number
    page_size?: number
  }) =>
    request.get<PaginatedResponse<Book>>('/books/search/elasticsearch', { params }),

  uploadCover: (id: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post(`/books/${id}/cover`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
