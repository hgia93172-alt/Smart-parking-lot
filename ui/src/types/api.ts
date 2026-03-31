export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

export interface ApiError extends Error {
  httpStatus: number
  code: number
  data?: unknown
}

export interface Paged<T> {
  count: number
  page: number
  page_size: number
  results: T[]
}

