import './Sidebar.css'

export type NavItem = 'applications' | 'settings'

interface SidebarProps {
  activeItem: NavItem
  onNavigate: (item: NavItem) => void
  apiStatus: 'unknown' | 'ok' | 'error'
}

export function Sidebar({ activeItem, onNavigate, apiStatus }: SidebarProps) {
  return (
    <nav className="sidebar" aria-label="Main navigation">
      <div className="sidebar__brand">
        <span className="sidebar__brand-name">EduVerify AI</span>
        <span className="sidebar__brand-sub">Admissions Review</span>
      </div>

      <ul className="sidebar__nav" role="list">
        <li>
          <button
            id="nav-applications"
            className={`sidebar__nav-item${activeItem === 'applications' ? ' sidebar__nav-item--active' : ''}`}
            onClick={() => onNavigate('applications')}
            aria-current={activeItem === 'applications' ? 'page' : undefined}
          >
            <span className="sidebar__nav-icon" aria-hidden="true">⊞</span>
            Applications
          </button>
        </li>
        <li>
          <button
            id="nav-settings"
            className={`sidebar__nav-item${activeItem === 'settings' ? ' sidebar__nav-item--active' : ''}`}
            onClick={() => onNavigate('settings')}
            aria-current={activeItem === 'settings' ? 'page' : undefined}
            disabled
            title="Settings — not yet implemented"
          >
            <span className="sidebar__nav-icon" aria-hidden="true">⚙</span>
            Settings
          </button>
        </li>
      </ul>

      <div className="sidebar__footer">
        <div className="sidebar__api-status">
          <span
            className={`sidebar__api-dot sidebar__api-dot--${apiStatus}`}
            aria-hidden="true"
          />
          <span className="sidebar__api-label">
            {apiStatus === 'ok' && 'API connected'}
            {apiStatus === 'error' && 'API unavailable'}
            {apiStatus === 'unknown' && 'Connecting…'}
          </span>
        </div>
        <p className="sidebar__data-notice">Synthetic data — SIH26261</p>
      </div>
    </nav>
  )
}
