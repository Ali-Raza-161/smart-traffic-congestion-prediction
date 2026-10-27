import { BrowserRouter, Link, NavLink, Route, Routes } from 'react-router-dom'
import Alerts from './pages/Alerts'
import Dashboard from './pages/Dashboard'
import Intersections from './pages/Intersections'
import Predictions from './pages/Predictions'
import Reports from './pages/Reports'
import Signals from './pages/Signals'
import Support from './pages/Support'

export default function App() {
  return (
    <BrowserRouter>
      <div className="shell">
        <nav>
          <div className="brand">Smart<span>Traffic</span></div>
          <div className="sub">Demo City (fictional) · Simulated IoT data only</div>
          <div className="group">TRAFFIC</div>
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/intersections">Intersections</NavLink>
          <NavLink to="/predictions">Predictions</NavLink>
          <NavLink to="/signals">Signals (Advisory)</NavLink>
          <NavLink to="/alerts">Alerts</NavLink>
          <div className="group">REPORTS &amp; HELP</div>
          <NavLink to="/reports">Reports</NavLink>
          <NavLink to="/support">Support &amp; Help</NavLink>
          <p style={{ fontSize: 12, color: '#cbd5e1' }}>Educational demo. No real traffic data. No real signal control.</p>
          <Link to="/support" style={{ fontSize: 12 }}>Contact support</Link>
        </nav>
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/intersections" element={<Intersections />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/signals" element={<Signals />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/support" element={<Support />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
