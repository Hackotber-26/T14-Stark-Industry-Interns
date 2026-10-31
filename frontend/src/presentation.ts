/** Presentation figures supplied for the simulated evaluation. */
export const PRESENTATION_STATS = { accuracyPercent: 100, simulatedRepairs: 120, timePerCheck: '<1 s', openSourcePercent: 100 } as const

export const HOW_IT_WORKS = [
  { title: 'Location', detail: 'Confirm the photo locations.' },
  { title: 'Duplicate', detail: 'Spot reused photo evidence.' },
  { title: 'Scene match', detail: 'Check it’s the same road.' },
  { title: 'Align', detail: 'Line up both photo views.' },
  { title: 'Measure damage', detail: 'Measure the marked pothole.' },
  { title: 'Verdict', detail: 'Explain the repair outcome.' },
] as const

/** Keep service details out of public error messages. */
export function friendlyError(error: unknown, context: 'demos' | 'verify' | 'ledger' | 'reconnect'): string {
  const status = typeof error === 'object' && error !== null && 'status' in error ? error.status : undefined
  if (status === 0) return 'We couldn’t reach the verification service. Check the local connection, then try again.'
  if (status === 422) return 'Please check your photos, complaint ID and location coordinates, then try again.'
  if (context === 'demos') return 'The demo cases couldn’t load just now. Try again, or upload your own photos below.'
  if (context === 'ledger') return 'The verification records couldn’t load just now. Please try again in a moment.'
  if (context === 'reconnect') return 'We couldn’t reconnect just yet. Check that the local service is running, then try again.'
  return 'We couldn’t complete this check. Please try again, or choose another pair of clear photos.'
}
