import { useEffect, useState } from 'react'
import { getServices, type Service } from './api'
import { ServiceList } from './components/ServiceList'
import { MetricsChart } from './components/MetricsChart'
import { AlertsPanel } from './components/AlertsPanel'

export default function App() {
  const [services, setServices] = useState<Service[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    getServices()
      .then((data) => {
        if (!cancelled) {
          setServices(data)
          if (data.length > 0 && !selectedId) {
            setSelectedId(data[0].id)
          }
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Failed to load services')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [])

  const selectedService = services.find((s) => s.id === selectedId)

  if (loading && services.length === 0) {
    return (
      <div className="app">
        <div className="loading">Loading services…</div>
      </div>
    )
  }

  if (error && services.length === 0) {
    return (
      <div className="app">
        <div className="error">{error}</div>
      </div>
    )
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>Services</h2>
        <ServiceList
          services={services}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
      </aside>
      <main className="main">
        {selectedService ? (
          <>
            <div className="detail-header">
              <h1>{selectedService.name}</h1>
              {selectedService.description && (
                <p className="description">{selectedService.description}</p>
              )}
            </div>
            <MetricsChart serviceId={selectedService.id} />
            <AlertsPanel serviceId={selectedService.id} />
          </>
        ) : (
          <p className="empty-state">Select a service or register one via the API.</p>
        )}
      </main>
    </div>
  )
}
