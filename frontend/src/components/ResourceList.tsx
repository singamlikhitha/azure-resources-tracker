import { useQuery } from '@tanstack/react-query'
import { resourcesApi } from '@/services/api'
import { Clock, CheckCircle2, XCircle, Loader2, ExternalLink, Search } from 'lucide-react'
import { format } from 'date-fns'
import { useState } from 'react'

interface StatusBadgeProps {
  status: string
}

function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig: Record<string, { icon: any; color: string; label: string }> = {
    'Pending': { icon: Clock, color: 'text-yellow-700 bg-yellow-100', label: 'Pending' },
    'In Progress': { icon: Loader2, color: 'text-blue-700 bg-blue-100', label: 'In Progress' },
    'Completed': { icon: CheckCircle2, color: 'text-green-700 bg-green-100', label: 'Completed' },
    'Failed': { icon: XCircle, color: 'text-red-700 bg-red-100', label: 'Failed' },
  }

  const config = statusConfig[status] || statusConfig['Pending']
  const StatusIcon = config.icon

  return (
    <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full ${config.color}`}>
      <StatusIcon className={`h-3 w-3 ${status === 'In Progress' ? 'animate-spin' : ''}`} />
      <span className="text-xs font-medium">{config.label}</span>
    </div>
  )
}

export function ResourceList() {
  const [searchQuery, setSearchQuery] = useState('')

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

  // Filter resources based on search query
  const filteredResources = resources.filter((resource) => {
    const query = searchQuery.toLowerCase()
    return (
      resource.resource_group_name?.toLowerCase().includes(query) ||
      resource.project_name?.toLowerCase().includes(query) ||
      resource.user_name?.toLowerCase().includes(query) ||
      resource.cloud_platform?.toLowerCase().includes(query) ||
      resource.resource_type?.toLowerCase().includes(query) ||
      resource.azure_resource_group_id?.toLowerCase().includes(query) ||
      resource.resource_id?.toLowerCase().includes(query)
    )
  })

  // Group resources by resource group name
  const groupedResources = filteredResources.reduce((acc, resource) => {
    const rgName = resource.resource_group_name || 'Ungrouped'
    if (!acc[rgName]) {
      acc[rgName] = []
    }
    acc[rgName].push(resource)
    return acc
  }, {} as Record<string, typeof resources>)

  // Sort resource groups alphabetically
  const sortedResourceGroups = Object.keys(groupedResources).sort()

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search by resource group, project name, or created by..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
            >
              <XCircle className="h-5 w-5" />
            </button>
          )}
        </div>
        {searchQuery && (
          <p className="mt-2 text-sm text-gray-600">
            Found {filteredResources.length} result{filteredResources.length !== 1 ? 's' : ''} for "{searchQuery}"
          </p>
        )}
      </div>

      {/* Resource Groups Tables */}
      {sortedResourceGroups.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No matching resources found</p>
        </div>
      ) : (
        <div className="space-y-8">
      {sortedResourceGroups.map((rgName) => {
        const rgResources = groupedResources[rgName]
        return (
          <div key={rgName} className="bg-white rounded-lg shadow overflow-hidden">
            {/* Resource Group Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">
                    {rgName}
                  </h3>
                  <p className="text-blue-100 text-sm mt-1">
                    {rgResources.length} resource{rgResources.length !== 1 ? 's' : ''}
                  </p>
                </div>
                {rgResources[0]?.azure_resource_group_id && (
                  <div className="text-xs text-blue-100 font-mono max-w-md truncate" title={rgResources[0].azure_resource_group_id}>
                    {rgResources[0].azure_resource_group_id}
                  </div>
                )}
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cloud Platform
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Resource Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Project Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created By
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      GitHub Repo
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {rgResources.map((resource) => (
                    <tr key={resource.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            resource.cloud_platform === 'Azure' ? 'bg-blue-100 text-blue-800' :
                            resource.cloud_platform === 'GCP' ? 'bg-green-100 text-green-800' :
                            resource.cloud_platform === 'AWS' ? 'bg-orange-100 text-orange-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {resource.cloud_platform || 'Azure'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {resource.resource_type || 'Resource Group'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {resource.project_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {resource.user_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {resource.date_of_creation 
                            ? format(new Date(resource.date_of_creation), 'MMM dd, yyyy HH:mm')
                            : 'Not available'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={resource.status} />
                        {resource.error_message && (
                          <div className="mt-1 text-xs text-red-600 max-w-xs truncate" title={resource.error_message}>
                            {resource.error_message}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {resource.github_repo_url ? (
                          <a
                            href={resource.github_repo_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        ) : (
                          <span className="text-sm text-gray-400">N/A</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )
      })}
      </div>
      )}
    </div>
  )
}
