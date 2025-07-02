"use client"

import React, { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Loader2, Save, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { DashboardHeader } from "@/components/layout/header/dashboard-header"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Separator } from '@/components/ui/separator'
import { prepareFieldsForAPI } from '@/lib/form-helpers'

interface FormData {
  id: string
  title: string
  description?: string
  published: boolean
  workspaceId?: string
  workspace?: {
    id: string
    name: string
  }
  fields?: any[]
  updatedAt: Date
}

export default function FormSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const formId = params.id as string
  
  const [form, setForm] = useState<FormData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  
  useEffect(() => {
    const fetchForm = async () => {
      try {
        const response = await fetch(`/api/forms/${formId}`)
        if (!response.ok) {
          throw new Error('Failed to fetch form')
        }
        
        const formData = await response.json()
        
        // Log form data for debugging
        console.log('Form data loaded in settings:', {
          hasFields: Array.isArray(formData.fields),
          fieldCount: Array.isArray(formData.fields) ? formData.fields.length : 0,
          hasBanner: !!formData.banner
        });
        
        setForm(formData)
      } catch (error) {
        console.error('Error fetching form:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchForm()
  }, [formId])
  
  const handleInputChange = (field: keyof FormData, value: any) => {
    if (!form) return
    
    setForm({
      ...form,
      [field]: value
    })
  }
  
  const saveSettings = async () => {
    if (!form) return;
    
    setIsSaving(true);
    
    try {
      const payload = {
        ...form,
        workspaceId: form.workspaceId || null,
        fields: form.fields || [], // Use existing fields or empty array
      };
      
      // Map field types to match schema if fields exist
      if (Array.isArray(payload.fields) && payload.fields.length > 0) {
        payload.fields = prepareFieldsForAPI(payload.fields);
      }
      
      const response = await fetch(`/api/forms/${formId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error saving form settings:', errorData);
        throw new Error(`Failed to save form settings: ${errorData.error || ''}`);
      }
      
      const updatedForm = await response.json();
      setForm(updatedForm);
    } catch (error) {
      console.error('Error saving form settings:', error);
    } finally {
      setIsSaving(false);
    }
  };
  
  const deleteForm = async () => {
    try {
      const response = await fetch(`/api/forms/${formId}/trash`, {
        method: 'PATCH',
      });
      
      if (!response.ok) {
        throw new Error('Failed to move form to trash');
      }
      
      if (form?.workspaceId) {
        router.push(`/dashboard/workspace/${form.workspaceId}`);
      } else {
        router.push('/dashboard/workspace');
      }
    } catch (error) {
      console.error('Error moving form to trash:', error);
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }
  
  if (!form) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Form not found</h1>
        <Button onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Go Back
        </Button>
      </div>
    )
  }
  
  return (
    <>
      <DashboardHeader
        workspaceId={form.workspaceId}
        workspaceName={form.workspace?.name || "My Workspace"}
        formId={form.id}
        formName={form.title}
        breadcrumbs={[
          { label: form.workspace?.name || "My Workspace", href: `/dashboard/workspace/${form.workspaceId || ''}` },
          { label: form.title, href: `/dashboard/forms/${form.id}` },
          { label: "Settings", href: `/dashboard/forms/${form.id}/settings` }
        ]}
      />
      
      <div className="container mx-auto py-6 px-4 max-w-5xl">
        <div className="grid gap-6">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold mb-4">Form Information</h2>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="title">Form Title</Label>
                <Input
                  id="title"
                  value={form.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="description">Form Description</Label>
                <Textarea
                  id="description"
                  value={form.description || ''}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="mt-1"
                  placeholder="Provide a description for your form"
                />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold mb-4">Form Status</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Published</h3>
                <p className="text-sm text-muted-foreground">
                  When published, people can submit responses to your form.
                </p>
              </div>
              <Switch
                checked={form.published}
                onCheckedChange={(checked: boolean) => handleInputChange('published', checked)}
              />
            </div>
            
            {form.published && (
              <div className="mt-4 p-4 bg-blue-50 text-blue-800 rounded-md text-sm">
                Your form is published. Anyone with the link can submit responses.
              </div>
            )}
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold mb-4 text-red-600">Danger Zone</h2>
            <Separator className="mb-4" />
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Move to Trash</h3>
                <p className="text-sm text-muted-foreground">
                  Move this form to trash. You can restore it from the trash later.
                </p>
              </div>
              <Button 
                variant="destructive"
                onClick={() => setShowDeleteDialog(true)}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Move to Trash
              </Button>
            </div>
          </div>
          
          <div className="flex justify-end mt-2">
            <Button onClick={saveSettings} disabled={isSaving}>
              <Save className="h-4 w-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>
        
        <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Move to Trash</DialogTitle>
              <DialogDescription>
                Are you sure you want to move this form to trash? You can restore it from the trash later.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="mt-4">
              <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={deleteForm}>
                Move to Trash
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </>
  )
} 