"use client"

import React, { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Download, Loader2, FileText, Share, RefreshCw } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { DashboardHeader } from "@/components/layout/header/dashboard-header"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

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

export default function FormResponsesPage() {
  const params = useParams()
  const router = useRouter()
  const formId = params.id as string
  
  const [form, setForm] = useState<FormData | null>(null)
  const [responses, setResponses] = useState<FormResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  
  const fetchData = async (isRefresh = false) => {
    if (isRefresh) {
      setIsRefreshing(true)
    } else {
      setIsLoading(true)
    }
    
    try {
      // Fetch form details
      const formResponse = await fetch(`/api/forms/${formId}`)
      if (!formResponse.ok) {
        throw new Error('Failed to fetch form')
      }
      
      const formData = await formResponse.json()
      setForm(formData)
      
      // Fetch form responses
      const responsesResponse = await fetch(`/api/forms/${formId}/responses`)
      if (!responsesResponse.ok) {
        throw new Error('Failed to fetch responses')
      }
      
      const responsesData = await responsesResponse.json()
      setResponses(responsesData)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      if (isRefresh) {
        setIsRefreshing(false)
      } else {
        setIsLoading(false)
      }
    }
  }
  
  useEffect(() => {
    fetchData()
  }, [formId])

  const handleRefresh = () => {
    fetchData(true)
  }
  
  const handleDownloadCSV = () => {
    if (!form || !responses.length) return
    
    // Create CSV header row
    const headers = ['Submission Date', ...form.fields.map(field => field.label)]
    
    // Create CSV rows for each response
    const rows = responses.map(response => {
      const date = new Date(response.createdAt).toLocaleString()
      const values = form.fields.map(field => {
        const value = response.data[field.id]
        
        // Handle different types of values
        if (value === undefined || value === null) return ''
        
        // Handle file uploads
        if (typeof value === 'object' && value !== null) {
          if (field.type === 'file' && value.fileName) {
            return value.fileName;
          }
          
          // Handle multi-select
          if ((field.type === 'multi_select' || field.type === 'multiSelect') && Array.isArray(value)) {
            return value.join(', ');
          }
          
          // For checkbox data stored as object with boolean values
          if (field.type === 'checkbox' && !Array.isArray(value)) {
            const selected = Object.entries(value)
              .filter(([_, selected]) => selected === true)
              .map(([option]) => option);
            return selected.join(', ');
          }
          
          // Try to stringify any other objects
          try {
            return JSON.stringify(value);
          } catch (e) {
            return '[Complex Data]';
          }
        }
        
        if (typeof value === 'boolean') return value ? 'Yes' : 'No'
        return String(value)
      })
      
      return [date, ...values]
    })
    
    // Escape CSV values to handle commas, quotes, etc.
    const escapeCSV = (value: string) => {
      if (value.includes(',') || value.includes('"') || value.includes('\n')) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      return value;
    };
    
    // Combine header and rows
    const csvContent = [
      headers.map(h => escapeCSV(h)).join(','),
      ...rows.map(row => row.map(cell => escapeCSV(String(cell))).join(','))
    ].join('\n')
    
    // Create and download the file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `${form.title}-responses.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
  
  const formatResponseValue = (field: FormField, value: any) => {
    if (value === undefined || value === null) return '-'

    // Special rendering for AI fields
    if (field.type === 'ai' || field.is_ai_field) {
      return (
        <div className="flex items-center gap-2 px-2 py-1 bg-gradient-to-r from-purple-50 to-purple-50 border border-purple-200 rounded-md">
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs font-bold">AI</span>
            </div>
            <span className="text-xs text-purple-700 font-medium truncate max-w-[100px]" title={String(value)}>
              {String(value).length > 15 ? String(value).substring(0, 15) + '...' : String(value)}
            </span>
          </div>
        </div>
      );
    }
    
    // Handle file uploads
    if (typeof value === 'object' && value !== null) {
      if (field.type === 'file' && value.fileName) {
        return (
          <div className="flex items-center">
            <FileText className="h-4 w-4 mr-2 text-purple-500" />
            <span className="text-xs text-purple-600 truncate max-w-[120px] inline-block">
              {value.fileName}
            </span>
          </div>
        );
      }
      
      // Handle multi-select
      if ((field.type === 'multi_select' || field.type === 'multiSelect') && Array.isArray(value)) {
        if (value.length === 0) return '-';
        if (value.length === 1) return value[0];
        return (
          <span className="text-xs">
            {value[0]} <span className="text-xs text-muted-foreground">+{value.length - 1}</span>
          </span>
        );
      }
      
      // For checkbox data stored as object with boolean values
      if (field.type === 'checkbox' && !Array.isArray(value)) {
        const selected = Object.entries(value)
          .filter(([_, selected]) => selected === true)
          .map(([option]) => option);
        
        if (selected.length === 0) return '-';
        if (selected.length === 1) return selected[0];
        return (
          <span className="text-xs">
            {selected[0]} <span className="text-xs text-muted-foreground">+{selected.length - 1}</span>
          </span>
        );
      }
      
      // Handle other object types
      try {
        const str = JSON.stringify(value);
        return str.length > 20 ? str.substring(0, 20) + '...' : str;
      } catch {
        return '[Data]';
      }
    }
    
    // Handle boolean values (checkboxes)
    if (field.type === 'checkbox') {
      return value ? <span className="text-green-600">✓</span> : '-';
    }
    
    // Handle dates
    if (field.type === 'date' && value) {
      try {
        return new Date(value).toLocaleDateString();
      } catch (e) {
        return String(value);
      }
    }
    
    // Truncate long text
    if ((field.type === 'text' || field.type === 'long_answer') && 
        typeof value === 'string' && value.length > 30) {
      return (
        <span className="truncate max-w-[120px] inline-block" title={value}>
          {value.substring(0, 30)}...
        </span>
      );
    }
    
    return String(value)
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
          { label: "Responses", href: `/dashboard/forms/${form.id}/responses` }
        ]}
      />
      
      <div className="container mx-auto py-6 px-4 max-w-7xl">
        <div className="flex justify-between items-center mb-6">
          <p className="text-muted-foreground">
            {responses.length} {responses.length === 1 ? 'response' : 'responses'} received
          </p>
          
          <div className="flex gap-2">
            <Button 
              onClick={handleRefresh}
              variant="outline"
              disabled={isRefreshing}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            
            {responses.length > 0 && (
              <Button onClick={handleDownloadCSV}>
                <Download className="h-4 w-4 mr-2" />
                Download CSV
              </Button>
            )}
          </div>
        </div>
        
        {responses.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
            <h3 className="text-lg font-medium mb-2">No responses yet</h3>
            <p className="text-muted-foreground mb-6">
              Share your form to start collecting responses.
            </p>
            <div className="flex justify-center gap-4">
              <Button 
                onClick={() => router.push(`/dashboard/forms/${formId}`)}
                variant="outline"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Form
              </Button>
              <Button 
                onClick={() => {
                  // Open the share form modal
                  router.push(`/dashboard/forms/${formId}?share=true`);
                }}
              >
                <Share className="h-4 w-4 mr-2" />
                Share Form
              </Button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="sticky top-0 bg-white">
                  <TableRow>
                    <TableHead className="w-32">Submitted</TableHead>
                    {form.fields
                      .filter(field => !['h1', 'h2', 'h3'].includes(field.type))
                      .slice(0, 6)
                      .map((field) => (
                        <TableHead key={field.id} className="max-w-[150px]">
                          <div className="truncate flex items-center gap-1">
                            {field.label}
                            {(field.type === 'ai' || field.is_ai_field) && (
                              <div className="w-3 h-3 bg-gradient-to-r from-purple-500 to-purple-500 rounded-full flex items-center justify-center ml-1">
                                <span className="text-white text-[8px] font-bold">AI</span>
                              </div>
                            )}
                          </div>
                        </TableHead>
                      ))}
                    <TableHead className="text-right w-20">View</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {responses.map((response) => (
                    <TableRow 
                      key={response.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => router.push(`/dashboard/forms/${formId}/responses/${response.id}`)}
                    >
                      <TableCell className="font-medium whitespace-nowrap">
                        {new Date(response.createdAt).toLocaleDateString()}
                      </TableCell>
                      {form.fields
                        .filter(field => !['h1', 'h2', 'h3'].includes(field.type))
                        .slice(0, 6)
                        .map((field) => (
                          <TableCell key={field.id} className="max-w-[150px]">
                            {formatResponseValue(field, response.data[field.id])}
                          </TableCell>
                        ))}
                      <TableCell className="text-right">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-8 w-8 p-0"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/dashboard/forms/${formId}/responses/${response.id}`);
                          }}
                        >
                          <FileText className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        )}
      </div>
    </>
  )
} 