import { useEffect, useState } from 'react'
import { getSignals } from '../services/api'

export default function Signals() {
  const [data, setData] = useState<any>(null)
  useEffect(() => { getSignals().then(setData).catch(() => undefined) }, [])
  return (
    <div>
      <h1>Signal Timing Suggestions</h1>
      <div className="notice"><strong>Advisory only.</strong> These suggestions do not control real traffic signals. A human operator must review any change before it is used anywhere.</div>
      <div className="card"><h3>Suggested green times (simulated congestion)</h3>
        <table><thead><tr><th>Intersection</th><th>Congestion</th><th>Current (s)</th><th>Suggested (s)</th><th>Adjustment</th></tr></thead>
        <tbody>{(data?.signals || []).map((s: any) => (<tr key={s.intersection_id}><td>{s.name}</td><td><span className={`badge ${s.congestion}`}>{s.congestion}</span></td><td>{s.current_green_seconds}</td><td>{s.suggested_green_seconds}</td><td>{s.adjustment_seconds > 0 ? `+${s.adjustment_seconds}` : s.adjustment_seconds} s</td></tr>))}</tbody></table>
        <p className="muted">{data?.note}</p>
      </div>
    </div>
  )
}
