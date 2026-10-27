import { useEffect, useState } from 'react'
import { BarChart } from '../components/Charts'
import { getReports } from '../services/api'

export default function Reports() {
  const [data, setData] = useState<any>(null)
  useEffect(() => { getReports().then(setData).catch(() => undefined) }, [])
  const m = data?.model_metrics
  return (
    <div>
      <h1>Reports</h1>
      <p className="muted">Summary of simulated readings and model evaluation on simulated data only.</p>
      <div className="notice"><strong>Simulated data only.</strong> Do not present these figures as real city traffic statistics.</div>
      <div className="grid">
        <div className="card"><h3>Total simulated readings</h3><div className="big">{data?.summary?.total_readings ?? '—'}</div></div>
        <div className="card"><h3>Classifier accuracy (synthetic test set)</h3><div className="big">{m ? `${(m.classifier_accuracy * 100).toFixed(1)}%` : '—'}</div></div>
        <div className="card"><h3>Count prediction MAE (synthetic)</h3><div className="big">{m?.regressor_mae ?? '—'}</div></div>
        <div className="card"><h3>Count prediction RMSE (synthetic)</h3><div className="big">{m?.regressor_rmse ?? '—'}</div></div>
      </div>
      <div className="two">
        <div className="card"><BarChart title="Readings by congestion level" data={Object.entries(data?.summary?.by_congestion || {}).map(([label, value]) => ({ label, value: Number(value) }))} /></div>
        <div className="card"><BarChart title="Average vehicles by intersection" data={(data?.summary?.by_intersection || []).map((r: any) => ({ label: r.intersection_id, value: r.avg_count }))} /></div>
      </div>
      <div className="card">
        <h3>Confusion matrix (synthetic test set)</h3>
        <p className="muted">Rows: actual level. Columns: predicted level. Labels: {m?.confusion_matrix_labels?.join(', ')}</p>
        <table><tbody>{(m?.confusion_matrix || []).map((row: number[], i: number) => (<tr key={i}>{row.map((v, j) => (<td key={j}>{v}</td>))}</tr>))}</tbody></table>
        <p><a href="http://localhost:8000/api/reports/export">Download CSV report (simulated data)</a></p>
      </div>
    </div>
  )
}
