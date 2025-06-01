"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Plus, MoreHorizontal, Trash2, Edit, Search, Sparkles } from "lucide-react"
import { useUser } from "@clerk/clerk-react"
import { useQueryClient } from "@tanstack/react-query"

import { Button } from "@/components/ui/button"
import { WorkspaceModal } from "@/components/features/workspace/workspace-modal"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { toast } from "@/hooks/use-toast"
import { useData } from "@/contexts/DataContext"
import { FormCreateModal } from "@/components/forms/form-create-modal"
import { useQueryData } from "@/hooks/use-query-data"
import { useMutationData } from "@/hooks/use-mutation-data"
import { deleteForm, deleteWorkspace, getWorkspace, getWorkspaceForms } from "@/lib/api/workspace"
import type { FormItem, WorkspaceData } from "@/lib/api/workspace"
import { Input } from "@/components/ui/input"
import { 
  AlertDialog, 
  AlertDialogAction, 
  AlertDialogCancel, 
  AlertDialogContent, 
  AlertDialogDescription,
  AlertDialogFooter, 
  AlertDialogHeader, 
  AlertDialogTitle 
} from "@/components/ui/alert-dialog"
import { AIFormBuilder } from "@/components/forms/ai-form-builder"

interface WorkspaceContentProps {
  workspaceId: string
}

interface WorkspaceMutationContext {
  previousWorkspaces?: any[]
}

interface FormMutationContext {
  previousForms?: FormItem[]
}

