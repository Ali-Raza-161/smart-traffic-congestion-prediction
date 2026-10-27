import { useEffect, useState } from 'react'
import { createTicket, getSettings, getTickets, updateTicket } from '../services/api'

export default function Support() {
  const [tickets, setTickets] = useState<any[]>([])
  const [settings, setSettings] = useState<any>({})
  const [form, setForm] = useState({ name: '', subject: '', message: '', priority: 'Medium' })
  async function load() { setTickets(await getTickets().catch(() => [])); setSettings(await getSettings().catch(() => ({}))) }
  useEffect(() => { load() }, [])
  async function submit(e: React.FormEvent) {
    e.preventDefault()
    await createTicket(form)
    setForm({ name: '', subject: '', message: '', priority: 'Medium' })
    load()
  }
  return (
    <div>
      <h1>Support &amp; Help</h1>
      <p className="muted">Guides, answers, and a ticket form. This is a demo system; no real traffic operations team is behind it.</p>
      <div className="two">
        <div className="card">
          <h3>Contact support</h3>
          <p><strong>Email:</strong> {settings.contact_email || 'Not set yet — add it in Settings.'}</p>
          <p><strong>Phone:</strong> {settings.contact_phone || 'Not set yet — add it in Settings.'}</p>
          <p className="muted">No support contact is shown unless the operator enters it in Settings.</p>
          <form onSubmit={submit}>
            <label>Your name</label><input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            <label>Subject</label><input value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} required />
            <label>Message</label><textarea rows={4} value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} required />
            <label>Priority</label><select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}><option>Low</option><option>Medium</option><option>High</option></select>
            <button>Create ticket</button>
          </form>
        </div>
        <div className="card">
          <h3>Help Center — quick guides</h3>
          <p><strong>Reading the dashboard.</strong> Congestion levels come from simulated occupancy: Low under 40%, Moderate under 65%, High under 85%, Severe at 85% and above.</p>
          <p><strong>Predictions.</strong> Choose an intersection and a horizon (15/30/60 minutes). The model was trained only on simulated data.</p>
          <p><strong>Signals.</strong> Green-time suggestions are advisory only and never control a real signal.</p>
          <h3>Frequently asked questions</h3>
          <p><strong>Is this real traffic data?</strong> No. Every reading is simulated in this demo.</p>
          <p><strong>Can it control traffic lights?</strong> No. It only suggests timings for a human to review.</p>
          <p><strong>What if a sensor goes offline?</strong> The sensor list and Alerts page show it, and the model keeps working from the remaining simulated history.</p>
        </div>
      </div>
      <div className="card"><h3>Support tickets</h3>
        <table><thead><tr><th>Subject</th><th>Priority</th><th>Status</th><th>Reply</th><th></th></tr></thead>
        <tbody>{tickets.map((t: any) => (<tr key={t.id}><td>{t.subject}</td><td>{t.priority}</td><td>{t.status}</td><td>{t.reply || '—'}</td><td><button className="secondary" onClick={async () => { await updateTicket(t.id, { status: t.status === 'Resolved' ? 'Open' : 'Resolved', reply: t.reply || 'Checked — simulated data only.' }); load() }}>{t.status === 'Resolved' ? 'Reopen' : 'Mark resolved'}</button></td></tr>))}</tbody></table>
      </div>
    </div>
  )
}
