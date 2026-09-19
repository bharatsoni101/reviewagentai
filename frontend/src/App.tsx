import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { CustomerPage } from './pages/CustomerPage'
import { LoginPage } from './pages/LoginPage'
import { AccountPage } from './pages/AccountPage'
import { OwnerDashboardPage } from './pages/OwnerDashboardPage'
import { AdminDashboardPage } from './pages/AdminDashboardPage'
import { getAuthToken } from './lib/auth'

function ProtectedAdmin() {
  const location = useLocation()
  return getAuthToken() ? <AdminDashboardPage /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

function ProtectedOwner() {
  const location = useLocation()
  return getAuthToken() ? <OwnerDashboardPage /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

function ProtectedAccount() {
  const location = useLocation()
  return getAuthToken() ? <AccountPage /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

export default function App() {
  return (
    <Routes>
      <Route path="/r/:slug" element={<CustomerPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/account" element={<ProtectedAccount />} />
      <Route path="/owner" element={<ProtectedOwner />} />
      <Route path="/admin" element={<ProtectedAdmin />} />
      <Route path="/" element={<Navigate to="/r/reviewagentai" replace />} />
      <Route path="*" element={<Navigate to="/r/reviewagentai" replace />} />
    </Routes>
  )
}
