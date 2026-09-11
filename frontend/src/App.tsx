import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { CustomerLandingPage } from './pages/CustomerLandingPage'
import { HomePage } from './pages/HomePage'
import { RatingPlaceholderPage } from './pages/RatingPlaceholderPage'

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/r/:slug" element={<CustomerLandingPage />} />
          <Route path="/r/:slug/rating" element={<RatingPlaceholderPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}
