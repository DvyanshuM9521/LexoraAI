import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Contracts from './pages/Contracts'
import Analysis from './pages/Analysis'
import Comparison from './pages/Comparison'
import Assistant from './pages/Assistant'
import Reports from './pages/Reports'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/contracts" element={<Contracts />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/comparison" element={<Comparison />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
