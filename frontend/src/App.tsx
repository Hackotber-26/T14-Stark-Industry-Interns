import { useEffect, useRef, useState } from 'react'
import type { PointerEvent } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider'
import { ArrowRight, Check, CheckCircle2, ChevronLeft, Crosshair, FileImage, Fingerprint, Layers, LoaderCircle, MapPin, RotateCcw, ScanLine, ShieldCheck, Upload, X, AlertTriangle } from 'lucide-react'
import { api, ApiError, imageUrl, isFixture, isOffline, mockMode } from './api'
import { shortcutKey } from './shortcuts'
import type { DemoCase, ROI, VerifyResult, Verdict } from './api'
import './App.css'

const labels: Record<Verdict, string> = { FIXED: 'Repair verified', PARTIAL: 'Partially repaired', NOT_FIXED: 'Not repaired', SUSPICIOUS: 'Suspicious evidence', NEEDS_REVIEW: 'Needs review' }
const colors: Record<Verdict, string> = { FIXED: '#22C55E', PARTIAL: '#F59E0B', NOT_FIXED: '#EF4444', SUSPICIOUS: '#A855F7', NEEDS_REVIEW: '#94A3B8' }
const steps = ['Location', 'Duplicate', 'Scene match', 'Align', 'Detect', 'Score']

function BoxEditor({ src, roi, onChange, suggested }: { src: string; roi: ROI | null; onChange: (roi: ROI | null) => void; suggested: boolean }) {
  const start = useRef<[number, number] | null>(null)
  const previous = useRef<ROI | null>(null)
  const moving = useRef(false)
  const [drawing, setDrawing] = useState(false)
  function point(event: PointerEvent<HTMLDivElement>): [number, number] {
    const r = event.currentTarget.getBoundingClientRect()
    return [Math.max(0, Math.min(1, (event.clientX - r.left) / r.width)), Math.max(0, Math.min(1, (event.clientY - r.top) / r.height))]
  }
  function down(event: PointerEvent<HTMLDivElement>) {
    if (event.button !== 0) return
    event.preventDefault(); event.currentTarget.setPointerCapture(event.pointerId)
    start.current = point(event); previous.current = roi
    moving.current = (event.target as HTMLElement).dataset.box === 'true'
    setDrawing(true)
    if (!moving.current) onChange(null)
  }
  function move(event: PointerEvent<HTMLDivElement>) {
    if (!start.current) return
    const p = point(event), s = start.current
    if (moving.current && previous.current) {
      const box = previous.current, dx = Math.max(-box[0][0], Math.min(1 - box[2][0], p[0] - s[0])), dy = Math.max(-box[0][1], Math.min(1 - box[2][1], p[1] - s[1]))
      onChange(box.map(([x, y]) => [x + dx, y + dy]))
    } else {
      const x = Math.min(s[0], p[0]), y = Math.min(s[1], p[1]), x2 = Math.max(s[0], p[0]), y2 = Math.max(s[1], p[1])
      onChange([[x, y], [x2, y], [x2, y2], [x, y2]])
    }
  }
  function finish() { start.current = null; setDrawing(false); if (roi && (roi[2][0] - roi[0][0] < .01 || roi[2][1] - roi[0][1] < .01)) onChange(null) }
  return <div className="editor-wrap"><div className="editor" onPointerDown={down} onPointerMove={move} onPointerUp={finish} onPointerCancel={() => { start.current = null; setDrawing(false); onChange(previous.current) }} aria-label="Drag over the before photo to mark the pothole">
    <img src={src} alt="Before repair. Drag a box around the pothole." draggable={false} />
    {roi && <div data-box="true" className="roi" style={{ left: `${roi[0][0] * 100}%`, top: `${roi[0][1] * 100}%`, width: `${(roi[2][0] - roi[0][0]) * 100}%`, height: `${(roi[2][1] - roi[0][1]) * 100}%` }}><span>{drawing ? 'Adjusting box' : suggested ? 'Suggested by AI, drag to adjust' : 'Marked pothole'}</span></div>}
  </div><div className="editor-help"><span><Crosshair size={16} /> {roi ? 'Drag the box to move it, or draw again outside it.' : 'Drag a box around the pothole'}</span><button type="button" className="text-button" onClick={() => onChange(null)}>Clear box</button></div>
  <details><summary>Use coordinates instead</summary><p>Normalized coordinates (0–1). Enter opposite corners.</p><div className="coordinate-grid">{['Left', 'Top', 'Right', 'Bottom'].map((label, i) => <label key={label}>{label}<input aria-label={label + ' box coordinate'} type="number" min="0" max="1" step="0.01" value={roi ? [roi[0][0], roi[0][1], roi[2][0], roi[2][1]][i] : ''} onChange={e => { const v = roi ? [roi[0][0], roi[0][1], roi[2][0], roi[2][1]] : [0, 0, 1, 1]; v[i] = Math.max(0, Math.min(1, Number(e.target.value))); onChange([[v[0], v[1]], [v[2], v[1]], [v[2], v[3]], [v[0], v[3]]]) }} /></label>)}</div></details></div>
}

