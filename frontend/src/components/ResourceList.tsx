import { useQuery } from '@tanstack/react-query'
import { resourcesApi, ResourceEntry } from '@/services/api'
import { Clock, CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { format } from 'date-fns'

interface ResourceCardProps {
  resource: ResourceEntry
}

function ResourceCard({ resource }: ResourceCardProps) {
  const statusConfig = {
    'Pending': { icon: Clock, color: 'text-yellow-600 bg-yellow-50', label: 'Pending' },
    'In Progress': { icon: Loader2, color: 'text-blue-600 bg-blue-50', label: 'In Progress' },
    'Completed': { icon: CheckCircle2, color: 'text-green-600 bg-green-50', label: 'Completed' },
    'Failed': { icon: XCircle, color: 'text-red-600 bg-red-50', label: 'Failed' },
  }

  const config = statusConfig[resource.status]
  const StatusIcon = config.icon

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">
            {resource.project_name}
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Resource Group: {resource.resource_group_name}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Created by: {resource.user_name}
          </p>
        </div>
        <div className={`flex items-center space-x-1 px-3 py-1 rounded-full ${config.color}`}>
          <StatusIcon className={`h-4 w-4 ${resource.status === 'In Progress' ? 'animate-spin' : ''}`} />
          <span className="text-xs font-medium">{config.label}</span>
        </div>
      </div>

      <div className="mt-4 space-y-2">
        <div className="text-xs text-gray-500">
          {format(new Date(resource.date_of_creation), 'PPpp')}
        </div>

        {resource.azure_resource_group_id && (
          <div className="text-xs">
            <span className="font-medium text-gray-700">Azure RG ID:</span>{' '}
            <span className="text-gray-600 font-mono text-xs">
              {resource.azure_resource_group_id}
            </span>
          </div>
        )}

        {resource.github_repo_url && (
          <div className="text-xs">
            <span className="font-medium text-gray-700">GitHub:</span>{' '}
            <a
              href={resource.github_repo_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {resource.github_repo_url}
            </a>
          </div>
        )}

        {resource.error_message && (
          <div className="mt-2 p-2 bg-red-50 rounded text-xs text-red-800">
            <span className="font-medium">Error:</span> {resource.error_message}
          </div>
        )}
      </div>
    </div>
  )
}

export function ResourceList() {
  const { data: resources, isLoading, error } = useQuery({
    queryKey: ['resources'],
    queryFn: resourcesApi.listResources,
    refetchInterval: 10000, // Refetch every 10 seconds
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">
          Error loading resources: {error.message}
        </p>
      </div>
    )
  }

  if (!resources || resources.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No resources found</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {resources.map((resource) => (
        <ResourceCard key={resource.id} resource={resource} />
      ))}
    </div>
  )
}
