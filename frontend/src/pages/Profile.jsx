import { useState, useEffect } from 'react'
import { profileAPI } from '../services/api'

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [csvHistory, setCsvHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState({ name: '', phone: '' })
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const [profileRes, historyRes] = await Promise.all([
        profileAPI.get(),
        profileAPI.getCSVHistory(),
      ])
      setProfile(profileRes.data)
      setCsvHistory(historyRes.data)
      setFormData({
        name: profileRes.data.name,
        phone: profileRes.data.phone,
      })
    } catch (error) {
      console.error('Error loading profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    setMessage('')

    try {
      await profileAPI.update(formData)
      setMessage('Profile updated successfully!')
      setEditing(false)
      loadProfile()
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to update profile')
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return
    }

    try {
      await profileAPI.delete()
      localStorage.removeItem('token')
      window.location.href = '/login'
    } catch (error) {
      alert('Failed to delete account. Please try again.')
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!profile) {
    return <div className="text-center py-12">Profile not found</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Profile & Settings</h1>
      </div>

      {/* Profile Information */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Personal Information</h2>
          {!editing && (
            <button
              onClick={() => setEditing(true)}
              className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800"
            >
              Edit
            </button>
          )}
        </div>

        {message && (
          <div className={`mb-4 p-3 rounded ${
            message.includes('success') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}>
            {message}
          </div>
        )}

        {editing ? (
          <form onSubmit={handleUpdate}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  value={profile.email}
                  disabled
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                />
                <p className="mt-1 text-xs text-gray-500">Email cannot be changed</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Phone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Save
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setEditing(false)
                    setFormData({ name: profile.name, phone: profile.phone })
                    setMessage('')
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          </form>
        ) : (
          <dl className="space-y-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{profile.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="mt-1 text-sm text-gray-900">{profile.email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Phone</dt>
              <dd className="mt-1 text-sm text-gray-900">{profile.phone}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Member Since</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatDate(profile.created_at)}</dd>
            </div>
          </dl>
        )}
      </div>

      {/* CSV Upload History */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Upload History</h2>
        {csvHistory.length === 0 ? (
          <p className="text-gray-500">No uploads yet</p>
        ) : (
          <div className="space-y-3">
            {csvHistory.map((account, index) => (
              <div key={index} className="flex justify-between items-center py-3 border-b border-gray-200">
                <div>
                  <p className="font-medium text-gray-900">{account.bank_account}</p>
                  <p className="text-sm text-gray-500">
                    {account.transaction_count} transactions • First: {formatDate(account.first_upload)} • Last: {formatDate(account.last_upload)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Danger Zone */}
      <div className="bg-white shadow rounded-lg p-6 border-2 border-red-200">
        <h2 className="text-lg font-semibold text-red-600 mb-4">Danger Zone</h2>
        <p className="text-sm text-gray-600 mb-4">
          Once you delete your account, there is no going back. Please be certain.
        </p>
        <button
          onClick={handleDelete}
          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Delete Account
        </button>
      </div>
    </div>
  )
}

