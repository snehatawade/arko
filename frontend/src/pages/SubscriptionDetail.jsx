import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { subscriptionsAPI } from '../services/api'

export default function SubscriptionDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [subscription, setSubscription] = useState(null)
  const [loading, setLoading] = useState(true)
  const [cancelling, setCancelling] = useState(false)

  useEffect(() => {
    loadSubscription()
  }, [id])

  const loadSubscription = async () => {
    try {
      const response = await subscriptionsAPI.getById(id)
      setSubscription(response.data)
    } catch (error) {
      console.error('Error loading subscription:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to mark this subscription as cancelled?')) {
      return
    }

    setCancelling(true)
    try {
      await subscriptionsAPI.cancel(id)
      navigate('/')
    } catch (error) {
      console.error('Error cancelling subscription:', error)
      alert('Failed to cancel subscription. Please try again.')
    } finally {
      setCancelling(false)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
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

  if (!subscription) {
    return <div className="text-center py-12">Subscription not found</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Dashboard
        </button>
        <h1 className="text-3xl font-bold text-gray-900">{subscription.name}</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Main Details */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Subscription Details</h2>
          <dl className="space-y-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Merchant Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{subscription.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Amount</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatCurrency(subscription.amount)}/{subscription.frequency}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Frequency</dt>
              <dd className="mt-1 text-sm text-gray-900 capitalize">{subscription.frequency}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">First Seen</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatDate(subscription.first_seen)}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Last Seen</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatDate(subscription.last_seen)}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Next Renewal</dt>
              <dd className="mt-1 text-sm text-gray-900 font-medium">{formatDate(subscription.next_renewal)}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Bank Account</dt>
              <dd className="mt-1 text-sm text-gray-900">{subscription.bank_account}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  subscription.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {subscription.status}
                </span>
              </dd>
            </div>
            {subscription.cancellation_probability !== null && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Cancellation Probability</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        className="bg-red-600 h-2 rounded-full"
                        style={{ width: `${subscription.cancellation_probability * 100}%` }}
                      ></div>
                    </div>
                    <span>{(subscription.cancellation_probability * 100).toFixed(0)}%</span>
                  </div>
                </dd>
              </div>
            )}
          </dl>

          {subscription.status === 'active' && (
            <button
              onClick={handleCancel}
              disabled={cancelling}
              className="mt-6 w-full px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
            >
              {cancelling ? 'Cancelling...' : 'Mark as Cancelled'}
            </button>
          )}
        </div>

        {/* Harvey Insights & Transactions */}
        <div className="space-y-6">
          {subscription.harvey_insights && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-3 flex items-center">
                <span className="mr-2">🤖</span>
                Harvey's Insights
              </h2>
              <p className="text-sm text-gray-700 whitespace-pre-line">{subscription.harvey_insights}</p>
            </div>
          )}

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Transaction History</h2>
            {subscription.transactions && subscription.transactions.length > 0 ? (
              <div className="space-y-3">
                {subscription.transactions.map((txn) => (
                  <div key={txn.id} className="flex justify-between items-center py-2 border-b border-gray-100">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{formatDate(txn.date)}</p>
                      <p className="text-xs text-gray-500">{txn.description}</p>
                    </div>
                    <p className="text-sm font-medium text-gray-900">{formatCurrency(Math.abs(txn.amount))}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No transactions found</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

