import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor to convert PascalCase API responses to snake_case
api.interceptors.response.use((response) => {
  // Only transform resource arrays/objects that have UserName field
  if (Array.isArray(response.data) && response.data.length > 0 && 'UserName' in response.data[0]) {
    response.data = response.data.map((item: any) => ({
      id: item.id,
      user_name: item.UserName || item.user_name,
      resource_group_name: item.ResourceGroupName || item.resource_group_name,
      date_of_creation: item.DateOfCreation || item.date_of_creation,
      project_name: item.ProjectName || item.project_name,
      status: item.Status || item.status,
      azure_resource_group_id: item.AzureResourceGroupId || item.azure_resource_group_id,
      github_repo_url: item.GitHubRepoUrl || item.github_repo_url,
      error_message: item.ErrorMessage || item.error_message
    }))
  } else if (response.data && typeof response.data === 'object' && 'UserName' in response.data) {
    // Single object response
    const item = response.data
    response.data = {
      id: item.id,
      user_name: item.UserName || item.user_name,
      resource_group_name: item.ResourceGroupName || item.resource_group_name,
      date_of_creation: item.DateOfCreation || item.date_of_creation,
      project_name: item.ProjectName || item.project_name,
      status: item.Status || item.status,
      azure_resource_group_id: item.AzureResourceGroupId || item.azure_resource_group_id,
      github_repo_url: item.GitHubRepoUrl || item.github_repo_url,
      error_message: item.ErrorMessage || item.error_message
    }
  }
  // Otherwise, leave response.data unchanged (for subscriptions, health, etc.)
  return response
})

//Resource types
export interface ResourceEntry {
  id?: string
  user_name: string
  cloud_platform: string
  resource_type: string
  resource_group_name: string
  date_of_creation: string
  project_name: string
  status: 'Pending' | 'In Progress' | 'Completed' | 'Failed'
  azure_resource_group_id?: string
  resource_id?: string
  github_repo_url?: string
  error_message?: string
  subscription_id?: string
}

export interface CreateResourceRequest {
  user_name: string
  cloud_platform: string
  resource_type: string
  resource_group_name: string
  project_name: string
  location?: string
  subscription_id?: string
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

export interface Subscription {
  subscription_id: string
  display_name: string
  state: string
}

export interface CloudPlatform {
  value: string
  label: string
}

export interface ResourceType {
  value: string
  label: string
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

  // List Azure subscriptions
  listSubscriptions: async (): Promise<Subscription[]> => {
    const response = await api.get<Subscription[]>('/api/resources/subscriptions')
    return response.data
  },

  // List cloud platforms
  listCloudPlatforms: async (): Promise<CloudPlatform[]> => {
    const response = await api.get<CloudPlatform[]>('/api/resources/cloud-platforms')
    return response.data
  },

  // List resource types
  listResourceTypes: async (cloudPlatform?: string): Promise<ResourceType[]> => {
    const params = cloudPlatform ? { cloud_platform: cloudPlatform } : {}
    const response = await api.get<ResourceType[]>('/api/resources/resource-types', { params })
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
