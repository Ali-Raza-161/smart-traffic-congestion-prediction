import { useEffect, useState } from 'react'
import { BarChart, LineChart } from '../components/Charts'
import { getCongestion, getReadings, type Reading } from '../services/api'

export default function Dashboard() {
  const [rows, setRows] = useState<any[]>([])
  const [readings, setReadings] = useState<Reading[]>([])
  const [err, setErr] = useState('')
  useEffect(() => {
    getCongestion().then(setRows).catch(() => setErr('API is not running. Start the backend first (see README).'))
    getReadings(undefined, 48).then(setReadings).catch(() => undefined)
  }, [])
  const severe = rows.filter((r) => r.congestion === 'Severe').length
  const high = rows.filter((r) => r.congestion === 'High').length
  const avgSpeed = rows.length ? Math.round(rows.reduce((a, r) => a + r.avg_speed_kmh, 0) / rows.length) : 0
  const totalQ = rows.reduce((a, r) => a + r.queue_length, 0)
  return (
    <div>
      <h1>Dashboard</h1>
      <p className="muted">Live congestion from simulated IoT sensors — fictional Demo City. Educational demo only.</p>
      <div className="notice"><strong>Simulated data only.</strong> No real IoT hardware, no real city traffic data. This dashboard never controls real traffic signals.</div>
      {err && <p>{err}</p>}
      <div className="grid">
        <div className="card"><h3>Intersections</h3><div className="big">{rows.length}</div></div>
        <div className="card"><h3>Severe congestion</h3><div className="big">{severe}</div></div>
        <div className="card"><h3>High congestion</h3><div className="big">{high}</div></div>
        <div className="card"><h3>Average speed</h3><div className="big">{avgSpeed} km/h</div></div>
        <div className="card"><h3>Total queue</h3><div className="big">{totalQ} vehicles</div></div>
      </div>
      <div className="two">
        <div className="card"><LineChart readings={readings} title="Recent vehicle counts (all intersections, simulated)" /></div>
        <div className="card"><BarChart title="Occupancy by intersection (%)" data={rows.map((r) => ({ label: r.name, value: r.occupancy_percent }))} /></div>
      </div>
      <div className="card">
        <h3>Current congestion</h3>
        <table><thead><tr><th>Intersection</th><th>Level</th><th>Vehicles / 5 min</th><th>Speed</th><th>Queue</th></tr></thead>
          <tbody>{rows.map((r) => (<tr key={r.intersection_id}><td>{r.name}</td><td><span className={`badge ${r.congestion}`}>{r.congestion}</span></td><td>{r.vehicle_count}</td><td>{r.avg_speed_kmh} km/h</td><td>{r.queue_length}</td></tr>))}</tbody></table>
      </div>
    </div>
  )
}
