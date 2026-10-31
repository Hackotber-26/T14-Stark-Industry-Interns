import { useCallback, useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet'
import { latLngBounds } from 'leaflet'
import { AlertTriangle, ArrowUpRight, ClipboardList, LoaderCircle, MapPin, RotateCcw } from 'lucide-react'
import { api, isFixture, mockMode } from './api'
import type { VerifyResult, Verdict } from './api'
import { hasCoordinates, summarizeWards } from './ledgerMetrics'
import { friendlyError } from './presentation'
import 'leaflet/dist/leaflet.css'

const colors: Record<Verdict, string> = { FIXED: 'var(--fixed)', PARTIAL: 'var(--partial)', NOT_FIXED: 'var(--not-fixed)', SUSPICIOUS: 'var(--suspicious)', NEEDS_REVIEW: 'var(--needs-review)' }
const labels: Record<Verdict, string> = { FIXED: 'Fixed', PARTIAL: 'Partial', NOT_FIXED: 'Not fixed', SUSPICIOUS: 'Suspicious', NEEDS_REVIEW: 'Needs review' }

function MapBounds({ results }: { results: VerifyResult[] }) {
  const map = useMap()
  useEffect(() => {
    if (!results.length) return
    const bounds = latLngBounds(results.map(result => [result.location!.lat, result.location!.lon]))
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16, animate: false })
  }, [map, results])
  return null
}

