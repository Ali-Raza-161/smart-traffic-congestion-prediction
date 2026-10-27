import { useEffect, useState } from 'react'
import { getIntersections, getSensors } from '../services/api'

export default function Intersections() {
  const [rows, setRows] = useState<any[]>([])
  const [sensors, setSensors] = useState<any[]>([])
  useEffect(() => { getIntersections().then(setRows).catch(() => undefined); getSensors().then(setSensors).catch(() => undefined) }, [])
  return (
    <div>
      <h1>Intersections</h1>
      <p className="muted">Fictional intersections in Demo City. All readings are simulated.</p>
      <div className="card"><h3>Intersections</h3>
        <table><thead><tr><th>ID</th><th>Name</th><th>Capacity / 5 min</th><th>Latest count</th><th>Occupancy</th><th>Level</th></tr></thead>
        <tbody>{rows.map((r: any) => (<tr key={r.id}><td>{r.id}</td><td>{r.name}</td><td>{r.capacity_per_5min}</td><td>{r.latest.vehicle_count}</td><td>{r.latest.occupancy_percent}%</td><td><span className={`badge ${r.latest.congestion}`}>{r.latest.congestion}</span></td></tr>))}</tbody></table>
      </div>
      <div className="card"><h3>IoT sensors (simulated)</h3>
        <table><thead><tr><th>Sensor</th><th>Intersection</th><th>Type</th><th>Status</th><th>Battery</th></tr></thead>
        <tbody>{sensors.map((s: any) => (<tr key={s.id}><td>{s.id}</td><td>{s.intersection_id}</td><td>{s.type}</td><td><span className={`badge ${s.status}`}>{s.status}</span></td><td>{s.battery_percent}%</td></tr>))}</tbody></table>
      </div>
    </div>
  )
}
