import type { ApiError, ApiResponse } from "@/types/api"

function getApiBaseUrl(): string {
  const raw = (import.meta.env.VITE_API_BASE_URL as string | undefined) || ""
  return raw.replace(/\/+$/, "")
}

function buildUrl(path: string): string {
  const base = getApiBaseUrl()
  if (!base) return path
  if (path.startsWith("http://") || path.startsWith("https://")) return path
  return base + path
}

function getStoredToken(): string | null {
  try {
    const raw = window.localStorage.getItem("auth_token")
    if (!raw) return null
    try {
      const val = JSON.parse(raw)
      return typeof val === "string" ? val : raw
    } catch {
      return raw
    }
  } catch {
    return null
  }
}

function createApiError(msg: string, httpStatus: number, code: number, data?: unknown): ApiError {
  return Object.assign(new Error(msg), { httpStatus, code, data })
}

async function parseJson<T>(resp: Response): Promise<T> {
  const text = await resp.text()
  if (!text) return {} as T
  return JSON.parse(text) as T
}

export async function requestR<T>(path: string, init?: RequestInit): Promise<T> {
  const url = buildUrl(path)
  const token = getStoredToken()
  const headers = new Headers(init?.headers || {})
  headers.set("Accept", "application/json")
  if (token) headers.set("Authorization", `Token ${token}`)

  const resp = await fetch(url, { ...init, headers })
  const isJson = (resp.headers.get("content-type") || "").includes("application/json")
  if (!isJson) {
    throw createApiError("响应不是 JSON", resp.status, -1)
  }
  const payload = await parseJson<ApiResponse<T>>(resp)
  if (resp.status >= 400) {
    throw createApiError(payload.msg || "请求失败", resp.status, payload.code || resp.status, payload.data)
  }
  if (payload.code !== 20001) {
    throw createApiError(payload.msg || "业务失败", resp.status, payload.code, payload.data)
  }
  return payload.data
}

export async function requestRJson<T>(path: string, method: string, body?: unknown): Promise<T> {
  const headers = new Headers()
  headers.set("Content-Type", "application/json")
  return requestR<T>(path, {
    method,
    body: body === undefined ? undefined : JSON.stringify(body),
    headers,
  })
}

export async function requestRForm<T>(path: string, method: string, formData: FormData): Promise<T> {
  return requestR<T>(path, { method, body: formData })
}

export async function downloadBlob(path: string): Promise<{ blob: Blob; filename: string }> {
  const url = buildUrl(path)
  const token = getStoredToken()
  const headers = new Headers()
  if (token) headers.set("Authorization", `Token ${token}`)

  const resp = await fetch(url, { method: "GET", headers })
  if (resp.status >= 400) {
    const isJson = (resp.headers.get("content-type") || "").includes("application/json")
    if (isJson) {
      const payload = await parseJson<ApiResponse<unknown>>(resp)
      throw createApiError(payload.msg || "下载失败", resp.status, payload.code || resp.status, payload.data)
    }
    throw createApiError("下载失败", resp.status, resp.status)
  }

  const cd = resp.headers.get("content-disposition") || ""
  const m = /filename\\*=UTF-8''([^;]+)|filename=\"?([^\";]+)\"?/i.exec(cd)
  const rawName = decodeURIComponent((m?.[1] || m?.[2] || "download").trim())
  const blob = await resp.blob()
  return { blob, filename: rawName }
}

