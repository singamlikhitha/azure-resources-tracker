import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Resource types
export interface ResourceEntry {
  id?: string
  user_name: string
  resource_group_name: string
  date_of_creation: string
  project_name: string
  status: 'Pending' | 'In Progress' | 'Completed' | 'Failed'
  azure_resource_group_id?: string
  github_repo_url?: string
  error_message?: string
}

export interface CreateResourceRequest {
  user_name: string
  resource_group_name: string
  project_name: string
  location?: string
  create_github_repo?: boolean
  tags?: Record<string, string>
}

export interface ResourceCreationResponse {
  status: string
  resource_group_id?: string
  resource_group_name?: string
  github_repo_url?: string
  sharepoint_item_id?: string
  message: string
  created_at: string
}

export interface AzureResourceGroup {
  id: string
  name: string
  location: string
  tags: Record<string, string>
  provisioning_state: string
}

export interface HealthResponse {
  status: string
  version: string
  timestamp: string
  services: Record<string, string>
}

// API functions
export const resourcesApi = {
  // Get all resources
  listResources: async (): Promise<ResourceEntry[]> => {
    const response = await api.get<ResourceEntry[]>('/api/resources')
    return response.data
  },

  // Get specific resource
  getResource: async (itemId: string): Promise<ResourceEntry> => {
    const response = await api.get<ResourceEntry>(`/api/resources/${itemId}`)
    return response.data
  },

  // Create resources manually
  createResources: async (
    request: CreateResourceRequest
  ): Promise<ResourceCreationResponse> => {
    const response = await api.post<ResourceCreationResponse>(
      '/api/resources/create',
      request
    )
    return response.data
  },

  // List Azure resource groups
  listAzureResourceGroups: async (): Promise<AzureResourceGroup[]> => {
    const response = await api.get<AzureResourceGroup[]>(
      '/api/resources/azure/resource-groups'
    )
    return response.data
  },

  // Health check
  healthCheck: async (): Promise<HealthResponse> => {
    const response = await api.get<HealthResponse>('/api/health')
    return response.data
  },

  // Manual trigger
  manualTrigger: async (itemId: string): Promise<{ status: string; item_id: string; message: string }> => {
    const response = await api.post(`/api/webhook/sharepoint/manual-trigger/${itemId}`)
    return response.data
  },
}
