import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { resourcesApi, CreateResourceRequest } from '@/services/api'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'

export function CreateResourcePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState<CreateResourceRequest>({
    user_name: '',
    resource_group_name: '',
    project_name: '',
    location: 'eastus',
    create_github_repo: true,
    tags: {},
  })

  const [customTags, setCustomTags] = useState('')

  const mutation = useMutation({
    mutationFn: resourcesApi.createResources,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] })
      setTimeout(() => navigate('/resources'), 2000)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Parse custom tags
    const tags: Record<string, string> = {}
    if (customTags) {
      customTags.split(',').forEach((tag) => {
        const [key, value] = tag.split(':').map((s) => s.trim())
        if (key && value) {
          tags[key] = value
        }
      })
    }

    mutation.mutate({ ...formData, tags })
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }))
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create Resources</h1>
        <p className="text-gray-600 mt-1">
          Create a new Azure Resource Group and GitHub repository
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8">
        {mutation.isSuccess ? (
          <div className="text-center py-8">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Resources Created Successfully!
            </h2>
            <p className="text-gray-600 mb-4">{mutation.data.message}</p>
            {mutation.data.github_repo_url && (
              <a
                href={mutation.data.github_repo_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                View GitHub Repository
              </a>
            )}
            <p className="text-sm text-gray-500 mt-4">
              Redirecting to resources page...
            </p>
          </div>
        ) : mutation.isError ? (
          <div className="text-center py-8">
            <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Creation Failed
            </h2>
            <p className="text-red-600">
              {mutation.error?.message || 'An error occurred'}
            </p>
            <button
              onClick={() => mutation.reset()}
              className="mt-4 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Try Again
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                User Name *
              </label>
              <input
                type="text"
                name="user_name"
                value={formData.user_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Resource Group Name *
              </label>
              <input
                type="text"
                name="resource_group_name"
                value={formData.resource_group_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="rg-myproject-dev"
              />
              <p className="text-xs text-gray-500 mt-1">
                Alphanumerics, underscores, hyphens, periods allowed (1-90 chars)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Name *
              </label>
              <input
                type="text"
                name="project_name"
                value={formData.project_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="My Awesome Project"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Azure Location
              </label>
              <select
                name="location"
                value={formData.location}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="eastus">East US</option>
                <option value="westus">West US</option>
                <option value="centralus">Central US</option>
                <option value="northeurope">North Europe</option>
                <option value="westeurope">West Europe</option>
                <option value="southeastasia">Southeast Asia</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Custom Tags
              </label>
              <input
                type="text"
                value={customTags}
                onChange={(e) => setCustomTags(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Environment:Development, Team:Engineering"
              />
              <p className="text-xs text-gray-500 mt-1">
                Format: key:value, key:value
              </p>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="create_github_repo"
                checked={formData.create_github_repo}
                onChange={handleChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Create GitHub Repository
              </label>
            </div>

            <div className="flex space-x-4 pt-4">
              <button
                type="submit"
                disabled={mutation.isPending}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors"
              >
                {mutation.isPending && (
                  <Loader2 className="h-4 w-4 animate-spin" />
                )}
                <span>
                  {mutation.isPending ? 'Creating...' : 'Create Resources'}
                </span>
              </button>
              <button
                type="button"
                onClick={() => navigate('/resources')}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
