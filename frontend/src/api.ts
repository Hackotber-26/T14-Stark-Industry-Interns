import fixed from './mocks/fixed.json'
import partial from './mocks/partial.json'
import notFixed from './mocks/not-fixed.json'
import suspicious from './mocks/suspicious.json'
import reused from './mocks/reused.json'
import demoCatalog from './mocks/demos.json'

export type Verdict = 'FIXED' | 'PARTIAL' | 'NOT_FIXED' | 'SUSPICIOUS' | 'NEEDS_REVIEW'
export type ROI = [number, number][]
export interface CheckResult {
  status: 'pass' | 'warn' | 'fail' | 'skipped'; detail: string
  distance_m?: number | null; inliers?: number | null; inlier_ratio?: number | null
  matched_complaint_id?: string | null; hamming?: number | null; score?: number | null
}
export interface VerifyResult {
  id: string; complaint_id: string; case_id: string | null; simulated: boolean
  verdict: Verdict; confidence: number; percent_resolved: number | null; reasons: string[]
  checks: Record<'location' | 'duplicate' | 'scene' | 'quality', CheckResult>
  explanation: { en: string; kn: string }
  images: { before: string; after: string; after_aligned: string | null; heatmap: string | null }
  roi: ROI | null; roi_source: 'marked' | 'model' | null
  location: { lat: number; lon: number; ward: string } | null
  timings_ms: Record<string, number>; created_at: string
}
export interface DemoCase {
  case_id: string; title: string; expected: Verdict; simulated: boolean
  ward: string; before_url: string; after_url: string
}
export const mockMode = import.meta.env.VITE_MOCK === '1'
export const apiBase = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')
const fixtures = [fixed, partial, notFixed, suspicious, reused] as unknown as VerifyResult[]
const cachedResults = new Map(fixtures.map(result => [result.case_id!, result]))
let offline = false
export const isOffline = () => offline
export const isFixture = (result: VerifyResult) => result.id.startsWith('mock_')
export const imageUrl = (url: string) => url.startsWith('/mock/') || /^(blob:|data:|https?:)/.test(url) ? url : `${apiBase}${url.startsWith('/') ? '' : '/'}${url}`

export class ApiError extends Error {
  status: number
  roiRequired: boolean
  constructor(message: string, status: number, roiRequired = false) {
    super(message); this.status = status; this.roiRequired = roiRequired
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${apiBase}${path}`, { ...init, signal: AbortSignal.timeout(15000) })
  } catch {
    offline = true
    throw new ApiError('Cannot reach the local backend. Check that it is running on port 8000, then retry.', 0)
  }
  offline = false
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    const message = typeof detail === 'string' ? detail : Array.isArray(detail)
      ? detail.map((item: { loc?: string[]; msg?: string }) => `${item.loc?.slice(1).join('.') ?? 'Input'}: ${item.msg ?? 'Invalid value'}`).join('; ')
      : `Request failed (${response.status}). Please try again.`
    const roiRequired = response.status === 422 && (/mark the pothole|\broi\b/i.test(message))
    throw new ApiError(message, response.status, roiRequired)
  }
  return response.json() as Promise<T>
}

function mockDemos(): DemoCase[] {
  return structuredClone(demoCatalog) as DemoCase[]
}


export const api = {
  health: () => request<{ ok: boolean; model_loaded: boolean; mock_seg: boolean }>('/api/health'),
  demos: async (): Promise<DemoCase[]> => {
    if (mockMode) return mockDemos()
    try {
      const demos = await request<DemoCase[]>('/api/demo')
      return demos.map(demo => demo.case_id === 'case_05' ? { ...demo, title: 'Reused photo', expected: 'SUSPICIOUS' } : demo)
    } catch (error) {
      if (error instanceof ApiError && error.status === 0) return mockDemos()
      throw error
    }
  },
  demoVerify: async (id: string): Promise<VerifyResult> => {
    if (!mockMode) {
      try {
        const result = await request<VerifyResult>(`/api/demo/${encodeURIComponent(id)}/verify`, { method: 'POST' })
        cachedResults.set(id, result)
        return result
      } catch (error) {
        if (!(error instanceof ApiError) || error.status !== 0) throw error
      }
    }
    const result = cachedResults.get(id)
    if (!result) throw new Error('No cached result for this demo case. Reconnect the backend and retry.')
    return structuredClone(result)
  },
  suggest: async (before: File): Promise<{ roi: ROI | null; confidence: number }> => {
    if (mockMode) return { roi: null, confidence: 0 }
    const body = new FormData(); body.append('before', before)
    return request('/api/suggest-roi', { method: 'POST', body })
  },
  verify: async (body: FormData): Promise<VerifyResult> => {
    if (mockMode) throw new Error('Upload verification needs the local backend. Mock mode only previews labeled demo results.')
    return request('/api/verify', { method: 'POST', body })
  },
  results: (): Promise<VerifyResult[]> => mockMode ? Promise.resolve(structuredClone(fixtures)) : request('/api/results'),
  result: async (id: string): Promise<VerifyResult> => {
    if (!mockMode) return request(`/api/results/${encodeURIComponent(id)}`)
    const result = fixtures.find(r => r.id === id)
    if (!result) throw new Error('Result not found')
    return structuredClone(result)
  },
}
