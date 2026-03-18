import { views } from '../constants'
import type { ViewId } from '../constants'

type HeaderProps = {
  view: ViewId
  onChange: (view: ViewId) => void
}

export default function Header({
  view,
  onChange,
}: HeaderProps) {
  return (
    <header className="header">
      <div className="brand">
        <span className="brand-mark">Bookwave</span>
        <span className="brand-sub">Microservice Control Deck</span>
      </div>
      <nav className="nav">
        {views.map((item) => (
          <button
            key={item.id}
            className={`nav-btn ${view === item.id ? 'active' : ''}`}
            onClick={() => onChange(item.id)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </nav>
    </header>
  )
}
