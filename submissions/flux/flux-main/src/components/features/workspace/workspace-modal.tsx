"use client"

import React, { useState, useEffect } from 'react'
import { useRouter } from "next/navigation"
import { useUser } from "@clerk/nextjs"
import { Plus } from "lucide-react"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from '@/components/ui/label'
import { toast } from '@/hooks/use-toast'

interface WorkspaceModalProps {
  workspace?: {
    id: string
    name: string
  }
  workspaceToEdit?: {
    id: string
    name: string
  }
  onSuccess?: () => void
  isOpen?: boolean
  onOpenChange?: (open: boolean) => void
}

export function WorkspaceModal({ 
  workspace, 
  workspaceToEdit, 
  onSuccess, 
  isOpen, 
  onOpenChange 
}: WorkspaceModalProps) {
  const { user, isLoaded } = useUser()
  const router = useRouter()
  const [internalOpen, setInternalOpen] = useState(false)
  const [name, setName] = useState((workspace || workspaceToEdit)?.name || '')
  const [isLoading, setIsLoading] = useState(false)
  
  // Use external or internal state based on what's available
  const open = isOpen !== undefined ? isOpen : internalOpen
  const setOpen = (newOpen: boolean) => {
    if (onOpenChange) {
      onOpenChange(newOpen)
    } else {
      setInternalOpen(newOpen)
    }
  }
  
  // Decide which workspace object to use (backwards compatibility)
  const workspaceObj = workspace || workspaceToEdit
  const isEditing = !!workspaceObj
  
  // Add a useEffect to update the name when the workspaceObj or isOpen changes
  useEffect(() => {
    if (isOpen) {
      setName((workspace || workspaceToEdit)?.name || '')
    }
  }, [isOpen, workspace, workspaceToEdit])
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!name.trim()) {
      toast({
        title: 'Workspace name is required',
        variant: 'destructive',
      })
      return
    }
    
    if (!isLoaded || !user) {
      toast({
        title: 'You must be logged in to create a workspace',
        variant: 'destructive',
      })
      return
    }
    
    setIsLoading(true)
    
    try {
      // Create or update workspace
      const url = isEditing 
        ? `/api/workspace/${workspaceObj.id}`
        : '/api/workspace'
      
      const method = isEditing ? 'PATCH' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
        }),
      })
      
      if (!response.ok) {
        throw new Error(`Failed to ${isEditing ? 'update' : 'create'} workspace`)
      }
      
      toast({
        title: `Workspace ${isEditing ? 'updated' : 'created'} successfully`,
      })
      
      setOpen(false)
      
      if (onSuccess) {
        onSuccess()
      }
      
      // Refresh the page to show the new workspace
      router.refresh()
    } catch (error) {
      console.error(`Error ${isEditing ? 'updating' : 'creating'} workspace:`, error)
      toast({
        title: `Failed to ${isEditing ? 'update' : 'create'} workspace`,
        description: 'Please try again later',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="space-y-3">
          <DialogTitle className="text-xl">
            {isEditing ? 'Edit Workspace' : 'Create New Workspace'}
          </DialogTitle>
          <DialogDescription>
            {isEditing 
              ? 'Update your workspace name below.'
              : 'Workspaces help you organize your forms and collaborate with team members.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-3">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-sm font-medium">
              Workspace Name
            </Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full"
              placeholder="e.g. Marketing, HR, Product"
              required
              autoFocus
            />
          </div>
          <DialogFooter className="flex flex-col sm:flex-row sm:justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              className="mt-2 sm:mt-0"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading}
              className="mt-2 sm:mt-0"
            >
              {isLoading
                ? isEditing ? 'Saving...' : 'Creating...'
                : isEditing ? 'Save Changes' : 'Create Workspace'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export function CreateWorkspaceButton({ onSuccess }: { onSuccess?: () => void }) {
  const [open, setOpen] = useState(false)
  
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Workspace
        </Button>
      </DialogTrigger>
      <WorkspaceModal isOpen={open} onOpenChange={setOpen} onSuccess={onSuccess} />
    </Dialog>
  )
} 