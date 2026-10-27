import { useEffect, useState } from 'react'
import { acknowledgeAlert, getAlerts } from '../services/api'

export default function Alerts() {
  const [rows, setRows] = useState<any[]>([])
  async function load() { setRows(await getAlerts().catch(() => [])) }
  useEffect(() => { load() }, [])
  return (
    <div>
      <h1>Alerts</h1>
      <p className="muted">In-app alerts only. No SMS or email is sent by this demo.</p>
      <div className="card"><table><thead><tr><th>Type</th><th>Message</th><th>Severity</th><th>Status</th><th></th></tr></thead>
        <tbody>{rows.map((a: any) => (<tr key={a.id}><td>{a.type}</td><td>{a.message}</td><td>{a.severity}</td><td>{a.acknowledged ? 'Acknowledged' : 'New'}</td><td>{!a.acknowledged && <button className="secondary" onClick={async () => { await acknowledgeAlert(a.id); load() }}>Acknowledge</button>}</td></tr>))}</tbody></table></div>
    </div>
  )
}
