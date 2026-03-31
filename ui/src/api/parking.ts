import axios from 'axios'

function getStoredToken(): string | null {
  try {
    const raw = window.localStorage.getItem('auth_token')
    if (!raw) return null
    try {
      const val = JSON.parse(raw)
      return typeof val === 'string' ? val : raw
    } catch {
      return raw
    }
  } catch {
    return null
  }
}

axios.interceptors.request.use((config) => {
  const token = getStoredToken()
  const headers: any = config.headers || {}

  if (typeof headers.set === 'function') {
    headers.set('Accept', 'application/json')
    if (token) headers.set('Authorization', `Token ${token}`)
    config.headers = headers
    return config
  }

  headers.Accept = headers.Accept || 'application/json'
  if (token) headers.Authorization = headers.Authorization || `Token ${token}`
  config.headers = headers
  return config
})

const BASE = '/api/parking'

// ── 停车场 ──────────────────────────────────────────────────────────────────
export const lotApi = {
  list: (params?: Record<string, any>) => axios.get(`${BASE}/lots/`, { params }),
  create: (data: any) => axios.post(`${BASE}/lots/`, data),
  get: (id: number) => axios.get(`${BASE}/lots/${id}/`),
  update: (id: number, data: any) => axios.patch(`${BASE}/lots/${id}/`, data),
  delete: (id: number) => axios.delete(`${BASE}/lots/${id}/`),
  dashboard: (id: number) => axios.get(`${BASE}/lots/${id}/dashboard/`),
}

// ── 摄像头 ──────────────────────────────────────────────────────────────────
export const cameraApi = {
  list: (params?: Record<string, any>) => axios.get(`${BASE}/cameras/`, { params }),
  create: (data: any) => axios.post(`${BASE}/cameras/`, data),
  get: (id: number) => axios.get(`${BASE}/cameras/${id}/`),
  update: (id: number, data: any) => axios.patch(`${BASE}/cameras/${id}/`, data),
  delete: (id: number) => axios.delete(`${BASE}/cameras/${id}/`),
}

// ── 车位 ──────────────────────────────────────────────────────────────────
export const spaceApi = {
  list: (params?: Record<string, any>) => axios.get(`${BASE}/spaces/`, { params }),
  create: (data: any) => axios.post(`${BASE}/spaces/`, data),
  get: (id: number) => axios.get(`${BASE}/spaces/${id}/`),
  update: (id: number, data: any) => axios.patch(`${BASE}/spaces/${id}/`, data),
  delete: (id: number) => axios.delete(`${BASE}/spaces/${id}/`),
  updateStatus: (id: number, status: string) => axios.patch(`${BASE}/spaces/${id}/status/`, { status }),
}

// ── 车辆记录 ──────────────────────────────────────────────────────────────────
export const vehicleApi = {
  list: (params?: Record<string, any>) => axios.get(`${BASE}/vehicles/`, { params }),
  entry: (data: any) => axios.post(`${BASE}/vehicles/entry/`, data),
  exit: (data: any) => axios.post(`${BASE}/vehicles/exit/`, data),
}

// ── 停车会话 ──────────────────────────────────────────────────────────────────
export const sessionApi = {
  list: (params?: Record<string, any>) => axios.get(`${BASE}/sessions/`, { params }),
  get: (id: number) => axios.get(`${BASE}/sessions/${id}/`),
  pay: (id: number) => axios.patch(`${BASE}/sessions/${id}/`),
}

// ── 违规记录 ──────────────────────────────────────────────────────────────────
export const violationApi = {
  list: (params?: Record<string, any>) => axios.get(`${BASE}/violations/`, { params }),
  create: (data: any) => axios.post(`${BASE}/violations/`, data),
  resolve: (id: number, remark = '') => axios.patch(`${BASE}/violations/${id}/resolve/`, { remark }),
}

// ── 计费规则 ──────────────────────────────────────────────────────────────────
export const billingApi = {
  list: (params?: Record<string, any>) => axios.get(`${BASE}/billing-rules/`, { params }),
  create: (data: any) => axios.post(`${BASE}/billing-rules/`, data),
  update: (id: number, data: any) => axios.patch(`${BASE}/billing-rules/${id}/`, data),
  delete: (id: number) => axios.delete(`${BASE}/billing-rules/${id}/`),
}

// ── 统计 ──────────────────────────────────────────────────────────────────────
export const statsApi = {
  overview: () => axios.get(`${BASE}/stats/overview/`),
  hourly: () => axios.get(`${BASE}/stats/hourly/`),
  revenue: (period: 'daily' | 'monthly' = 'daily') => axios.get(`${BASE}/stats/revenue/`, { params: { period } }),
}
