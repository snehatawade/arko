import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import SubscriptionDetail from './pages/SubscriptionDetail'
import HarveyInsights from './pages/HarveyInsights'
import Profile from './pages/Profile'
import Layout from './components/Layout'

// Create a context to share auth state
export const AuthContext = React.createContext()

function AppContent() {
  const location = useLocation()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token')
      setIsAuthenticated(!!token)
      setLoading(false)
    }
    
    checkAuth()
    
    // Re-check auth on route changes
    const interval = setInterval(checkAuth, 200)
    
    return () => clearInterval(interval)
  }, [location])

  const ProtectedRoute = ({ children }) => {
    if (loading) {
      return <div className="flex items-center justify-center min-h-screen">Loading...</div>
    }
    return isAuthenticated ? children : <Navigate to="/login" replace />
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated }}>
      <Routes>
        <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/subscription/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <SubscriptionDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/harvey"
          element={
            <ProtectedRoute>
              <Layout>
                <HarveyInsights />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Layout>
                <Profile />
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </AuthContext.Provider>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}


export default App

