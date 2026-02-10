import { useQuery } from '@tanstack/react-query'
import { resourcesApi } from '@/services/api'
import { Activity, Server, Github, AlertCircle, CheckCircle } from 'lucide-react'
import { ResourceList } from '@/components/ResourceList'

export function Dashboard() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: resourcesApi.healthCheck,
    refetchInterval: 30000,
  })

  const { data: resources } = useQuery({
    queryKey: ['resources'],
    queryFn: resourcesApi.listResources,
    refetchInterval: 10000,
  })

  const stats = {
    total: resources?.length || 0,
    pending: resources?.filter((r) => r.status === 'Pending').length || 0,
    inProgress: resources?.filter((r) => r.status === 'In Progress').length || 0,
    completed: resources?.filter((r) => r.status === 'Completed').length || 0,
    failed: resources?.filter((r) => r.status === 'Failed').length || 0,
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Monitor your Azure resources and GitHub repositories
        </p>
      </div>

      {/* Health Status */}
      {health && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ServiceStatus
            name="Azure"
            status={health.services.azure}
            icon={Server}
          />
          <ServiceStatus
            name="GitHub"
            status={health.services.github}
            icon={Github}
          />
          <ServiceStatus
            name="SharePoint"
            status={health.services.sharepoint}
            icon={Activity}
          />
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard label="Total" value={stats.total} color="blue" />
        <StatCard label="Pending" value={stats.pending} color="yellow" />
        <StatCard label="In Progress" value={stats.inProgress} color="blue" />
        <StatCard label="Completed" value={stats.completed} color="green" />
        <StatCard label="Failed" value={stats.failed} color="red" />
      </div>

      {/* Recent Resources */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Recent Resources
        </h2>
        <ResourceList />
      </div>
    </div>
  )
}

interface ServiceStatusProps {
  name: string
  status: string
  icon: React.ElementType
}

function ServiceStatus({ name, status, icon: Icon }: ServiceStatusProps) {
  const isHealthy = status === 'healthy'

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Icon className="h-5 w-5 text-gray-600" />
          <span className="font-medium text-gray-900">{name}</span>
        </div>
        {isHealthy ? (
          <CheckCircle className="h-5 w-5 text-green-500" />
        ) : (
          <AlertCircle className="h-5 w-5 text-red-500" />
        )}
      </div>
      <p className={`text-xs mt-2 ${isHealthy ? 'text-green-600' : 'text-red-600'}`}>
        {isHealthy ? 'Operational' : 'Degraded'}
      </p>
    </div>
  )
}

interface StatCardProps {
  label: string
  value: number
  color: 'blue' | 'yellow' | 'green' | 'red'
}

function StatCard({ label, value, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-900',
    yellow: 'bg-yellow-50 text-yellow-900',
    green: 'bg-green-50 text-green-900',
    red: 'bg-red-50 text-red-900',
  }

  return (
    <div className={`rounded-lg shadow p-4 ${colorClasses[color]}`}>
      <p className="text-sm font-medium opacity-75">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  )
}
