import axios from 'axios'

export const api = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000',
})

export interface Reading {
  id?: number
  intersection_id: string
  sensor_id: string
  timestamp: string
  vehicle_count: number
  avg_speed_kmh: number
  occupancy_percent: number
  queue_length: number
  weather: string
  event: boolean
  congestion: string
}

export async function getCongestion() {
  const r = await api.get('/api/congestion')
  return r.data.congestion as any[]
}
export async function getIntersections() {
  const r = await api.get('/api/intersections')
  return r.data.intersections as any[]
}
export async function getSensors() {
  const r = await api.get('/api/sensors')
  return r.data.sensors as any[]
}
export async function getReadings(intersectionId?: string, limit = 48) {
  const r = await api.get('/api/readings', { params: { intersection_id: intersectionId, limit } })
  return r.data.readings as Reading[]
}
export async function predict(intersectionId: string, horizon: number) {
  const r = await api.post('/api/predict', { intersection_id: intersectionId, horizon_minutes: horizon })
  return r.data
}
export async function getSignals() {
  const r = await api.get('/api/signals')
  return r.data
}
export async function getAlerts() {
  const r = await api.get('/api/alerts')
  return r.data.alerts as any[]
}
export async function acknowledgeAlert(id: number) {
  const r = await api.post(`/api/alerts/${id}/acknowledge`)
  return r.data
}
export async function getReports() {
  const r = await api.get('/api/reports')
  return r.data
}
export async function getTickets() {
  const r = await api.get('/api/support/tickets')
  return r.data as any[]
}
export async function createTicket(body: any) {
  const r = await api.post('/api/support/tickets', body)
  return r.data
}
export async function updateTicket(id: number, body: any) {
  const r = await api.patch(`/api/support/tickets/${id}`, body)
  return r.data
}
export async function getSettings() {
  const r = await api.get('/api/settings')
  return r.data
}
