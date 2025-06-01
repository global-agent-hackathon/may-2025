export interface WorkspaceData {
  id: string
  name: string
  createdAt: Date
  updatedAt: Date
}

export interface FormItem {
  id: string
  title: string
  description?: string | null
  updatedAt: Date
  published?: boolean
  submissionCount?: number
}

export async function getWorkspace(workspaceId: string): Promise<WorkspaceData> {
  const response = await fetch(`/api/workspace/${workspaceId}`)
  if (!response.ok) {
    throw new Error("Failed to fetch workspace details")
  }
  return response.json()
}

export async function getWorkspaceForms(workspaceId: string): Promise<FormItem[]> {
  const response = await fetch(`/api/workspace/${workspaceId}/forms`)
  if (!response.ok) {
    throw new Error("Failed to fetch workspace forms")
  }
  return response.json()
}

export async function deleteWorkspace(workspaceId: string) {
  // First, move all forms to trash
  const forms = await getWorkspaceForms(workspaceId)
  await Promise.all(
    forms.map(form => 
      fetch(`/api/forms/${form.id}/trash`, {
        method: 'PATCH',
      })
    )
  )
  
  // Then delete the workspace
  const response = await fetch(`/api/workspace/${workspaceId}`, {
    method: 'DELETE',
  })
  
  if (!response.ok) {
    throw new Error('Failed to delete workspace')
  }
  
  return response.json()
}

export async function deleteForm(formId: string) {
  const response = await fetch(`/api/forms/${formId}/trash`, {
    method: 'PATCH',
  })
  
  if (!response.ok) {
    throw new Error('Failed to move form to trash')
  }
  
  return response.json()
} 