export const WorkspaceContent = ({ workspaceId }: WorkspaceContentProps) => {
  const router = useRouter()
  const { user } = useUser()
  const { forceRefresh } = useData()
  const queryClient = useQueryClient()

  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [showDeleteWorkspaceDialog, setShowDeleteWorkspaceDialog] = useState(false)
  const [isFormCreateModalOpen, setIsFormCreateModalOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [showAIFormBuilder, setShowAIFormBuilder] = useState(false)

  // Queries
  const { data: workspace, isPending: isWorkspaceLoading } = useQueryData<WorkspaceData>(
    ["workspace", workspaceId],
    () => getWorkspace(workspaceId)
  )

  const { data: formsData, isPending: isFormsLoading } = useQueryData<FormItem[]>(
    ["workspace", workspaceId, "forms"],
    () => getWorkspaceForms(workspaceId)
  )

  // Ensure forms is always an array
  const forms = Array.isArray(formsData) ? formsData : [];

  // Filter forms based on search
  const filteredForms = forms.filter(
    (form: FormItem) =>
      !searchQuery ||
      form.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (form.description && form.description.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  // Mutations
  const deleteMutation = useMutationData<void, string, WorkspaceMutationContext>(
    ["delete-workspace"],
    () => deleteWorkspace(workspaceId),
    ["workspaces"],
    () => {
      toast({
        title: 'Workspace deleted',
        description: `The workspace "${workspace?.name}" has been deleted and its forms moved to trash.`,
      })
      router.push('/dashboard/workspace')
    },
    {
      onMutate: async (workspaceId) => {
        // Cancel outgoing refetches
        await queryClient.cancelQueries({ queryKey: ["workspaces"] })
        await queryClient.cancelQueries({ queryKey: ["workspace", workspaceId] })
        
        // Snapshot current data
        const previousWorkspaces = queryClient.getQueryData<any[]>(["workspaces"])
        
        // Optimistically remove the workspace from the list
        queryClient.setQueryData(["workspaces"], (old: any[]) => 
          old?.filter(w => w.id !== workspaceId) ?? []
        )
        
        return { previousWorkspaces }
      },
      onError: (err, variables, context) => {
        // Restore previous data on error
        if (context?.previousWorkspaces) {
          queryClient.setQueryData(["workspaces"], context.previousWorkspaces)
        }
        toast({
          title: "Error",
          description: "Failed to delete workspace"
        })
      }
    }
  )

  const formDeleteMutation = useMutationData<void, string, FormMutationContext>(
    ["delete-form"],
    (formId: string) => deleteForm(formId),
    ["workspace", workspaceId, "forms"],
    () => {
      toast({
        title: 'Form deleted',
        description: 'The form has been moved to trash.',
      })
    },
    {
      onMutate: async (formId) => {
        // Cancel outgoing refetches
        await queryClient.cancelQueries({ queryKey: ["workspace", workspaceId, "forms"] })
        
        // Snapshot current data
        const previousForms = queryClient.getQueryData<FormItem[]>(["workspace", workspaceId, "forms"])
        
        // Optimistically remove the form from the list
        queryClient.setQueryData(["workspace", workspaceId, "forms"], (old: FormItem[]) => 
          old?.filter(f => f.id !== formId) ?? []
        )
        
        return { previousForms }
      },
      onError: (err, variables, context) => {
        // Restore previous data on error
        if (context?.previousForms) {
          queryClient.setQueryData(["workspace", workspaceId, "forms"], context.previousForms)
        }
        toast({
          title: "Error",
          description: "Failed to delete form"
        })
      }
    }
  )

  const handleCreateForm = () => {
    if (!workspace) return
    setIsFormCreateModalOpen(true)
  }

  const handleFormCreateSuccess = (formId: string) => {
    router.push(`/dashboard/forms/${formId}`)
  }

  const handleEditWorkspace = () => {
    if (!workspace) return
    setIsEditModalOpen(true)
  }

  const handleDeleteWorkspace = async () => {
    if (!workspace) return
    deleteMutation.mutate(workspaceId)
  }

  const handleDeleteForm = async (e: React.MouseEvent, formId: string) => {
    e.stopPropagation()
    formDeleteMutation.mutate(formId)
  }

  const handleCreateAIForm = () => {
    if (!workspace) return
    setShowAIFormBuilder(true)
  }

  const formatTimeAgo = (date: Date) => {
    if (!date) return ""
    return `${new Date(date).toLocaleDateString(undefined, { day: "numeric", month: "short" })} ago`
  }

  if (isWorkspaceLoading || !workspace) {
    return (
      <div className="space-y-8">
        {/* Header skeleton */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-7 w-48 bg-gray-100 rounded animate-pulse" />
            <div className="h-4 w-24 bg-gray-50 rounded animate-pulse" />
          </div>
          <div className="flex items-center gap-2">
            <div className="h-8 w-20 bg-gray-50 rounded animate-pulse" />
            <div className="h-8 w-24 bg-gray-100 rounded animate-pulse" />
            <div className="h-8 w-8 bg-gray-50 rounded animate-pulse" />
          </div>
        </div>

        {/* Search skeleton */}
        <div className="w-80">
          <div className="h-9 bg-gray-50 rounded-md animate-pulse" />
        </div>

        {/* Forms list skeleton */}
        <div className="space-y-1">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center justify-between py-3 px-3">
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <div className="h-4 w-32 bg-gray-100 rounded animate-pulse" />
                  <div className="h-4 w-12 bg-gray-50 rounded animate-pulse" />
                </div>
                <div className="flex items-center gap-3">
                  <div className="h-3 w-20 bg-gray-50 rounded animate-pulse" />
                  <div className="h-3 w-24 bg-gray-50 rounded animate-pulse" />
                </div>
              </div>
              <div className="h-7 w-7 bg-gray-50 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header section */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-medium text-gray-900">
            {isWorkspaceLoading ? (
              <div className="h-8 bg-gray-100 animate-pulse rounded w-[200px]" />
            ) : (
              workspace?.name || "Workspace"
            )}
          </h1>
          <p className="text-sm text-gray-500">
            {isWorkspaceLoading ? (
              <div className="h-4 bg-gray-100 animate-pulse rounded w-[120px]" />
            ) : (
              `${filteredForms.length} ${filteredForms.length === 1 ? 'form' : 'forms'}`
            )}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCreateAIForm}
            className="gap-2 border-gray-200 text-gray-700 hover:bg-gray-50 hover:border-gray-300"
          >
            <Sparkles className="h-4 w-4" />
            AI Form
          </Button>
          <Button
            onClick={handleCreateForm}
            size="sm"
            className="gap-2 bg-gray-900 hover:bg-gray-800 text-white border-0"
          >
            <Plus className="h-4 w-4" />
            New Form
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-400 hover:text-gray-600 hover:bg-gray-50">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleEditWorkspace}>
                <Edit className="h-4 w-4 mr-2" />
                Edit workspace
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => setShowDeleteWorkspaceDialog(true)}
                className="text-red-600 focus:text-red-600"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete workspace
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Search section */}
      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search forms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 border-gray-200 focus:border-gray-300 focus:ring-0 bg-white"
          />
        </div>
      </div>

      {/* Forms list */}
      {isFormsLoading ? (
        <div className="space-y-1">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="flex items-center justify-between py-3 px-3">
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <div className="h-4 w-40 bg-gray-100 rounded animate-pulse" />
                  <div className="h-4 w-10 bg-gray-50 rounded-full animate-pulse" />
                </div>
                <div className="flex items-center gap-3">
                  <div className="h-3 w-16 bg-gray-50 rounded animate-pulse" />
                  <div className="h-3 w-20 bg-gray-50 rounded animate-pulse" />
                </div>
              </div>
              <div className="h-7 w-7 bg-gray-50 rounded animate-pulse opacity-0" />
            </div>
          ))}
        </div>
      ) : filteredForms.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="rounded-lg bg-gray-50 p-3 mb-4">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <h3 className="text-base font-medium text-gray-900 mb-1">No forms found</h3>
          <p className="text-sm text-gray-500 mb-6">
            {searchQuery ? "Try adjusting your search term" : "Get started by creating your first form"}
          </p>
          {!searchQuery && (
            <div className="flex gap-3">
              <Button onClick={handleCreateAIForm} variant="outline" className="gap-2 border-gray-200 text-gray-700 hover:bg-gray-50">
                <Sparkles className="h-4 w-4" />
                Create with AI
              </Button>
              <Button onClick={handleCreateForm} className="gap-2 bg-gray-900 hover:bg-gray-800 text-white">
                <Plus className="h-4 w-4" />
                New Form
              </Button>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-1">
          {filteredForms.map((form) => (
            <div
              key={form.id}
              className="group relative hover:bg-gray-50/60 rounded-md transition-colors duration-150 cursor-pointer"
              onClick={() => router.push(`/dashboard/forms/${form.id}`)}
            >
              <div className="flex items-center justify-between py-3 px-3">
                {/* Left side - Form info */}
                <div className="flex-1 min-w-0 mr-4">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium text-gray-900 truncate text-sm">
                      {form.title}
                    </h3>
                    {!form.published && (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                        Draft
                      </span>
                    )}
                    {form.published && (
                      <div className="flex items-center gap-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                        <span className="text-xs text-gray-500">Live</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span>{form.submissionCount || 0} {(form.submissionCount || 0) === 1 ? 'response' : 'responses'}</span>
                    <span>Updated {formatTimeAgo(new Date(form.updatedAt))}</span>
                  </div>
                </div>

                {/* Right side - Actions */}
                <div className="flex items-center">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                      >
                        <MoreHorizontal className="h-3.5 w-3.5" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/dashboard/forms/${form.id}/edit`);
                      }}>
                        <Edit className="h-4 w-4 mr-2" />
                        Edit form
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={(e) => handleDeleteForm(e, form.id)}
                        className="text-red-600 focus:text-red-600"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete form
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      <WorkspaceModal
        workspace={workspace}
        isOpen={isEditModalOpen}
        onOpenChange={setIsEditModalOpen}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ["workspace", workspaceId] });
          queryClient.invalidateQueries({ queryKey: ["workspaces"] });
        }}
      />

      <FormCreateModal
        isOpen={isFormCreateModalOpen}
        onOpenChange={setIsFormCreateModalOpen}
        workspaceId={workspaceId}
        onSuccess={handleFormCreateSuccess}
      />

      <AIFormBuilder
        isOpen={showAIFormBuilder}
        onOpenChange={setShowAIFormBuilder}
        workspaceId={workspaceId}
      />

      <AlertDialog open={showDeleteWorkspaceDialog} onOpenChange={setShowDeleteWorkspaceDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Workspace</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this workspace? All forms in this workspace will be moved to trash and can be restored later.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteWorkspace}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete Workspace
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
} 