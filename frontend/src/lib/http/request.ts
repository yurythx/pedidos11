import { api } from './axios'
import axios, { AxiosRequestConfig } from 'axios'

export type HttpError = {
  status: number | null
  message: string
  code?: string | null
  details?: unknown
}

const toHttpError = (err: unknown): HttpError => {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status ?? null
    const message =
      (err.response?.data as any)?.detail ||
      (err.response?.data as any)?.message ||
      err.message ||
      'Erro de requisição'
    const code = (err.response?.data as any)?.code ?? null
    return { status, message, code, details: err.response?.data }
  }
  return { status: null, message: 'Erro desconhecido', code: null, details: err }
}

export const request = {
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const res = await api.get<T>(url, config)
      return res.data
    } catch (err) {
      throw toHttpError(err)
    }
  },
  async post<T, B = unknown>(url: string, body?: B, config?: AxiosRequestConfig): Promise<T> {
    try {
      const res = await api.post<T>(url, body, config)
      return res.data
    } catch (err) {
      throw toHttpError(err)
    }
  },
  async put<T, B = unknown>(url: string, body?: B, config?: AxiosRequestConfig): Promise<T> {
    try {
      const res = await api.put<T>(url, body, config)
      return res.data
    } catch (err) {
      throw toHttpError(err)
    }
  },
  async patch<T, B = unknown>(url: string, body?: B, config?: AxiosRequestConfig): Promise<T> {
    try {
      const res = await api.patch<T>(url, body, config)
      return res.data
    } catch (err) {
      throw toHttpError(err)
    }
  },
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const res = await api.delete<T>(url, config)
      return res.data
    } catch (err) {
      throw toHttpError(err)
    }
  },
}

