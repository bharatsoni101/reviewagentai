import { Navigate, Route, Routes } from 'react-router-dom'
import { CustomerPage } from './pages/CustomerPage'

export default function App() {
  return (
    <Routes>
      <Route path="/r/:slug" element={<CustomerPage />} />
      <Route path="/" element={<Navigate to="/r/reviewagentai" replace />} />
      <Route path="*" element={<Navigate to="/r/reviewagentai" replace />} />
    </Routes>
  )
}
