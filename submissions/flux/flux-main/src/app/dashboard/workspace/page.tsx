"use client"

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, MoreHorizontal, Search } from 'lucide-react'
import { useUser } from '@clerk/clerk-react'
import { toast } from '@/hooks/use-toast'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { DashboardHeader } from "@/components/layout/header/dashboard-header"
import { WorkspaceModal } from "@/components/features/workspace/workspace-modal"

interface WorkspaceItem {
  id: string
  name: string
  emoji?: string
  formCount?: number
  createdAt: Date
  updatedAt: Date
}

export default function WorkspacesPage() {
  const router = useRouter()
  const { user, isLoaded } = useUser()
  const [workspaces, setWorkspaces] = useState<WorkspaceItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [isWorkspaceModalOpen, setIsWorkspaceModalOpen] = useState(false)

  const fetchWorkspaces = async () => {
    if (!isLoaded || !user) return

    setIsLoading(true)

    try {
      // Fetch workspaces
      const workspacesResponse = await fetch(`/api/workspace`)
      if (!workspacesResponse.ok) {
        throw new Error("Failed to fetch workspaces")
      }

      const workspacesData = await workspacesResponse.json()

      // Get form counts for each workspace
      const workspacesWithFormCounts = await Promise.all(
        workspacesData.map(async (workspace: any) => {
          const formsResponse = await fetch(`/api/workspace/${workspace.id}/forms`)
          if (!formsResponse.ok) {
            return {
              ...workspace,
              formCount: 0
            }
          }

          const forms = await formsResponse.json()
          return {
            ...workspace,
            formCount: forms.length
          }
        })
      )

      setWorkspaces(workspacesWithFormCounts)
    } catch (error) {
      console.error("Error fetching workspaces:", error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchWorkspaces()
  }, [user, isLoaded])

  const filteredWorkspaces = searchQuery.trim() === ""
    ? workspaces
    : workspaces.filter(workspace =>
        workspace.name.toLowerCase().includes(searchQuery.toLowerCase())
      )

  const handleCreateWorkspace = () => {
    setIsWorkspaceModalOpen(true)
  }

  const handleWorkspaceCreateSuccess = () => {
    // Refresh workspaces after creation
    fetchWorkspaces()
  }

  return (
    <>
      {/* Pass the workspaceName prop for the /dashboard/workspace route */}
      <DashboardHeader workspaceName="My workspaces" />

      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex flex-col space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-medium">My workspaces</h1>

            <Button
              onClick={handleCreateWorkspace}
              variant="purple"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Workspace
            </Button>
          </div>

          <hr className="border-t border-gray-200" />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {isLoading ? (
              // Loading skeletons
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="border border-gray-200 rounded-lg p-4 animate-pulse">
                  <div className="w-1/2 h-6 bg-gray-200 rounded mb-2"></div>
                  <div className="w-1/3 h-4 bg-gray-200 rounded"></div>
                </div>
              ))
            ) : filteredWorkspaces.length > 0 ? (
              // Workspace grid
              filteredWorkspaces.map((workspace) => (
                <div
                  key={workspace.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 cursor-pointer"
                  onClick={() => router.push(`/dashboard/workspace/${workspace.id}`)}
                >
                  <h3 className="font-medium mb-1">{workspace.name}</h3>
                  <p className="text-sm text-gray-500">
                    {workspace.formCount || 0} form{workspace.formCount !== 1 ? 's' : ''}
                  </p>
                </div>
              ))
            ) : (
              // No workspaces found
              <div className="col-span-full text-center py-8">
                {searchQuery ? (
                  <p className="text-gray-500">No workspaces match your search.</p>
                ) : (
                  <>
                    <p className="text-gray-500 mb-4">No workspaces yet. Create your first workspace to get started.</p>
                    <Button
                      onClick={handleCreateWorkspace}
                      variant="purple"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Create your first workspace
                    </Button>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Workspace Modal */}
      <WorkspaceModal 
        isOpen={isWorkspaceModalOpen}
        onOpenChange={setIsWorkspaceModalOpen}
        onSuccess={handleWorkspaceCreateSuccess}
      />
    </>
  )
} 