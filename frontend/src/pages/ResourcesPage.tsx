import { ResourceList } from '@/components/ResourceList'
import { Link } from 'react-router-dom'
import { PlusCircle } from 'lucide-react'

export function ResourcesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Resources</h1>
          <p className="text-gray-600 mt-1">
            View all created Azure resources and GitHub repositories
          </p>
        </div>
        <Link
          to="/create"
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <PlusCircle className="h-4 w-4" />
          <span>Create New</span>
        </Link>
      </div>

      <ResourceList />
    </div>
  )
}
