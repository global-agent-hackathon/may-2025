/* eslint-disable @typescript-eslint/no-unused-vars */
"use client"

import * as React from 'react'
import { useEffect, useState } from "react"
import { useParams, useRouter, useSearchParams } from "next/navigation"
import { 
  MoreHorizontal, 
  Share, 
  Edit, 
  Trash, 
  FileText,
  Loader2,
  Download,
  Settings,
  AlertCircle,
  CheckCircle,
  Copy,
  Eye,
  BarChart2,
  Inbox,
  MessageSquare,
  TestTube,
  ArrowLeft
} from "lucide-react"
import { toast } from "@/hooks/use-toast"
import { useUser } from "@clerk/nextjs"
import Link from "next/link"
import { faker } from '@faker-js/faker'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { FormattedDate } from "@/components/ui/formatted-date"
import { DashboardHeader } from "@/components/layout/header/dashboard-header"
import { useData } from "@/contexts/DataContext"
import { ChatThreadManager } from "@/components/chat/ChatThreadManager"

interface FormSubmission {
  id: string
  formId: string
  createdAt: Date
  data: Record<string, any>
}

interface FormData {
  id: string
  title: string
  description?: string
  workspaceId?: string
  workspace?: {
    id: string
    name: string
  }
  fields: FormField[]
  updatedAt: Date
  published?: boolean
  banner?: string
}

interface FormField {
  id: string
  type: string
  label: string
  required: boolean
  placeholder?: string
  options?: string[]
  fileSize?: number
  fileTypes?: string[]
  // AI field properties
  is_ai_field?: boolean
  ai_metadata_prompt?: string
  ai_computed_value?: string
}

// Compact summary card component
function SummaryCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg bg-card/50 p-3 flex justify-between items-center">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="text-lg font-semibold text-foreground">{value}</div>
    </div>
  )
}

