import type { Reading } from '../services/api'

export function LineChart({ readings, title }: { readings: Reading[]; title: string }) {
  const rows = [...readings].reverse().slice(-24)
  if (rows.length < 2) return <p className="muted">Not enough simulated readings yet.</p>
  const max = Math.max(...rows.map((r) => r.vehicle_count), 1)
  const w = 560, h = 180, pad = 28
  const pts = rows.map((r, i) => {
    const x = pad + (i / (rows.length - 1)) * (w - pad * 2)
    const y = h - pad - (r.vehicle_count / max) * (h - pad * 2)
    return `${x},${y}`
  }).join(' ')
  return (
    <div>
      <h3>{title}</h3>
      <svg viewBox={`0 0 ${w} ${h}`} width="100%" role="img" aria-label={title}>
        <polyline points={pts} fill="none" stroke="#0f766e" strokeWidth="3" />
        {rows.map((r, i) => (
          <circle key={i} cx={pad + (i / (rows.length - 1)) * (w - pad * 2)}
            cy={h - pad - (r.vehicle_count / max) * (h - pad * 2)} r="3" fill="#f59e0b" />
        ))}
      </svg>
      <p className="muted">Vehicle count per 5 minutes (simulated). Latest: {rows[rows.length - 1].vehicle_count} vehicles.</p>
    </div>
  )
}

export function BarChart({ data, title }: { data: { label: string; value: number }[]; title: string }) {
  const max = Math.max(...data.map((d) => d.value), 1)
  return (
    <div>
      <h3>{title}</h3>
      {data.map((d) => (
        <div key={d.label} style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '6px 0' }}>
          <span style={{ width: 190 }}>{d.label}</span>
          <div style={{ flex: 1, background: '#e2e8f0', borderRadius: 6 }}>
            <div style={{ width: `${(d.value / max) * 100}%`, background: '#0f766e', height: 18, borderRadius: 6 }} />
          </div>
          <span>{Math.round(d.value)}</span>
        </div>
      ))}
    </div>
  )
}
