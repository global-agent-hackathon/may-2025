"use client"

import React, { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Download, Loader2, FileText, Image, ExternalLink, File } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

import { Button } from '@/components/ui/button'
import { DashboardHeader } from "@/components/layout/header/dashboard-header"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'

interface FormData {
  id: string
  title: string
  fields: FormField[]
  workspaceId?: string
  workspace?: {
    id: string
    name: string
  }
}

interface FormField {
  id: string
  type: string
  label: string
  required: boolean
  options?: string[]
  // AI field properties
  is_ai_field?: boolean
  ai_metadata_prompt?: string
  ai_computed_value?: string
}

interface FormResponse {
  id: string
  formId: string
  data: Record<string, any>
  createdAt: string
}

export default function SingleResponsePage() {
  const params = useParams()
  const router = useRouter()
  const formId = params.id as string
  // Access responseId from the dynamic segment
  const responseId = params.responseId as string
  
  const [form, setForm] = useState<FormData | null>(null)
  const [response, setResponse] = useState<FormResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch form details
        const formResponse = await fetch(`/api/forms/${formId}`)
        if (!formResponse.ok) {
          throw new Error('Failed to fetch form')
        }
        
        const formData = await formResponse.json()
        setForm(formData)
        
        // Fetch specific response
        const singleResponseResponse = await fetch(`/api/forms/${formId}/responses/${responseId}`)
        if (!singleResponseResponse.ok) {
          throw new Error('Failed to fetch response')
        }
        
        const responseData = await singleResponseResponse.json()
        setResponse(responseData)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchData()
  }, [formId, responseId])
  
  const renderResponseValue = (field: FormField, value: any) => {
    if (value === undefined || value === null) {
      return <span className="text-muted-foreground">No response</span>
    }

    // Special rendering for AI fields
    if (field.type === 'ai' || field.is_ai_field) {
      return (
        <div className="flex items-center gap-3 p-3 bg-gradient-to-r from-purple-50 to-purple-50 border border-purple-200 rounded-lg">
          <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-white text-sm font-bold">AI</span>
          </div>
          <div className="flex-1">
            <div className="text-purple-700 font-medium">{String(value)}</div>
            {field.ai_metadata_prompt && (
              <div className="text-xs text-purple-600 mt-1 opacity-75">
                Prompt: {field.ai_metadata_prompt}
              </div>
            )}
          </div>
        </div>
      );
    }
    
    if (typeof value === 'object' && value !== null) {
      if (field.type === 'file' && value.fileName) {
        const isPdf = value.fileType === 'application/pdf' || value.extension === 'pdf';
        const isImage = value.fileType?.startsWith('image/') || ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(value.extension);
        
        return (
          <div className="flex flex-col">
            <div className="flex items-center mb-2">
              <span className="text-blue-600 hover:underline cursor-pointer flex items-center" 
                onClick={() => {
                  if (value.content && (isPdf || isImage)) {
                    // Create data URL for preview
                    const dataUrl = `data:${value.fileType};base64,${value.content}`;
                    window.open(dataUrl, '_blank');
                  } else {
                    // Download for non-previewable files
                    const link = document.createElement('a');
                    link.href = `data:${value.fileType};base64,${value.content}`;
                    link.download = value.fileName;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                  }
                }}
              >
                {isPdf ? (
                  <FileText className="h-4 w-4 mr-2" />
                ) : isImage ? (
                  <Image className="h-4 w-4 mr-2" />
                ) : (
                  <File className="h-4 w-4 mr-2" />
                )}
                {value.fileName}
              </span>
              <Badge className="ml-2" variant="outline">
                {(value.fileSize / 1024).toFixed(1)} KB
              </Badge>
            </div>
            
            {/* Preview for PDFs and images */}
            {isPdf && value.content && (
              <div className="mt-2 border rounded-md overflow-hidden">
                <iframe 
                  src={`data:application/pdf;base64,${value.content}`}
                  className="w-full h-72"
                  title={`PDF Preview: ${value.fileName}`}
                ></iframe>
              </div>
            )}
            
            {isImage && value.content && (
              <div className="mt-2 border rounded-md overflow-hidden">
                <img 
                  src={`data:${value.fileType};base64,${value.content}`} 
                  alt={value.fileName}
                  className="max-h-72 max-w-full object-contain mx-auto"
                />
              </div>
            )}
            
            <div className="flex space-x-2 mt-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  // Create a download link from base64 data
                  if (value.content) {
                    const link = document.createElement('a');
                    link.href = `data:${value.fileType};base64,${value.content}`;
                    link.download = value.fileName;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                  }
                }}
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
              
              {(isPdf || isImage) && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    // Open file in new tab
                    if (value.content) {
                      const dataUrl = `data:${value.fileType};base64,${value.content}`;
                      window.open(dataUrl, '_blank');
                    }
                  }}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open
                </Button>
              )}
            </div>
          </div>
        );
      } else if (field.type === 'checkbox' || field.type === 'multi_select') {
        // For checkbox with options or multi_select, show selected options
        if (Array.isArray(value)) {
          return value.join(", ")
        } else {
          // For checkbox data stored as object with boolean values
          return Object.entries(value)
            .filter(([_, selected]) => selected === true)
            .map(([option]) => option)
            .join(", ")
        }
      }
      return JSON.stringify(value)
    }
    
    switch (field.type) {
      case 'date':
        return new Date(value).toLocaleDateString()
      case 'link':
      case 'url':
        return (
          <a 
            href={value} 
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            {value}
          </a>
        )
      default:
        return String(value)
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }
  
  if (!form || !response) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Response not found</h1>
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
          { label: "Responses", href: `/dashboard/forms/${form.id}/responses` },
          { label: "Response Details", href: `/dashboard/forms/${form.id}/responses/${responseId}` }
        ]}
      />
      
      <div className="container mx-auto py-6 px-4 max-w-4xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => router.back()}
              className="mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Responses
            </Button>
            <h1 className="text-2xl font-bold">Response Details</h1>
            <p className="text-muted-foreground">
              Submitted on {new Date(response.createdAt).toLocaleString()}
            </p>
          </div>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Form Response</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {form.fields.map((field) => (
                <div key={field.id} className="space-y-2">
                  <Label className="text-base font-semibold flex items-center gap-2">
                    {field.label}
                    {(field.type === 'ai' || field.is_ai_field) && (
                      <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-purple-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs font-bold">AI</span>
                      </div>
                    )}
                  </Label>
                  <div className="p-3 bg-gray-50 rounded-md">
                    {renderResponseValue(field, response.data[field.id])}
                  </div>
                  <Separator className="my-4" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  )
} 