export default function FormDashboardPage() {
  const router = useRouter()
  const params = useParams()
  const formId = params.id as string
  const { forceRefresh } = useData()
  const { user, isLoaded } = useUser()
  const searchParams = useSearchParams()

  const [form, setForm] = useState<FormData | null>(null)
  const [submissions, setSubmissions] = useState<FormSubmission[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showShareModal, setShowShareModal] = useState(false)
  const [shareDialogOpen, setShareDialogOpen] = useState(false)
  const [submissionTitle, setSubmissionTitle] = useState("Most Recent Responses")
  const [loading, setLoading] = useState(true)
  const [copying, setCopying] = useState(false)
  const [copied, setCopied] = useState(false)
  const [generatingTestData, setGeneratingTestData] = useState(false)
  
  useEffect(() => {
    const fetchFormData = async () => {
      if (!formId) return

      setIsLoading(true)

      try {
        // Fetch form details
        const formResponse = await fetch(`/api/forms/${formId}`)
        if (!formResponse.ok) {
          throw new Error("Failed to fetch form")
        }
        const formData = await formResponse.json()
        setForm(formData)
        
        // Fetch form submissions with more detailed error handling
        console.log(`Fetching responses for form: ${formId}`)
        
        const responsesResponse = await fetch(`/api/forms/${formId}/responses`)
        if (responsesResponse.ok) {
          const responsesData = await responsesResponse.json()
          console.log(`Successfully fetched ${responsesData.length} responses:`, responsesData)
          setSubmissions(responsesData)
        } else {
          const errorText = await responsesResponse.text()
          console.error(`Failed to fetch responses: ${responsesResponse.status} ${responsesResponse.statusText}`, errorText)
        }
      } catch (error) {
        console.error("Error fetching data:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchFormData()
  }, [formId])

  // Handle share dialog from query param
  useEffect(() => {
    if (searchParams?.get("share") === "true") {
      setShareDialogOpen(true)
    }
  }, [searchParams])

  const handleShareForm = () => {
    setShareDialogOpen(true)
  }

  const handleEditForm = () => {
    router.push(`/dashboard/forms/${formId}`)
  }

  const handleDeleteForm = async () => {
    if (!form) return;
    
    try {
      const response = await fetch(`/api/forms/${formId}/trash`, {
        method: 'PATCH',
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete form');
      }
      
      // Refresh data context to update all places showing forms
      await forceRefresh();
      
      // Navigate to workspace if available, otherwise go to dashboard
      if (form.workspaceId) {
        router.push(`/dashboard/workspace/${form.workspaceId}`);
      } else {
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Error deleting form:', error);
    }
  };

  const handlePublishChange = async (published: boolean) => {
    if (!form) return

    try {
      const response = await fetch(`/api/forms/${formId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form,
          published,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to update form publish status")
      }

      const updatedForm = await response.json()
      setForm(updatedForm)

      return Promise.resolve()
    } catch (error) {
      console.error("Error updating form publish status:", error)
      return Promise.reject(error)
    }
  }

  const renderSubmissionValue = (value: any, field: FormField, isModal: boolean = false) => {
    if (value === undefined || value === null) {
      return (
        <div className="flex items-center gap-2 text-gray-400">
          <div className="w-1.5 h-1.5 bg-gray-300 rounded-full"></div>
          <span className="text-sm">No response</span>
        </div>
      )
    }

    // Special rendering for AI fields
    if (field.type === 'ai' || field.is_ai_field) {
      return (
        <div className="bg-gradient-to-r from-purple-50 to-purple-50 border border-purple-200 rounded-lg p-3">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-purple-500 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-white text-xs font-bold">AI</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-purple-900 leading-relaxed">
                {String(value)}
              </p>
              <div className="flex items-center gap-1 mt-2">
                <div className="w-1 h-1 bg-purple-400 rounded-full"></div>
                <span className="text-xs text-purple-600">AI Generated</span>
              </div>
            </div>
          </div>
        </div>
      );
    }
    
    // Handle objects (like files)
    if (typeof value === 'object' && value !== null) {
      if (field.type === 'file' && value.fileName) {
        return (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileText className="h-4 w-4 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-blue-900 truncate">
                  {value.fileName}
                </p>
                <p className="text-xs text-blue-600">
                  {(value.fileSize / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
          </div>
        );
      }
      
      // Handle multi-select
      if ((field.type === 'multi_select' || field.type === 'multiSelect') && Array.isArray(value)) {
        if (value.length === 0) return (
          <div className="flex items-center gap-2 text-gray-400">
            <div className="w-1.5 h-1.5 bg-gray-300 rounded-full"></div>
            <span className="text-sm">No selection</span>
          </div>
        );
        
        return (
          <div className="space-y-1">
            {value.slice(0, 2).map((item, index) => (
              <div key={index} className="inline-flex items-center gap-1 bg-gray-100 text-gray-700 px-2 py-1 rounded-md text-xs mr-1">
                {item}
              </div>
            ))}
            {value.length > 2 && (
              <div className="inline-flex items-center gap-1 bg-gray-200 text-gray-600 px-2 py-1 rounded-md text-xs">
                +{value.length - 2} more
              </div>
            )}
          </div>
        );
      }
      
      // For checkbox data stored as object with boolean values
      if (field.type === 'checkbox' && !Array.isArray(value)) {
        const selected = Object.entries(value)
          .filter(([_, selected]) => selected === true)
          .map(([option]) => option);
        
        if (selected.length === 0) return (
          <div className="flex items-center gap-2 text-gray-400">
            <div className="w-1.5 h-1.5 bg-gray-300 rounded-full"></div>
            <span className="text-sm">None selected</span>
          </div>
        );
        
        return (
          <div className="space-y-1">
            {selected.slice(0, 2).map((item, index) => (
              <div key={index} className="inline-flex items-center gap-1 bg-green-100 text-green-700 px-2 py-1 rounded-md text-xs mr-1">
                ✓ {item}
              </div>
            ))}
            {selected.length > 2 && (
              <div className="inline-flex items-center gap-1 bg-gray-200 text-gray-600 px-2 py-1 rounded-md text-xs">
                +{selected.length - 2} more
              </div>
            )}
          </div>
        );
      }
      
      // If it's some other object type, stringify it
      try {
        const str = JSON.stringify(value);
        return (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-2">
            <code className="text-xs text-gray-600 font-mono">
              {str.length > 50 ? str.substring(0, 50) + '...' : str}
            </code>
          </div>
        );
      } catch (e) {
        return (
          <div className="flex items-center gap-2 text-gray-400">
            <div className="w-1.5 h-1.5 bg-gray-300 rounded-full"></div>
            <span className="text-sm">Complex data</span>
          </div>
        );
      }
    }
    
    // Handle simple types
    if (field.type === 'checkbox') {
      return value ? (
        <div className="inline-flex items-center gap-2 bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
          <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
          Yes
        </div>
      ) : (
        <div className="inline-flex items-center gap-2 bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full"></div>
          No
        </div>
      );
    }
    
    // Handle dates
    if (field.type === 'date' && value) {
      try {
        return (
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
            <div className="text-sm font-medium text-blue-900">
              <FormattedDate date={value} format="short" />
            </div>
            <div className="text-xs text-blue-600">Date response</div>
          </div>
        );
      } catch (e) {
        return (
          <div className="text-sm text-gray-900 font-medium">
            {String(value)}
          </div>
        );
      }
    }
    
    // Handle long text
    if ((field.type === 'text' || field.type === 'long_answer') && typeof value === 'string') {
      if (value.length > 100) {
        return (
          <div className="space-y-2">
            <p className="text-sm text-gray-900 leading-relaxed">
              {value.substring(0, 100)}...
            </p>
            <div className="text-xs text-gray-500">
              {value.length} characters
            </div>
          </div>
        );
      }
      return (
        <p className="text-sm text-gray-900 leading-relaxed">
          {value}
        </p>
      );
    }
    
    // Handle numbers
    if (field.type === 'number' && typeof value === 'number') {
      return (
        <div className="inline-flex items-center gap-2 bg-orange-50 border border-orange-200 rounded-lg px-3 py-2">
          <div className="text-lg font-bold text-orange-900">
            {value}
          </div>
          <div className="text-xs text-orange-600">
            Number
          </div>
        </div>
      );
    }
    
    // Handle URLs
    if ((field.type === 'link' || field.type === 'url') && typeof value === 'string') {
      return (
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
          <a 
            href={value} 
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline text-sm font-medium break-all"
            title={value}
          >
            {value.length > 50 ? value.substring(0, 50) + '...' : value}
          </a>
          <div className="text-xs text-blue-600 mt-1">URL</div>
        </div>
      );
    }
    
    // Default case
    return (
      <div className="text-sm text-gray-900 font-medium">
        {String(value)}
      </div>
    );
  };

  const renderSubmissionValueLinear = (value: any, field: FormField) => {
    if (value === undefined || value === null) {
      return (
        <span className="text-gray-400 text-sm">—</span>
      )
    }

    // Special rendering for AI fields - Linear style
    if (field.type === 'ai' || field.is_ai_field) {
      return (
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-purple-500 rounded-sm flex items-center justify-center flex-shrink0">
            <span className="text-white text-[10px] font-bold">AI</span>
          </div>
          <span className="text-sm text-gray-900 font-medium truncate" title={String(value)}>
            {String(value)}
          </span>
        </div>
      );
    }
    
    // Handle objects (like files)
    if (typeof value === 'object' && value !== null) {
      if (field.type === 'file' && value.fileName) {
        return (
          <div className="flex items-center gap-2 min-w-0">
            <FileText className="h-4 w-4 text-gray-400 flex-shrink-0" />
            <span className="text-sm text-gray-900 truncate" title={value.fileName}>
              {value.fileName}
            </span>
          </div>
        );
      }
      
      // Handle multi-select - Linear style
      if ((field.type === 'multi_select' || field.type === 'multiSelect') && Array.isArray(value)) {
        if (value.length === 0) return <span className="text-gray-400 text-sm">—</span>;
        
        return (
          <div className="flex items-center gap-1 min-w-0">
            <span className="text-sm text-gray-900 truncate">
              {value.slice(0, 2).join(', ')}
            </span>
            {value.length > 2 && (
              <span className="text-xs text-gray-500 flex-shrink-0">
                +{value.length - 2}
              </span>
            )}
          </div>
        );
      }
      
      // For checkbox data stored as object with boolean values
      if (field.type === 'checkbox' && !Array.isArray(value)) {
        const selected = Object.entries(value)
          .filter(([_, selected]) => selected === true)
          .map(([option]) => option);
        
        if (selected.length === 0) return <span className="text-gray-400 text-sm">—</span>;
        
        return (
          <div className="flex items-center gap-1 min-w-0">
            <span className="text-sm text-gray-900 truncate">
              {selected.slice(0, 2).join(', ')}
            </span>
            {selected.length > 2 && (
              <span className="text-xs text-gray-500 flex-shrink-0">
                +{selected.length - 2}
              </span>
            )}
          </div>
        );
      }
      
      // If it's some other object type, stringify it
      try {
        const str = JSON.stringify(value);
        return (
          <span className="text-sm text-gray-600 font-mono truncate" title={str}>
            {str.length > 30 ? str.substring(0, 30) + '...' : str}
          </span>
        );
      } catch (e) {
        return <span className="text-gray-400 text-sm">Complex data</span>;
      }
    }
    
    // Handle simple types
    if (field.type === 'checkbox') {
      return (
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-sm border flex items-center justify-center ${
            value 
              ? 'bg-blue-500 border-blue-500' 
              : 'border-gray-300'
          }`}>
            {value && <div className="w-1.5 h-1.5 bg-white rounded-sm"></div>}
          </div>
          <span className="text-sm text-gray-900">
            {value ? 'Yes' : 'No'}
          </span>
        </div>
      );
    }
    
    // Handle dates
    if (field.type === 'date' && value) {
      try {
        return (
          <span className="text-sm text-gray-900">
            <FormattedDate date={value} format="short" />
          </span>
        );
      } catch (e) {
        return (
          <span className="text-sm text-gray-900">
            {String(value)}
          </span>
        );
      }
    }
    
    // Handle numbers
    if (field.type === 'number' && typeof value === 'number') {
      return (
        <span className="text-sm font-medium text-gray-900">
          {value.toLocaleString()}
        </span>
      );
    }
    
    // Handle long text
    if ((field.type === 'text' || field.type === 'long_answer') && typeof value === 'string') {
      return (
        <span className="text-sm text-gray-900 truncate" title={value}>
          {value.length > 50 ? value.substring(0, 50) + '...' : value}
        </span>
      );
    }
    
    // Handle URLs
    if ((field.type === 'link' || field.type === 'url') && typeof value === 'string') {
      return (
        <a 
          href={value} 
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline text-sm truncate"
          title={value}
        >
          {value.length > 30 ? value.substring(0, 30) + '...' : value}
        </a>
      );
    }
    
    // Default case
    return (
      <span className="text-sm text-gray-900 truncate" title={String(value)}>
        {String(value)}
      </span>
    );
  };

  const copyLink = () => {
    const url = `${typeof window !== "undefined" ? window.location.origin : ""}/forms/${form?.id}`;
    navigator.clipboard.writeText(url);
    
    setCopying(true);
    setTimeout(() => {
      setCopying(false);
      setCopied(true);
      
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    }, 500);
  }

  const generateTestData = async () => {
    if (!form) return;

    try {
      setGeneratingTestData(true);
      toast({
        title: "Generating test data...",
        description: "Creating 50 fake form submissions",
      });

      const submissions = [];

      for (let i = 0; i < 50; i++) {
        const formData: Record<string, any> = {};

        // Generate fake data for each field
        form.fields.forEach((field: FormField) => {
          // Skip header fields and AI fields as they don't need user input
          if (['h1', 'h2', 'h3'].includes(field.type) || field.type === 'ai' || field.is_ai_field) {
            return;
          }

          switch (field.type) {
            case 'text':
            case 'shortText':
              formData[field.id] = faker.person.fullName();
              break;
            
            case 'long_answer':
            case 'longText':
              formData[field.id] = faker.lorem.paragraphs(2);
              break;
            
            case 'email':
              formData[field.id] = faker.internet.email();
              break;
            
            case 'phone':
              formData[field.id] = faker.phone.number();
              break;
            
            case 'number':
              formData[field.id] = faker.number.int({ min: 1, max: 100 });
              break;
            
            case 'date':
              // Generate dates within the last 30 days
              formData[field.id] = faker.date.recent({ days: 30 }).toISOString().split('T')[0];
              break;
            
            case 'checkbox':
              if (field.options && field.options.length > 0) {
                // Select 1-3 random options
                const numSelections = faker.number.int({ min: 1, max: Math.min(3, field.options.length) });
                formData[field.id] = faker.helpers.arrayElements(field.options, numSelections);
              } else {
                formData[field.id] = faker.datatype.boolean();
              }
              break;
            
            case 'multiple_choice':
            case 'radio':
            case 'dropdown':
            case 'select':
              if (field.options && field.options.length > 0) {
                formData[field.id] = faker.helpers.arrayElement(field.options);
              }
              break;
            
            case 'multi_select':
            case 'multiSelect':
              if (field.options && field.options.length > 0) {
                // Select 1-3 random options
                const numSelections = faker.number.int({ min: 1, max: Math.min(3, field.options.length) });
                formData[field.id] = faker.helpers.arrayElements(field.options, numSelections);
              }
              break;
            
            case 'file':
            case 'fileUpload':
              // Generate fake file data
              formData[field.id] = {
                fileName: faker.system.fileName(),
                fileType: 'application/pdf',
                fileSize: faker.number.int({ min: 1000, max: 5000000 }),
                content: `data:application/pdf;base64,${faker.string.alphanumeric(100)}`,
                mimeType: 'application/pdf',
                extension: 'pdf'
              };
              break;
            
            case 'link':
            case 'url':
              formData[field.id] = faker.internet.url();
              break;
            
            default:
              formData[field.id] = faker.lorem.words(3);
          }
        });

        submissions.push(formData);
      }

      // Submit all the test data in smaller batches to avoid overwhelming the server
      const batchSize = 10;
      for (let i = 0; i < submissions.length; i += batchSize) {
        const batch = submissions.slice(i, i + batchSize);
        
        const promises = batch.map(async (submissionData) => {
          const response = await fetch(`/api/forms/${formId}/responses`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(submissionData),
          });

          if (!response.ok) {
            throw new Error(`Failed to submit test data: ${response.statusText}`);
          }

          return response.json();
        });

        await Promise.all(promises);
        
        // Update progress
        toast({
          title: "Progress...",
          description: `Generated ${Math.min(i + batchSize, submissions.length)} of ${submissions.length} submissions`,
        });
      }

      // Refresh the submissions list
      const responsesResponse = await fetch(`/api/forms/${formId}/responses`);
      if (responsesResponse.ok) {
        const responsesData = await responsesResponse.json();
        setSubmissions(responsesData);
      }

      toast({
        title: "Test data generated!",
        description: "Successfully created 50 fake form submissions",
      });

    } catch (error) {
      console.error('Error generating test data:', error);
      toast({
        title: "Error",
        description: "Failed to generate test data. Please try again.",
        variant: "destructive",
      });
    } finally {
      setGeneratingTestData(false);
    }
  }

  if (isLoading || !form) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  console.log('form.fields:', form?.fields);

  const renderedFields = form.fields.filter((field: FormField) => !['h1', 'h2', 'h3'].includes(field.type));
  console.log('Table column header fields:', renderedFields);

  return (
    <>
      {form && (
        <DashboardHeader
          workspaceId={form.workspaceId}
          workspaceName={form.workspace?.name || "My Workspace"}
          formId={form.id}
          formName={form.title}
          breadcrumbs={[
            { label: form.workspace?.name || "My Workspace", href: `/dashboard/workspace/${form.workspaceId || ''}` },
            { label: form.title, href: `/dashboard/forms/${form.id}` }
          ]}
        />
      )}
      
      {form && (
        <div className="container py-3 flex justify-end">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={handleShareForm}
              className="border-gray-200/60"
              size="sm"
            >
              <Share className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button 
              size="sm"
              onClick={handleEditForm}
              className="text-white"
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit Form
            </Button>
          </div>
        </div>
      )}
      
      <div className="container py-6">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold">{form.title}</h1>
          
          <div className="flex items-center gap-2">
            <Button onClick={handleShareForm} variant="outline">
              <Share className="mr-2 h-4 w-4" />
              Share
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <MoreHorizontal className="h-5 w-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleEditForm}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit form
                </DropdownMenuItem>

                <DropdownMenuItem onClick={() => router.push(`/dashboard/forms/${formId}/settings`)}>
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>

                <DropdownMenuItem onClick={generateTestData} disabled={generatingTestData}>
                  <TestTube className="mr-2 h-4 w-4" />
                  Generate Test Data
                </DropdownMenuItem>

                <DropdownMenuItem onClick={handleDeleteForm} className="text-destructive">
                  <Trash className="mr-2 h-4 w-4" />
                  Delete form
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        
        <Tabs defaultValue="summary" className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="summary" className="flex items-center gap-1">
              <BarChart2 className="h-4 w-4" /> Dashboard
            </TabsTrigger>
            <TabsTrigger value="submissions" className="flex items-center gap-1">
              <Inbox className="h-4 w-4" /> Submissions
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="summary" className="space-y-6">
            {/* Grid container */}
            <div className="grid gap-6 lg:grid-cols-[1fr_250px]">
              {/* Chat */}
              <div className="flex flex-col rounded-xl bg-background shadow-sm min-h-[320px] h-full">
                <div className="px-5 py-3 border-b text-sm font-medium text-muted-foreground">Chat with your data</div>
                <ChatThreadManager formId={formId} className="flex-1" />
              </div>
              
              {/* Stats */}
              <div>
                <h2 className="text-sm font-medium text-muted-foreground mb-3">FORM SNAPSHOT</h2>
                <div className="space-y-2">
                  <SummaryCard label="Submissions" value={submissions.length} />
                  <SummaryCard label="Fields" value={form.fields.length} />
                  <SummaryCard label="Status" value={form.published ? 'Published' : 'Draft'} />
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="submissions" className="space-y-8">
            {/* Header Section - Linear Style */}
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <h2 className="text-2xl font-semibold tracking-tight text-gray-900">Submissions</h2>
                <p className="text-sm text-gray-600">
                  {submissions.length} {submissions.length === 1 ? 'response' : 'responses'}
                </p>
              </div>
              {submissions.length > 0 && (
                <div className="flex items-center gap-3">
                  <Button variant="ghost" size="sm" className="h-8 px-3 text-gray-600 hover:text-gray-900">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                  <Button variant="ghost" size="sm" className="h-8 px-3 text-gray-600 hover:text-gray-900">
                    <Settings className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                </div>
              )}
            </div>

            {submissions.length > 0 ? (
              <div className="space-y-0">
                {/* Table Header - Notion Style */}
                <div className="grid grid-cols-[auto_1fr_auto] gap-6 px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100">
                  <div className="w-12"></div>
                  <div className="grid gap-6" style={{ gridTemplateColumns: `repeat(${renderedFields.length}, minmax(200px, 1fr))` }}>
                    {renderedFields.map((field: FormField) => (
                      <div key={field.id} className="flex items-center gap-2 min-w-0">
                        {(field.type === 'ai' || field.is_ai_field) && (
                          <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-purple-500 rounded-sm flex items-center justify-center flex-shrink0">
                            <span className="text-white text-[10px] font-bold">AI</span>
                          </div>
                        )}
                        <span className={`truncate ${
                          field.type === 'ai' || field.is_ai_field ? 'text-purple-700' : 'text-gray-500'
                        }`}>
                          {field.label}
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className="w-16 text-right">Actions</div>
                </div>

                {/* Table Body - Linear Style */}
                <div className="divide-y divide-gray-50">
                  {submissions.map((submission: FormSubmission, index: number) => (
                    <div 
                      key={submission.id}
                      className="group grid grid-cols-[auto_1fr_auto] gap-6 px-4 py-4 hover:bg-gray-50/30 transition-colors duration-150 cursor-pointer border-l-2 border-transparent hover:border-l-blue-500"
                      onClick={() => router.push(`/dashboard/forms/${formId}/responses/${submission.id}`)}
                    >
                      {/* Row Number */}
                      <div className="w-12 flex items-center">
                        <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-xs font-medium text-gray-600 group-hover:bg-blue-100 group-hover:text-blue-700 transition-colors">
                          {index + 1}
                        </div>
                      </div>

                      {/* Field Values */}
                      <div className="grid gap-6 min-w-0" style={{ gridTemplateColumns: `repeat(${renderedFields.length}, minmax(200px, 1fr))` }}>
                        {renderedFields.map((field: FormField) => (
                          <div key={field.id} className="min-w-0 flex items-center">
                            {renderSubmissionValueLinear(submission.data[field.id], field)}
                          </div>
                        ))}
                      </div>

                      {/* Actions */}
                      <div className="w-16 flex items-center justify-end">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 transition-opacity duration-150 hover:bg-gray-100"
                          onClick={(e: React.MouseEvent) => {
                            e.stopPropagation();
                            router.push(`/dashboard/forms/${formId}/responses/${submission.id}`);
                          }}
                        >
                          <Eye className="h-3.5 w-3.5 text-gray-500" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Footer - Minimal */}
                {submissions.length > 10 && (
                  <div className="flex items-center justify-center py-6 border-t border-gray-50">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      className="h-8 px-3 text-gray-600 hover:text-gray-900"
                      onClick={() => router.push(`/dashboard/forms/${formId}/responses`)}
                    >
                      View all {submissions.length} responses
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              /* Empty State - Linear Style */
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mb-4">
                  <FileText className="h-6 w-6 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No responses yet</h3>
                <p className="text-gray-500 mb-6 max-w-sm">
                  Share your form to start collecting responses from your audience.
                </p>
                <div className="flex items-center gap-3">
                  <Button 
                    variant="outline"
                    size="sm"
                    onClick={handleShareForm}
                    className="h-8 px-3"
                  >
                    <Share className="h-4 w-4 mr-2" />
                    Share form
                  </Button>
                  <Button 
                    variant="ghost"
                    size="sm"
                    onClick={() => router.push(`/forms/${formId}`)}
                    className="h-8 px-3"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Preview
                  </Button>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
      
      <Dialog open={shareDialogOpen} onOpenChange={setShareDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Share your form</DialogTitle>
            <DialogDescription>
              {form?.published ? (
                "Your form is published and ready to be shared with others."
              ) : (
                <span className="text-red-500 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Your form is not published. Publish it first to share.
                </span>
              )}
            </DialogDescription>
          </DialogHeader>
          {form?.published && (
            <>
              <div className="flex items-center space-x-2">
                <div className="grid flex-1 gap-2">
                  <Label htmlFor="link" className="sr-only">
                    Link
                  </Label>
                  <Input
                    id="link"
                    defaultValue={`${
                      typeof window !== "undefined"
                        ? window.location.origin
                        : ""
                    }/forms/${form.id}`}
                    readOnly
                  />
                </div>
                <Button
                  type="submit"
                  size="sm"
                  className="px-3"
                  onClick={copyLink}
                >
                  <span className="sr-only">Copy</span>
                  {copying ? (
                    <Skeleton className="h-4 w-4" />
                  ) : copied ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <Separator />
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <div className="flex flex-col space-y-0.5">
                    <Label htmlFor="require-login">Require sign in</Label>
                    <p className="text-xs text-muted-foreground">
                      Only allow logged in users to submit your form
                    </p>
                  </div>
                  <Switch disabled id="require-login" />
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex flex-col space-y-0.5">
                    <Label htmlFor="limit-responses">Limit responses</Label>
                    <p className="text-xs text-muted-foreground">
                      Set a maximum number of allowed responses
                    </p>
                  </div>
                  <Switch disabled id="limit-responses" />
                </div>
              </div>
              <DialogFooter className="flex flex-col-reverse sm:flex-row sm:justify-between sm:space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setShareDialogOpen(false)}
                >
                  Close
                </Button>
                <Button
                  type="button"
                  size="sm"
                  className="px-3"
                  variant="ghost"
                  onClick={() => toast({
                    title: "Coming soon",
                    description: "Additional sharing options will be available soon."
                  })}
                >
                  <Link
                    href={`/forms/${form.id}`}
                    target="_blank"
                    className="flex items-center"
                  >
                    <Eye className="h-4 w-4 mr-2" /> Preview Form
                  </Link>
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
} 