import type { Service } from '../api'
import './ServiceList.css'

interface ServiceListProps {
  services: Service[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export function ServiceList({ services, selectedId, onSelect }: ServiceListProps) {
  return (
    <ul className="service-list">
      {services.map((s) => (
        <li key={s.id}>
          <button
            type="button"
            className={`service-list-item ${s.id === selectedId ? 'selected' : ''}`}
            onClick={() => onSelect(s.id)}
          >
            <span className="service-list-name">{s.name}</span>
            <span className="service-list-date">
              {new Date(s.created_at).toLocaleDateString()}
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