function UploadZone({ label, file, onFile }: { label: string; file: File | null; onFile: (file: File) => void }) {
  const [over, setOver] = useState(false)
  return <label className={`upload-zone ${over ? 'over' : ''}`} onDragOver={e => { e.preventDefault(); setOver(true) }} onDragLeave={() => setOver(false)} onDrop={e => { e.preventDefault(); setOver(false); if (e.dataTransfer.files[0]) onFile(e.dataTransfer.files[0]) }}><input type="file" accept="image/*" onChange={e => { if (e.target.files?.[0]) onFile(e.target.files[0]) }} /><span className="upload-icon">{file ? <FileImage /> : <Upload />}</span><strong>{file ? file.name : `${label} photo`}</strong><span>{file ? 'Click or drop to replace' : 'Drop an image or browse files'}</span><small>{label === 'Before' ? 'Original complaint evidence' : 'Submitted repair evidence'}</small></label>
}

function Result({ result, onBack }: { result: VerifyResult; onBack: () => void }) {
  const [heat, setHeat] = useState(false), [kn, setKn] = useState(false)
  const reduce = useReducedMotion()
  const color = colors[result.verdict], pct = result.percent_resolved
  useEffect(() => { const key = (e: KeyboardEvent) => { const key = shortcutKey(e); if (key === 'h') { e.preventDefault(); setHeat(v => !v) } if (key === 'k') { e.preventDefault(); setKn(v => !v) } }; window.addEventListener('keydown', key); return () => window.removeEventListener('keydown', key) }, [])
  const comparison = heat ? result.images.heatmap : result.images.after_aligned
  return <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="result">
    <div className="section-heading"><button className="text-button" onClick={onBack}><ChevronLeft size={18} /> Verify another repair</button><span className="eyebrow">{result.complaint_id}</span></div>
    {result.simulated && <div className="demo-tag">Simulated repair (demo){isFixture(result) ? ' · Illustrative mock result' : ''}</div>}
    <div className="result-grid"><div className="card verdict-card" style={{ '--verdict': color } as React.CSSProperties}><div className="eyebrow">VERIFICATION COMPLETE</div><h1 style={{ color }}>{labels[result.verdict]}</h1><div className="verdict-meta"><span className="verdict-code">{result.verdict}</span><span>{Math.round(result.confidence * 100)}% confidence</span></div><ul className="reasons">{result.reasons.map(r => <li key={r}><ArrowRight size={17} /><span>{r}</span></li>)}</ul></div>
    <div className="card score-card"><div className="ring"><svg viewBox="0 0 160 160"><circle cx="80" cy="80" r="68" fill="none" stroke="var(--border)" strokeWidth="10" /><motion.circle cx="80" cy="80" r="68" fill="none" stroke={color} strokeWidth="10" strokeLinecap="round" strokeDasharray={427.3} initial={{ strokeDashoffset: 427.3 }} animate={{ strokeDashoffset: 427.3 * (1 - (pct ?? 0) / 100) }} transition={{ duration: reduce ? 0 : 1 }} transform="rotate(-90 80 80)" /></svg><strong>{pct === null ? '—' : `${pct}%`}</strong></div><strong>{pct === null ? 'Not scored' : 'Original damage repaired'}</strong><small>{pct === null ? 'Evidence needs further inspection' : 'Measured inside the marked pothole'}</small></div></div>
    <div className="checks">{Object.entries(result.checks).map(([name, check]) => <div className={`card check-card status-${check.status}`} key={name}><span className="check-icon">{check.status === 'pass' ? <CheckCircle2 /> : check.status === 'fail' ? <X /> : check.status === 'warn' ? <AlertTriangle /> : <span>—</span>}</span><div><div className="check-title">{name === 'scene' ? 'Same scene' : name === 'quality' ? 'Patch quality' : name}<span>{check.status}</span></div><p>{check.detail}</p></div></div>)}</div>
    <div className="card evidence"><div className="section-heading"><div><h2>See the evidence</h2><p>Drag the divider to inspect the change.</p></div><button className={`toggle ${heat ? 'active' : ''}`} aria-keyshortcuts="h" aria-pressed={heat} onClick={() => setHeat(v => !v)}><Layers size={16} />Show heatmap</button></div><div className="compare-wrap">{comparison ? <ReactCompareSlider itemOne={<ReactCompareSliderImage src={imageUrl(result.images.before)} alt="Before repair" />} itemTwo={<ReactCompareSliderImage src={imageUrl(comparison)} alt={heat ? 'Repair heatmap' : 'Aligned after repair'} />} /> : <img className="fallback-image" src={imageUrl(result.images.before)} alt="Before repair" />}{result.roi && <div className="result-roi" style={{ left: `${result.roi[0][0] * 100}%`, top: `${result.roi[0][1] * 100}%`, width: `${(result.roi[2][0] - result.roi[0][0]) * 100}%`, height: `${(result.roi[2][1] - result.roi[0][1]) * 100}%` }} /> }<span className="image-label left">Before · marked area</span>{comparison && <span className="image-label right">{heat ? 'Heatmap' : 'After · aligned'}</span>}</div>{!comparison && <p className="unavailable">{heat ? 'Heatmap unavailable for this result.' : 'Aligned comparison unavailable for this result.'}</p>}{heat && comparison && <div className="legend"><span className="green-dot" />Repaired<span className="red-dot" />Still broken</div>}</div>
    <div className="card explanation"><div className="section-heading"><h2>A clear explanation</h2><div className="language" aria-label="Explanation language; K to toggle"><button className={!kn ? 'selected' : ''} onClick={() => setKn(false)}>EN</button><button className={kn ? 'selected' : ''} onClick={() => setKn(true)}>ಕನ್ನಡ</button></div></div><p lang={kn ? 'kn' : 'en'}>{result.explanation[kn ? 'kn' : 'en']}</p></div>
  </motion.section>
}

