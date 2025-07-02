import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { trackFormInteraction } from "@/lib/memory"
import { useUser } from "@clerk/clerk-react"

import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Loader2, Sparkles, ArrowRight } from 'lucide-react'
import { formCreateSchema } from '@/schemas/form'

type FormCreateValues = z.infer<typeof formCreateSchema>

interface FormCreateModalProps {
  isOpen: boolean
  onOpenChange: (open: boolean) => void
  workspaceId?: string
  onSuccess?: (formId: string) => void
}

export function FormCreateModal({
  isOpen,
  onOpenChange,
  workspaceId,
  onSuccess,
}: FormCreateModalProps) {
  const router = useRouter()
  const { user } = useUser()
  const [isCreating, setIsCreating] = useState(false)

  const form = useForm<FormCreateValues>({
    resolver: zodResolver(formCreateSchema),
    defaultValues: {
      title: '',
      description: '',
      workspaceId: workspaceId,
    },
  })

  const onSubmit = async (values: FormCreateValues) => {
    setIsCreating(true)
    
    try {
      const apiUrl = workspaceId 
        ? `/api/workspace/${workspaceId}/forms`
        : '/api/forms'
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      })
      
      if (!response.ok) {
        throw new Error('Failed to create form')
      }
      
      const data = await response.json()
      
      // Track form creation memory for admin insights
      if (user?.id) {
        try {
          await trackFormInteraction(
            user.id,
            data.id,
            values.title,
            "created",
            {
              creation_method: "manual",
              has_description: !!values.description,
              workspace_id: workspaceId,
              creation_timestamp: new Date().toISOString(),
              title_length: values.title.length,
              description_length: values.description?.length || 0
            }
          );
        } catch (memoryError) {
          console.warn("Failed to track form creation memory:", memoryError);
        }
      }
      
      // Close modal and navigate to form editor
      onOpenChange(false)
      
      if (onSuccess) {
        onSuccess(data.id)
      } else {
        router.push(`/dashboard/forms/${data.id}`)
      }
    } catch (error) {
      console.error('Error creating form:', error)
    } finally {
      setIsCreating(false)
    }
  }

  const handleSwitchToAI = () => {
    onOpenChange(false)
    const aiUrl = workspaceId 
      ? `/dashboard/ai?workspace=${workspaceId}`
      : '/dashboard/ai'
    router.push(aiUrl)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create a new form</DialogTitle>
        </DialogHeader>
        
        <div className="py-4 space-y-6">
          {/* AI Option */}
          <div className="p-4 bg-gradient-to-r from-purple-50 to-purple-50 border border-purple-200/60 rounded-lg">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Sparkles className="h-5 w-5 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">Build with AI</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Describe your form in plain English and let AI create it for you instantly.
                </p>
                <Button 
                  onClick={handleSwitchToAI}
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                  size="sm"
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Try AI Builder
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-500 font-medium">Or create manually</span>
            </div>
          </div>

          {/* Manual Form Creation */}
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Form Title</Label>
              <Input
                id="title"
                placeholder="Enter a title for your form"
                {...form.register('title')}
              />
              {form.formState.errors.title && (
                <p className="text-red-500 text-sm">
                  {form.formState.errors.title.message}
                </p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                placeholder="Add a description to help participants understand the purpose of this form"
                {...form.register('description')}
              />
            </div>
            
            <DialogFooter className="pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isCreating}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Form'
                )}
              </Button>
            </DialogFooter>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  )
} 