import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { subscriptionsAPI, harveyAPI, uploadAPI } from '../services/api'

export default function Dashboard() {
  const [subscriptions, setSubscriptions] = useState([])
  const [savings, setSavings] = useState({ total_monthly_cost: 0, avoidable_spend: 0, potential_savings: 0 })
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [subsRes, savingsRes] = await Promise.all([
        subscriptionsAPI.getAll(),
        harveyAPI.getSavings(),
      ])
      setSubscriptions(subsRes.data || [])
      setSavings(savingsRes.data || { total_monthly_cost: 0, avoidable_spend: 0, potential_savings: 0 })
    } catch (error) {
      console.error('Error loading data:', error)
      // Don't redirect on error - just show empty state
      // The interceptor will handle 401 errors
      if (error.response?.status === 401) {
        // Token is invalid, let the interceptor handle it
        return
      }
      // Set empty state on error
      setSubscriptions([])
      setSavings({ total_monthly_cost: 0, avoidable_spend: 0, potential_savings: 0 })
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type
    const fileExt = file.name.split('.').pop().toLowerCase()
    if (!['csv', 'xlsx', 'xls'].includes(fileExt)) {
      setUploadMessage('Please upload a CSV or Excel file (.csv, .xlsx, .xls)')
      return
    }

    setUploading(true)
    setUploadMessage('')

    try {
      console.log('Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type)
      const response = await uploadAPI.uploadCSV(file)
      console.log('Upload response:', response.data)
      setUploadMessage(`Success! ${response.data.transactions_added} transactions added, ${response.data.subscriptions_detected} subscriptions detected.`)
      // Reload data after successful upload with error handling
      setTimeout(async () => {
        try {
          await loadData()
        } catch (err) {
          console.error('Error reloading data after upload:', err)
          // Don't show error to user, just log it
        }
      }, 500)
    } catch (error) {
      console.error('Upload error details:', {
        message: error.message,
        response: error.response,
        data: error.response?.data,
        status: error.response?.status,
        code: error.code,
        request: error.request
      })
      
      let errorMessage = 'Upload failed. Please try again.'
      
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage = 'Upload timeout. The file might be too large. Please try again.'
      } else if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
        errorMessage = 'Network error. Please check if the backend server is running on http://localhost:8000'
      } else if (error.response) {
        const detail = error.response.data?.detail
        if (Array.isArray(detail)) {
          errorMessage = detail.map((d) => d.msg || JSON.stringify(d)).join(', ')
        } else if (detail) {
          errorMessage = typeof detail === 'string' ? detail : JSON.stringify(detail)
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message
        } else {
          errorMessage = `Server error: ${error.response.status}`
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setUploadMessage(errorMessage)
    } finally {
      setUploading(false)
      e.target.value = '' // Reset file input
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      return new Date(dateString).toLocaleDateString()
    } catch (e) {
      return String(dateString)
    }
  }

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined || isNaN(amount)) {
      return '₹0.00'
    }
    try {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
      }).format(amount)
    } catch (e) {
      return `₹${Number(amount).toFixed(2)}`
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  // Ensure savings has default values
  const safeSavings = savings || { total_monthly_cost: 0, avoidable_spend: 0, potential_savings: 0 }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">Manage your subscriptions and track spending</p>
      </div>

      {/* Upload CSV Section */}
      <div className="mb-6 bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Upload Bank Statement</h2>
        <div className="flex items-center space-x-4">
          <label className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 cursor-pointer">
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
            {uploading ? 'Uploading...' : 'Choose File (CSV/Excel)'}
          </label>
          {uploadMessage && (
            <p className={`text-sm ${uploadMessage.includes('Success') ? 'text-green-600' : 'text-red-600'}`}>
              {uploadMessage}
            </p>
          )}
        </div>
        <p className="mt-2 text-xs text-gray-500">
          Upload your bank statement (CSV or Excel). Expected columns: date, amount, description
        </p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">💰</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Monthly Cost</dt>
                  <dd className="text-lg font-medium text-gray-900">{formatCurrency(safeSavings.total_monthly_cost)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">📊</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Subscriptions</dt>
                  <dd className="text-lg font-medium text-gray-900">{subscriptions.length || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">💸</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Potential Savings</dt>
                  <dd className="text-lg font-medium text-red-600">{formatCurrency(safeSavings.avoidable_spend)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subscriptions List */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Your Subscriptions</h2>
        </div>
        {!subscriptions || subscriptions.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            <p>No subscriptions detected yet.</p>
            <p className="mt-2 text-sm">Upload a CSV or Excel bank statement to get started.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {subscriptions.map((sub) => (
              <div key={sub.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h3 className="text-lg font-medium text-gray-900">{sub.name || 'Unknown'}</h3>
                      <span className={`ml-3 px-2 py-1 text-xs font-medium rounded-full ${
                        (sub.status || 'active') === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {sub.status || 'active'}
                      </span>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 space-x-4">
                      <span>{formatCurrency(sub.amount || 0)}/{sub.frequency || 'monthly'}</span>
                      <span>•</span>
                      <span>Last seen: {sub.last_seen ? formatDate(sub.last_seen) : 'N/A'}</span>
                      <span>•</span>
                      <span>Renews: {sub.next_renewal ? formatDate(sub.next_renewal) : 'N/A'}</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <Link
                      to={`/subscription/${sub.id}`}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

