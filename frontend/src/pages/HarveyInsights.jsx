import { useState, useEffect } from 'react'
import { harveyAPI } from '../services/api'

export default function HarveyInsights() {
  const [recommendations, setRecommendations] = useState([])
  const [savings, setSavings] = useState(null)
  const [anomalies, setAnomalies] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInsights()
  }, [])

  const loadInsights = async () => {
    try {
      const [recRes, savingsRes, anomaliesRes] = await Promise.all([
        harveyAPI.getRecommendations(),
        harveyAPI.getSavings(),
        harveyAPI.getAnomalies(),
      ])
      setRecommendations(recRes.data)
      setSavings(savingsRes.data)
      setAnomalies(anomaliesRes.data)
    } catch (error) {
      console.error('Error loading insights:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
    }).format(amount)
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <span className="mr-3">🤖</span>
          Harvey AI Insights
        </h1>
        <p className="mt-2 text-sm text-gray-600">AI-powered recommendations and insights</p>
      </div>

      {/* Savings Summary */}
      {savings && (
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 mb-6 text-white">
          <h2 className="text-xl font-semibold mb-4">Savings Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm opacity-90">Total Monthly Cost</p>
              <p className="text-2xl font-bold">{formatCurrency(savings.total_monthly_cost)}</p>
            </div>
            <div>
              <p className="text-sm opacity-90">Avoidable Spend</p>
              <p className="text-2xl font-bold">{formatCurrency(savings.avoidable_spend)}</p>
            </div>
            <div>
              <p className="text-sm opacity-90">Potential Savings</p>
              <p className="text-2xl font-bold">{formatCurrency(savings.potential_savings)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Recommendations</h2>
        {recommendations.length === 0 ? (
          <p className="text-gray-500">No recommendations at this time. Great job managing your subscriptions!</p>
        ) : (
          <div className="space-y-4">
            {recommendations.map((rec, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  rec.risk_score > 0.7
                    ? 'bg-red-50 border-red-500'
                    : rec.risk_score > 0.5
                    ? 'bg-yellow-50 border-yellow-500'
                    : 'bg-green-50 border-green-500'
                }`}
              >
                <div className="flex justify-between items-start">
                  <p className="text-sm text-gray-700">{rec.recommendation_text}</p>
                  <span className="ml-4 text-xs font-medium text-gray-500">
                    Risk: {(rec.risk_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Anomalies */}
      {anomalies.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">⚠️ Detected Anomalies</h2>
          <div className="space-y-4">
            {anomalies.map((anomaly, index) => (
              <div
                key={index}
                className="p-4 rounded-lg bg-red-50 border border-red-200"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-red-900">{anomaly.anomaly_type.replace('_', ' ').toUpperCase()}</p>
                    <p className="text-sm text-red-700 mt-1">{anomaly.description}</p>
                  </div>
                  <span className="ml-4 text-xs font-medium text-red-600">
                    Risk: {(anomaly.risk_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {anomalies.length === 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">⚠️ Detected Anomalies</h2>
          <p className="text-gray-500">No anomalies detected. Your subscriptions look healthy!</p>
        </div>
      )}
    </div>
  )
}