export default function Ledger({ onOpen }: { onOpen: (result: VerifyResult) => void }) {
  const [results, setResults] = useState<VerifyResult[]>([])
  const [loading, setLoading] = useState(true), [error, setError] = useState('')
  const [includeDemo, setIncludeDemo] = useState(mockMode)
  const [tilesFailed, setTilesFailed] = useState(false)
  const load = useCallback(async (active: () => boolean = () => true) => {
    try { const data = await api.results(); if (active()) { setResults(data); setError('') } }
    catch (e) { if (active()) setError(friendlyError(e, 'ledger')) }
    finally { if (active()) setLoading(false) }
  }, [])
  useEffect(() => {
    let active = true
    void Promise.resolve().then(() => { if (active) void load(() => active) })
    return () => { active = false }
  }, [load])
  function refresh() { setLoading(true); setError(''); void load() }
  const visible = useMemo(() => results.filter(result => includeDemo || !result.simulated).sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at)), [results, includeDemo])
  const wards = useMemo(() => summarizeWards(visible), [visible])
  const mapped = useMemo(() => visible.filter(hasCoordinates), [visible])
  const complaints = wards.reduce((sum, ward) => sum + ward.total, 0)
  const failed = wards.reduce((sum, ward) => sum + ward.failed, 0)
  const pending = wards.reduce((sum, ward) => sum + ward.pending, 0)
  return <motion.section className="ledger" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .25 }}>
    <div className="section-heading ledger-heading"><div><div className="eyebrow">PUBLIC EVIDENCE, AT A GLANCE</div><h1>The verification ledger.</h1><p>Follow repair claims across wards. Inspect the evidence behind every verdict.</p></div><button className="toggle" disabled={loading} onClick={refresh}><RotateCcw size={15} className={loading ? 'spin' : ''} />Refresh</button></div>
    <div className="ledger-controls"><label><input type="checkbox" checked={includeDemo} onChange={event => setIncludeDemo(event.target.checked)} />Include simulated demo results</label><span>{visible.length} verification{visible.length === 1 ? '' : 's'}</span></div>
    {mockMode && <div className="ledger-notice">Mock preview: all data and map positions are illustrative fixtures.</div>}
    {includeDemo && !mockMode && <div className="ledger-notice">Simulated demo results are included in the table, map and ward statistics.</div>}
    {error && <div className="error-card" role="alert"><AlertTriangle size={22} /><div><strong>Could not refresh the ledger</strong><p>{error}{results.length ? ' Previously loaded results remain below.' : ''}</p></div><button disabled={loading} onClick={refresh}><RotateCcw size={16} />Retry</button></div>}
    {loading && !results.length ? <div className="card ledger-empty" role="status"><LoaderCircle className="spin" size={28} /><h2>Loading the evidence…</h2></div> : <>
      <div className="ledger-stats"><div className="card"><span>Submitted complaints</span><strong>{complaints}</strong><small>Latest verification per complaint</small></div><div className="card"><span>Failed verification</span><strong className="failed-number">{failed}</strong><small>Partial, not fixed or suspicious</small></div><div className="card"><span>Awaiting review</span><strong>{pending}</strong><small>Kept separate from failed checks</small></div></div>
      <section className="card ledger-map-card"><div className="section-heading"><div><h2><MapPin size={19} />Repair claims on the map</h2><p>{mapped.length} located verification{mapped.length === 1 ? '' : 's'} · {visible.length - mapped.length} without valid coordinates</p></div></div>
        {mapped.length ? <div className="ledger-map"><MapContainer center={[mapped[0].location!.lat, mapped[0].location!.lon]} zoom={14} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}><TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' eventHandlers={{ tileerror: () => setTilesFailed(true) }} /><MapBounds results={mapped} />{mapped.map(result => <CircleMarker key={result.id} center={[result.location!.lat, result.location!.lon]} radius={9} pathOptions={{ color: colors[result.verdict], fillColor: colors[result.verdict], fillOpacity: .8, weight: 3 }}><Popup><div className="ledger-popup"><strong>{result.complaint_id}</strong><span style={{ color: colors[result.verdict] }}>{labels[result.verdict]}</span><span>{result.location!.ward || 'Unassigned ward'}</span><span>{result.percent_resolved === null ? 'Not scored' : `${result.percent_resolved}% repaired`}</span>{result.simulated && <small>Simulated repair (demo)</small>}<button onClick={() => onOpen(result)}>View evidence <ArrowUpRight size={14} /></button></div></Popup></CircleMarker>)}</MapContainer></div> : <div className="map-empty"><MapPin size={28} /><p>No mapped results yet.</p><span>Results with valid GPS coordinates will appear here.</span></div>}
        {tilesFailed && <p className="tile-warning" role="status">Map tiles could not load. OpenStreetMap needs an internet connection; the result table remains available.</p>}
        <div className="map-legend">{Object.entries(colors).map(([verdict, color]) => <span key={verdict}><i style={{ background: color }} />{labels[verdict as Verdict]}</span>)}</div>
      </section>
      <section className="card ward-section"><div className="section-heading"><div><h2>Which wards need another look?</h2><p>Share of submitted “resolved” claims that failed verification.</p></div></div><p className="metric-note">The API has no closure-status field, so each submitted complaint is treated as a resolved claim. We count its latest verification: partial, not fixed and suspicious are failures; needs review remains pending in the denominator. {includeDemo ? 'Simulated results are included.' : 'Simulated results are excluded.'}</p>
        {wards.length ? <div className="ward-grid">{wards.map(ward => <article className="ward-card" key={ward.ward}><div><strong>{ward.ward}</strong><span>{ward.failurePercent}%</span></div><div className="ward-meter" role="meter" aria-label={`${ward.ward} failed verification rate`} aria-valuenow={ward.failurePercent} aria-valuemin={0} aria-valuemax={100}><motion.div initial={{ width: 0 }} animate={{ width: `${ward.failurePercent}%` }} transition={{ duration: .35 }} /></div><p>{ward.failed} failed / {ward.total} complaint{ward.total === 1 ? '' : 's'} · {ward.pending} pending</p></article>)}</div> : <p className="ledger-empty-text">No complaints in this view yet.</p>}
      </section>
      <section className="card ledger-table-card"><div className="section-heading"><div><h2><ClipboardList size={19} />Every verification, on record</h2><p>Newest first. Repeated submissions remain visible here.</p></div></div>{visible.length ? <div className="table-scroll" tabIndex={0} role="region" aria-label="Verification results; scroll horizontally for all columns"><table><caption className="sr-only">Verification results, newest first</caption><thead><tr><th scope="col">Complaint</th><th scope="col">Ward</th><th scope="col">Verdict</th><th scope="col">Repaired</th><th scope="col">Confidence</th><th scope="col">Verified at</th><th scope="col">Evidence</th></tr></thead><tbody>{visible.map(result => <tr key={result.id}><td><strong>{result.complaint_id}</strong><small>{result.simulated ? 'Simulated repair (demo)' : result.id}{isFixture(result) ? ' · Mock fixture' : ''}</small></td><td>{result.location?.ward || 'Unassigned ward'}</td><td><span className="ledger-verdict" style={{ color: `color-mix(in srgb, ${colors[result.verdict]} 90%, var(--text))`, borderColor: colors[result.verdict], background: `color-mix(in srgb, ${colors[result.verdict]} 10%, var(--surface))` }}>{labels[result.verdict]}</span></td><td>{result.percent_resolved === null ? '—' : `${result.percent_resolved}%`}</td><td>{Math.round(result.confidence * 100)}%</td><td><time dateTime={result.created_at}>{Number.isFinite(Date.parse(result.created_at)) ? new Date(result.created_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : 'Unavailable'}</time></td><td><button className="text-button" onClick={() => onOpen(result)} aria-label={`View evidence for ${result.complaint_id}`}>View<ArrowUpRight size={14} /></button></td></tr>)}</tbody></table></div> : <div className="ledger-empty"><ClipboardList size={28} /><h3>No verification results yet.</h3><p>{results.length ? 'Enable simulated results to inspect demo records.' : 'Run a repair verification, then refresh this page.'}</p></div>}</section>
    </>}
  </motion.section>
}
