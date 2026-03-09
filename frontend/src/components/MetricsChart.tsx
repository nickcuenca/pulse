import { useEffect, useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { getMetrics, type Metric } from '../api'
import './MetricsChart.css'

interface MetricsChartProps {
  serviceId: string
}

const POLL_MS = 5000

export function MetricsChart({ serviceId }: MetricsChartProps) {
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const fetchData = async () => {
      try {
        const data = await getMetrics(serviceId, { limit: 50 })
        if (!cancelled) {
          setMetrics(data)
          setError(null)
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Failed to load metrics')
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

  if (loading && metrics.length === 0) {
    return (
      <div className="metrics-chart loading">
        Loading metrics…
      </div>
    )
  }

  if (error && metrics.length === 0) {
    return (
      <div className="metrics-chart error">
        {error}
      </div>
    )
  }

  // Group by metric_name; build series for Recharts: { timestamp, metricName1: v1, metricName2: v2, ... }
  const metricNames = [...new Set(metrics.map((m) => m.name))]
  type ChartRow = { timestamp: string; [key: string]: string | number }
  const byTime = new Map<string, ChartRow>()

  for (const m of metrics) {
    const ts = new Date(m.timestamp).toISOString()
    const row = byTime.get(ts) ?? { timestamp: ts }
    row[m.name] = m.value
    byTime.set(ts, row)
  }

  const chartData = Array.from(byTime.values()).sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  )

  const colors = ['#1a73e8', '#34a853', '#ea4335', '#f9ab00', '#9334e6']

  return (
    <div className="metrics-chart section">
      <h3>Metrics (last 50, polling every 5s)</h3>
      {chartData.length === 0 ? (
        <p className="empty-state">No metrics yet.</p>
      ) : (
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(ts) => new Date(ts).toLocaleTimeString()}
                stroke="#666"
              />
              <YAxis stroke="#666" />
              <Tooltip
                labelFormatter={(ts) => new Date(ts).toLocaleString()}
                contentStyle={{ fontSize: 12 }}
              />
              <Legend />
              {metricNames.map((name, i) => (
                <Line
                  key={name}
                  type="monotone"
                  dataKey={name}
                  stroke={colors[i % colors.length]}
                  dot={false}
                  strokeWidth={2}
                  name={name}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
