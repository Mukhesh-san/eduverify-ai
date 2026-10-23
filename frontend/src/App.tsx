import { useState, useEffect } from 'react'
import { Sidebar, type NavItem } from './components/Sidebar'
import { ApplicationsPage } from './pages/ApplicationsPage'
import { api } from './api/client'
import './App.css'

export default function App() {
  const [activeNav, setActiveNav] = useState<NavItem>('applications')
  const [apiStatus, setApiStatus] = useState<'unknown' | 'ok' | 'error'>('unknown')

  useEffect(() => {
    api.health()
      .then(() => setApiStatus('ok'))
      .catch(() => setApiStatus('error'))
  }, [])

  return (
    <div className="app-shell">
      <Sidebar
        activeItem={activeNav}
        onNavigate={setActiveNav}
        apiStatus={apiStatus}
      />
      <main className="app-shell__main">
        {activeNav === 'applications' && <ApplicationsPage />}
        {activeNav === 'settings' && (
          <div className="app-shell__placeholder">
            <p>Settings — not yet implemented.</p>
          </div>
        )}
      </main>
    </div>
  )
}
