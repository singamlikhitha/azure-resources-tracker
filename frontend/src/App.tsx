import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { ResourcesPage } from './pages/ResourcesPage'
import { CreateResourcePage } from './pages/CreateResourcePage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/resources" element={<ResourcesPage />} />
        <Route path="/create" element={<CreateResourcePage />} />
      </Routes>
    </Layout>
  )
}

export default App
