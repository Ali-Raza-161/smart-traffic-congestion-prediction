import { useEffect, useState } from 'react'
import { getIntersections, predict } from '../services/api'

export default function Predictions() {
  const [list, setList] = useState<any[]>([])
  const [id, setId] = useState('INT-A')
  const [horizon, setHorizon] = useState(15)
  const [result, setResult] = useState<any>(null)
  const [err, setErr] = useState('')
  useEffect(() => { getIntersections().then(setList).catch(() => undefined) }, [])
  async function run() {
    setErr('')
    try { setResult(await predict(id, horizon)) } catch { setErr('Prediction failed. Check the API is running and the model trained.') }
  }
  return (
    <div>
      <h1>Predictions</h1>
      <p className="muted">Model trained only on simulated data. Predictions are for the next 15, 30 or 60 minutes.</p>
      <div className="notice"><strong>Simulated data only.</strong> Accuracy figures in Reports describe synthetic data, not real traffic.</div>
      <div className="card">
        <label>Intersection</label>
        <select value={id} onChange={(e) => setId(e.target.value)}>{list.map((x: any) => (<option key={x.id} value={x.id}>{x.name}</option>))}</select>
        <label>Horizon (minutes)</label>
        <select value={horizon} onChange={(e) => setHorizon(Number(e.target.value))}><option value={15}>15</option><option value={30}>30</option><option value={60}>60</option></select>
        <button onClick={run}>Predict congestion</button>
        {err && <p>{err}</p>}
        {result && (
          <div>
            <p>Predicted level: <span className={`badge ${result.congestion}`}>{result.congestion}</span></p>
            <p>Predicted vehicle count: <strong>{result.predicted_vehicle_count}</strong> per 5 minutes</p>
            <p className="muted">Weather: {result.weather} · Event: {result.event ? 'Yes' : 'No'} · {result.note}</p>
          </div>
        )}
      </div>
    </div>
  )
}
