import type { VerifyResult } from './api'

export interface WardSummary {
  ward: string
  total: number
  failed: number
  pending: number
  failurePercent: number
}

/** Count the latest verification per complaint so retries do not inflate rates. */
export function summarizeWards(results: VerifyResult[]): WardSummary[] {
  const latest = new Map<string, VerifyResult>()
  for (const result of results) {
    const key = result.complaint_id || result.id
    const existing = latest.get(key)
    if (!existing || Date.parse(result.created_at) > Date.parse(existing.created_at)) latest.set(key, result)
  }
  const wards = new Map<string, WardSummary>()
  for (const result of latest.values()) {
    const ward = result.location?.ward?.trim() || 'Unassigned ward'
    const summary = wards.get(ward) ?? { ward, total: 0, failed: 0, pending: 0, failurePercent: 0 }
    summary.total++
    if (['PARTIAL', 'NOT_FIXED', 'SUSPICIOUS'].includes(result.verdict)) summary.failed++
    if (result.verdict === 'NEEDS_REVIEW') summary.pending++
    summary.failurePercent = Math.round(1000 * summary.failed / summary.total) / 10
    wards.set(ward, summary)
  }
  return [...wards.values()].sort((a, b) => b.failurePercent - a.failurePercent || a.ward.localeCompare(b.ward))
}

export function hasCoordinates(result: VerifyResult): boolean {
  const location = result.location
  return !!location && Number.isFinite(location.lat) && Number.isFinite(location.lon) && Math.abs(location.lat) <= 90 && Math.abs(location.lon) <= 180
}
