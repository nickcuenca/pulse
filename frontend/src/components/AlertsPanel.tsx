import { useEffect, useState } from 'react'
import { getAlerts, type Alert } from '../api'
import './AlertsPanel.css'

interface AlertsPanelProps {
  serviceId: string
}

const POLL_MS = 5000

export function AlertsPanel({ serviceId }: AlertsPanelProps) {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const fetchData = async () => {
      try {
        const data = await getAlerts(serviceId)
        if (!cancelled) {
          setAlerts(data)
          setError(null)
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Failed to load alerts')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, POLL_MS)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [serviceId])

  if (loading && alerts.length === 0) {
    return (
      <div className="alerts-panel section">
        <h3>Alerts (polling every 5s)</h3>
        <p className="empty-state">Loading…</p>
      </div>
    )
  }

  if (error && alerts.length === 0) {
    return (
      <div className="alerts-panel section">
        <h3>Alerts (polling every 5s)</h3>
        <p className="error">{error}</p>
      </div>
    )
  }

  return (
    <div className="alerts-panel section">
      <h3>Alerts (polling every 5s)</h3>
      {alerts.length === 0 ? (
        <p className="empty-state">No alerts.</p>
      ) : (
        <ul className="alerts-list">
          {alerts.map((a) => (
            <li key={a.id} className={`alert-item state-${a.state.toLowerCase()}`}>
              <span className="alert-value">{a.metric_value}</span>
              <span className="alert-state">{a.state}</span>
              <span className="alert-time">
                Triggered: {new Date(a.triggered_at).toLocaleString()}
              </span>
              {a.resolved_at && (
                <span className="alert-time">
                  Resolved: {new Date(a.resolved_at).toLocaleString()}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