export default function App() {
  const [demos, setDemos] = useState<DemoCase[]>([]), [result, setResult] = useState<VerifyResult | null>(null)
  const [offline, setOffline] = useState(false)
  const [busy, setBusy] = useState(false), [step, setStep] = useState(0), [error, setError] = useState('')
  const [before, setBefore] = useState<File | null>(null), [after, setAfter] = useState<File | null>(null), [preview, setPreview] = useState('')
  const [roi, setRoi] = useState<ROI | null>(null), [suggested, setSuggested] = useState(false), [suggesting, setSuggesting] = useState(false)
  const [complaint, setComplaint] = useState(''), [gps, setGps] = useState(['', '', '', ''])
  const previewUrl = useRef('')
  const requestBusy = useRef(false)
  const focusEditor = useRef(false)
  const suggestionId = useRef(0), retry = useRef<(() => void) | null>(null)
  useEffect(() => {
    let active = true
    const load = () => {
      setError('')
      api.demos().then(data => { if (active) { setDemos(data); setOffline(isOffline()) } }).catch(e => { if (active) setError(`Cannot load demo cases. ${e.message}`) })
    }
    retry.current = load; load()
    return () => { active = false }
  }, [])
  async function reconnect() {
    setError('')
    retry.current = () => { void reconnect() }
    try { const data = await api.demos(); setDemos(data); setOffline(isOffline()) } catch (e) { setError(e instanceof Error ? e.message : 'Could not reconnect.') }
  }
  useEffect(() => () => { if (previewUrl.current) URL.revokeObjectURL(previewUrl.current) }, [])
  useEffect(() => { if (!busy) return; const timer = setInterval(() => setStep(s => Math.min(s + 1, 5)), 350); return () => clearInterval(timer) }, [busy])
  async function run(action: () => Promise<VerifyResult>, upload = false) {
    if (requestBusy.current) return
    requestBusy.current = true
    setError(''); setBusy(true); setStep(0)
    retry.current = () => { void run(action, upload) }
    try { setResult(await action()); window.scrollTo({ top: 0, behavior: 'smooth' }) }
    catch (e) {
      if (upload && e instanceof ApiError && e.roiRequired) {
        setRoi(null); setSuggested(false); setResult(null); retry.current = null
        setError('Mark the pothole on the before photo. Draw a new box, then select Verify repair.')
        focusEditor.current = true
      } else setError(e instanceof Error ? e.message : 'Verification failed. Please try again.')
    } finally { requestBusy.current = false; setBusy(false); setOffline(isOffline()) }
  }
  useEffect(() => {
    const keydown = (event: KeyboardEvent) => {
      const key = shortcutKey(event)
      if (!key || !/^[1-5]$/.test(key) || requestBusy.current) return
      const demo = demos[Number(key) - 1]
      if (demo) { event.preventDefault(); void run(() => api.demoVerify(demo.case_id)) }
    }
    window.addEventListener('keydown', keydown)
    return () => window.removeEventListener('keydown', keydown)
  }, [demos])
  async function chooseBefore(file: File) {
    if (!file.type.startsWith('image/')) { setError('Choose an image file.'); return }
    if (previewUrl.current) URL.revokeObjectURL(previewUrl.current)
    previewUrl.current = URL.createObjectURL(file); setPreview(previewUrl.current)
    const id = ++suggestionId.current; setBefore(file); setRoi(null); setSuggested(false); setSuggesting(true); setError('')
    try { const data = await api.suggest(file); if (id === suggestionId.current) { setRoi(data.roi); setSuggested(!!data.roi) } } catch { if (id === suggestionId.current) { retry.current = () => { void chooseBefore(file) }; setError('Automatic suggestion unavailable. Drag a box around the pothole to continue, or retry the suggestion.') } } finally { if (id === suggestionId.current) setSuggesting(false); setOffline(isOffline()) }
  }
  const validBox = roi && roi[2][0] > roi[0][0] && roi[2][1] > roi[0][1]
  function submit(e: React.SubmitEvent<HTMLFormElement>) { e.preventDefault(); if (!before || !after || !validBox) return; const body = new FormData(); body.append('before', before); body.append('after', after); body.append('complaint_id', complaint.trim()); body.append('roi', JSON.stringify(roi)); ['before_lat', 'before_lon', 'after_lat', 'after_lon'].forEach((name, i) => { if (gps[i]) body.append(name, gps[i]) }); void run(() => api.verify(body), true) }
  return <div className="app"><header><a className="brand" href="/" onClick={e => { e.preventDefault(); if (!busy) setResult(null) }}><span className="brand-icon"><ShieldCheck size={25} /></span>Fix<span>Check</span></a><div className="header-right"><span className="local-dot" />{mockMode ? 'MOCK PREVIEW' : 'LOCAL VERIFICATION'}<span className="header-divider" /><span>Proof, before payment.</span></div></header><main>{offline && !mockMode && <div className="offline-banner" role="status"><AlertTriangle size={20} /><div><strong>Backend offline – showing cached demo results</strong><p>Bundled fallback results are labeled illustrative. Uploads require the local backend.</p></div><button className="text-button" disabled={busy} onClick={() => void reconnect()}><RotateCcw size={16} />Reconnect</button></div>}<AnimatePresence mode="wait">{busy ? <motion.section key="progress" className="card progress-panel" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} aria-live="polite" aria-busy="true"><div className="scan-icon"><ScanLine size={40} /></div><div className="eyebrow">FOLLOWING THE EVIDENCE</div><h1>Every repair claim gets checked.</h1><p>Checking location, authenticity and the original damage.</p><div className="steps">{steps.map((s, i) => <div key={s} className={i <= step ? 'lit' : ''}><span>{i < step ? <Check size={20} /> : i === step ? <LoaderCircle className="spin" size={20} /> : i + 1}</span><strong>{s}</strong></div>)}</div><small>Progress animation is illustrative. The verdict uses the completed checks.</small></motion.section> : result ? <Result key={result.id} result={result} onBack={() => setResult(null)} /> : <motion.div key="verify" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><section className="hero"><div className="eyebrow"><span /> CIVIC ACCOUNTABILITY, VERIFIED</div><h1>Stop paying for<br /><em>fake repairs.</em></h1><p>A photo says “fixed.” The evidence tells the whole story.<br className="desktop" /> Verify pothole repairs with transparent, local image analysis.</p><div className="hero-features"><span><MapPin size={16} />Same location</span><span><Fingerprint size={16} />Original evidence</span><span><Crosshair size={16} />Measurable repair</span></div><div className="hero-stamp"><ShieldCheck size={42} /><strong>Trust the evidence.</strong><span>Before → verify → accountable</span></div></section><section className="demo-section"><div className="section-heading"><div><div className="eyebrow">START WITH THE EVIDENCE</div><h2>Five claims. See what holds up.</h2></div><span className="small-muted">{mockMode || offline ? 'Illustrative mock fixtures' : 'Shortcuts: 1–5 to run a case'}</span></div><div className="demo-grid">{demos.map((demo, i) => <article className="card demo-card" key={demo.case_id}><div className="thumbnail"><img src={imageUrl(demo.before_url)} alt={`Before: ${demo.title}`} /><span>CASE 0{i + 1}</span></div><div className="demo-body"><h3>{demo.title}</h3><small>{demo.simulated ? 'Simulated repair (demo)' : 'Repair evidence'}</small><button aria-keyshortcuts={String(i + 1)} onClick={() => void run(() => api.demoVerify(demo.case_id))}>Run verification<ArrowRight size={16} /></button></div></article>)}</div>{!demos.length && !error && <p className="small-muted">Loading demo cases…</p>}</section><section className="card upload-panel"><div className="section-heading"><div><div className="eyebrow">YOUR OWN EVIDENCE</div><h2>Verify a repair</h2><p>Two photos. One marked pothole. A transparent verdict.</p></div><span className="step-tag">01 — UPLOAD & MARK</span></div><form onSubmit={submit}><div className="upload-grid"><UploadZone label="Before" file={before} onFile={file => void chooseBefore(file)} /><UploadZone label="After" file={after} onFile={file => { if (file.type.startsWith('image/')) { setAfter(file); setError('') } else setError('Choose an image file.') }} /></div>{preview && <section className="mark-section" tabIndex={-1} ref={node => { if (node && focusEditor.current) { focusEditor.current = false; requestAnimationFrame(() => { node.focus({ preventScroll: true }); node.scrollIntoView({ behavior: 'smooth', block: 'center' }) }) } }}><div className="section-heading"><h3><Crosshair size={20} />Mark the pothole</h3><span className="small-muted">{suggesting ? 'Looking for a suggested box…' : validBox ? 'Box ready' : 'Required before verification'}</span></div><BoxEditor src={preview} roi={roi} suggested={suggested} onChange={value => { ++suggestionId.current; setSuggesting(false); setRoi(value); setSuggested(false) }} /></section>}<div className="form-fields"><label>Complaint ID<input required value={complaint} onChange={e => setComplaint(e.target.value)} placeholder="e.g. BLR-2026-0042" /></label><details className="gps"><summary>Location coordinates <span>Optional</span></summary><div className="gps-grid">{['Before latitude', 'Before longitude', 'After latitude', 'After longitude'].map((name, i) => <label key={name}>{name}<input type="number" step="any" min={i % 2 ? -180 : -90} max={i % 2 ? 180 : 90} value={gps[i]} onChange={e => setGps(gps.map((v, j) => i === j ? e.target.value : v))} placeholder={i % 2 ? '77.6245' : '12.9352'} /></label>)}</div></details></div><div className="submit-row"><span><ShieldCheck size={17} />Local processing. No paid APIs.</span><button className="primary" type="submit" disabled={!before || !after || !validBox || !complaint.trim() || suggesting}>Verify repair<ArrowRight size={18} /></button></div>{mockMode && <p className="mock-note">Mock preview: use the five demo cases above to explore verdicts. Upload analysis requires the local backend.</p>}</form></section></motion.div>}</AnimatePresence>{error && <div className="error-card" role="alert"><AlertTriangle size={22} /><div><strong>Something needs attention</strong><p>{error}</p></div>{!busy && retry.current && <button onClick={() => retry.current?.()}><RotateCcw size={16} />Retry</button>}<button aria-label="Dismiss error" onClick={() => setError('')}><X size={18} /></button></div>}</main><footer><span>FixCheck <span className="footer-slash">/</span> Proof of fix.</span><span>The model suggests. The measurement verifies.</span></footer></div>
}
