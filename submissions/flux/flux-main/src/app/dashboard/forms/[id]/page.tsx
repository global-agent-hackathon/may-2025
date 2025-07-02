/* eslint-disable @typescript-eslint/no-unused-vars */
"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { useRouter, useParams } from "next/navigation"
import { ArrowLeft, Settings, ChevronDown, Trash, Upload, Hash, Plus, Loader2, Check, Share, Pen, Eye, LayoutDashboard, Save, Sparkles, MessageSquare, Table, Edit3, BarChart3, Users, Calendar, History, Download } from "lucide-react"
import { useUser } from "@clerk/nextjs"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { FormShareModal } from "@/components/forms/form-share-modal"
import { DashboardHeader } from "@/components/layout/header/dashboard-header"
import { toast } from "@/hooks/use-toast"
import { Switch } from "@/components/ui/switch"
import { InteractiveHoverButton } from "@/components/magicui/interactive-hover-button"
import { AIFormBuilder } from "@/components/forms/ai-form-builder"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { ChatUI } from "@/components/chat/ChatUI"
import { useMediaQuery } from "@/lib/hooks/use-media-query"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { cn } from "@/lib/utils"
import { AnalyticsPage } from "@/components/analytics/AnalyticsPage"
import { trackFormInteraction } from "@/lib/memory"

// Import form helpers
import { prepareFieldsForAPI, prepareFieldsForUI } from "@/lib/form-helpers"

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
  type:
    | "text"
    | "number"
    | "email"
    | "phone"
    | "date"
    | "time"
    | "checkbox"
    | "multiple_choice"
    | "dropdown"
    | "file"
    | "long_answer"
    | "multi_select"
    | "link"
    | "h1"
    | "h2"
    | "h3"
    | "ai"
  label: string
  required: boolean
  placeholder?: string
  options?: string[] // For multiple choice, dropdown
  fileSize?: number // Max file size in MB (default 5MB)
  fileTypes?: string[] // Allowed file types
  // AI field properties
  is_ai_field?: boolean
  ai_metadata_prompt?: string
  ai_computed_value?: string
}

interface Submission {
  id: string
  formId: string
  data: Record<string, any>
  createdAt: Date
  updatedAt: Date
}

// Chat thread metadata
interface Thread {
  id: string
  title: string
  updatedAt: string
  formId: string
}

export default function FormEditorPage() {
  const router = useRouter()
  const params = useParams()
  const formId = params.id as string
  const { user, isLoaded: isUserLoaded } = useUser()

  const [form, setForm] = useState<FormData | null>(null)
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [showFieldMenu, setShowFieldMenu] = useState(false)
  const [showShareModal, setShowShareModal] = useState(false)
  const [activeField, setActiveField] = useState<string | null>(null)
  const [commandInput, setCommandInput] = useState("")
  const [showCommandMenu, setShowCommandMenu] = useState(false)
  const [bannerImage, setBannerImage] = useState<string | null>(null)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [isPublishing, setIsPublishing] = useState(false)
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== 'undefined') {
      const hash = window.location.hash.replace('#', '');
      return ['editor', 'data', 'analytics'].includes(hash) ? hash : 'editor';
    }
    return 'editor';
  });
  const [aiChatMessages, setAiChatMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([])
  const [aiInput, setAiInput] = useState("")
  const [isAiLoading, setIsAiLoading] = useState(false)
  const commandInputRef = useRef<HTMLInputElement>(null)
  const fieldMenuRef = useRef<HTMLDivElement>(null)
  const [showAIFormBuilder, setShowAIFormBuilder] = useState(false)
  const [isAIRefreshing, setIsAIRefreshing] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  const [aiPanelExpanded, setAiPanelExpanded] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Chat thread state
  const [threads, setThreads] = useState<Thread[]>([])
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null)
  const [loadingThreads, setLoadingThreads] = useState(true)
  const [creatingThread, setCreatingThread] = useState(false)
  const [showAiChat, setShowAiChat] = useState(false)
  const isDesktop = useMediaQuery("(min-width: 1024px)")

  const [selectedSubmission, setSelectedSubmission] = useState<Submission | null>(null)

  // Track tab changes for admin insights
  const handleTabChange = (newTab: string) => {
    setActiveTab(newTab);
    window.location.hash = `#${newTab}`;
    
    // Track data viewing for admin insights
    if (user?.id && newTab === 'data' && form) {
      trackFormInteraction(
        user.id,
        formId,
        "Data View",
        "viewed",
        {
          data_session: {
            view_timestamp: new Date().toISOString(),
            submission_count: submissions.length,
            has_ai_fields: form.fields.some(f => f.is_ai_field),
            ai_field_count: form.fields.filter(f => f.is_ai_field).length,
            total_fields: form.fields.length,
            user_role: "admin"
          }
        }
      ).catch(error => {
        console.warn("Failed to track data view:", error);
      });
    }
  };

  // Sync tab state with URL hash on mount and on hash change
  useEffect(() => {
    if (typeof window === 'undefined') return
    const updateTabFromHash = () => {
      const hash = window.location.hash.slice(1)
      if (['editor','data','analytics'].includes(hash)) {
        setActiveTab(hash)
      }
    }
    updateTabFromHash()
    window.addEventListener('hashchange', updateTabFromHash)
    return () => window.removeEventListener('hashchange', updateTabFromHash)
  }, [])

  // Handle responsive layouts
  useEffect(() => {
    // Function to check if viewport is mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 640);
    };
    
    // Initial check
    checkMobile();
    
    // Add event listener for window resize
    window.addEventListener('resize', checkMobile);
    
    // Cleanup
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Fetch form data and submissions
  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      if (!formId || formId === "new") {
        if (isMounted) {
          setIsLoading(false);
          setForm(null);
          setIsAIRefreshing(false);
        }
        return;
      }

      if (!isAIRefreshing) {
        setIsLoading(true);
      }
      
      try {
        // Fetch form data
        const formResponse = await fetch(`/api/forms/${formId}`);
        if (!formResponse.ok) {
          throw new Error("Failed to fetch form data");
        }
        const formData = await formResponse.json();
        
        // Fetch submissions
        const submissionsResponse = await fetch(`/api/forms/${formId}/responses`);
        const submissionsData = submissionsResponse.ok ? await submissionsResponse.json() : [];
        
        if (isMounted) {
          if (formData.fields && Array.isArray(formData.fields)) {
            formData.fields = prepareFieldsForUI(formData.fields);
          }
          setForm(formData);
          setSubmissions(submissionsData);
          if (formData.banner) setBannerImage(formData.banner);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        if (isMounted) {
          setForm(null);
          setSubmissions([]);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
          setIsAIRefreshing(false);
        }
      }
    };

    fetchData();
    return () => { isMounted = false; };
  }, [formId, refreshKey]);
  
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (fieldMenuRef.current && !fieldMenuRef.current.contains(event.target as Node)) {
        setShowFieldMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!form) return
    setForm({
      ...form,
      title: e.target.value,
    })
  }
  
  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (!form) return
    setForm({
      ...form,
      description: e.target.value,
    })
  }

  const addField = (type: FormField["type"]) => {
    if (!form) return

    const newField: FormField = {
      id: `field_${Date.now()}`,
      type,
      label: type === "file" ? "Upload File" : type === "ai" ? "AI Computed Field" : "Question",
      required: type === "ai" ? false : true, // AI fields are not required user input
      placeholder: "",
    }

    if (type === "checkbox" || type === "multiple_choice") {
      newField.options = ["Option 1"]
    } else if (type === "dropdown" || type === "multi_select") {
      newField.options = ["Option 1"]
    } else if (type === "file") {
      newField.fileSize = 10
      newField.fileTypes = ["application/pdf"]
    } else if (type === "ai") {
      newField.is_ai_field = true
      newField.ai_metadata_prompt = "Looking at {field1_id} and their {field2_id}, provide a rating or analysis..."
      newField.ai_computed_value = ""
    }

    setForm({
      ...form,
      fields: [...form.fields, newField],
    })

    setShowFieldMenu(false)
    setCommandInput("")
    setShowCommandMenu(false)
  }

  const removeField = (fieldId: string) => {
    if (!form) return

    setForm({
      ...form,
      fields: form.fields.filter((field) => field.id !== fieldId),
    })
  }

  const updateField = (fieldId: string, updates: Partial<FormField>) => {
    if (!form) return

    setForm({
      ...form,
      fields: form.fields.map((field) => (field.id === fieldId ? { ...field, ...updates } : field)),
    })
  }

  const addOption = (fieldId: string, option = "New option") => {
    if (!form) return

    setForm({
      ...form,
      fields: form.fields.map((field) => {
        if (field.id === fieldId && field.options) {
          return {
            ...field,
            options: [...field.options, option],
          }
        }
        return field
      }),
    })
  }

  const updateOption = (fieldId: string, index: number, value: string) => {
    if (!form) return

    setForm({
      ...form,
      fields: form.fields.map((field) => {
        if (field.id === fieldId && field.options) {
          const newOptions = [...field.options]
          newOptions[index] = value
          return {
            ...field,
            options: newOptions,
          }
        }
        return field
      }),
    })
  }

  const removeOption = (fieldId: string, index: number) => {
    if (!form) return

    setForm({
      ...form,
      fields: form.fields.map((field) => {
        if (field.id === fieldId && field.options) {
          const newOptions = [...field.options]
          newOptions.splice(index, 1)
          return {
            ...field,
            options: newOptions,
          }
        }
        return field
      }),
    })
  }

  // AI Chat functionality
  const handleAiChat = async () => {
    if (!aiInput.trim() || !form) return;
    
    setIsAiLoading(true);
    const userMessage = aiInput;
    setAiInput("");
    
    // Add user message
    setAiChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    
    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          formData: form,
          submissions: submissions,
          context: 'form-analysis'
        }),
      });
      
      if (!response.ok) throw new Error('Failed to get AI response');
      
      const data = await response.json();
      setAiChatMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
    } catch (error) {
      console.error('AI chat error:', error);
      setAiChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setIsAiLoading(false);
    }
  };

  // Render submission value for table
  const renderSubmissionValue = (value: any, field: FormField, isModal: boolean = false) => {
    if (value === undefined || value === null || value === '') {
      return <span className="text-gray-400 text-sm">—</span>;
    }

    if (field.type === 'file' && typeof value === 'object') {
      if (isModal) {
        // In modal, show file with download button
        return (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-blue-600">{value.name || value.fileName || 'File'}</span>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={(e) => {
                e.stopPropagation();
                // Create download link
                if (value.content) {
                  const link = document.createElement('a');
                  link.href = `data:${value.fileType || 'application/octet-stream'};base64,${value.content}`;
                  link.download = value.name || value.fileName || 'file';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                } else if (value.url) {
                  // If there's a URL instead of base64 content
                  window.open(value.url, '_blank');
                }
              }}
              className="h-7 px-2 text-xs"
            >
              <Download className="h-3 w-3 mr-1" />
              Download
            </Button>
          </div>
        );
      } else {
        // In table, show file indicator with download button
        return (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-blue-600 truncate max-w-[80px]" title={value.name || value.fileName || 'File'}>
              {value.name || value.fileName || 'File'}
            </span>
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                // Create download link
                if (value.content) {
                  const link = document.createElement('a');
                  link.href = `data:${value.fileType || 'application/octet-stream'};base64,${value.content}`;
                  link.download = value.name || value.fileName || 'file';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                } else if (value.url) {
                  // If there's a URL instead of base64 content
                  window.open(value.url, '_blank');
                }
              }}
              className="h-6 w-6 p-0 hover:bg-gray-100"
            >
              <Download className="h-3 w-3 text-gray-500" />
            </Button>
          </div>
        );
      }
    }

    if (field.type === 'checkbox' && Array.isArray(value)) {
      return (
        <div className="flex flex-wrap gap-1">
          {value.slice(0, isModal ? value.length : 2).map((item, idx) => (
            <Badge key={idx} variant="outline" className="text-xs">
              {item}
            </Badge>
          ))}
          {!isModal && value.length > 2 && (
            <Badge variant="outline" className="text-xs">
              +{value.length - 2}
            </Badge>
          )}
        </div>
      );
    }

    if (field.type === 'date') {
      return (
        <span className="text-sm text-gray-600">
          {new Date(value).toLocaleDateString()}
        </span>
      );
    }

    // Handle long text differently in table vs modal
    if (typeof value === 'string') {
      if (isModal) {
        // In modal, show full text with line breaks preserved
        return (
          <div className="whitespace-pre-wrap break-words text-sm text-gray-900 max-w-full">
            {value}
          </div>
        );
      } else if (value.length > 50) {
        // In table, truncate with ellipsis
        return (
          <span className="text-sm text-gray-600" title={value}>
            {value.substring(0, 50)}...
          </span>
        );
      }
    }

    return <span className="text-sm text-gray-900">{String(value)}</span>;
  };

  // Save form function (keeping existing logic)
  const saveForm = async () => {
    if (!form) return;

    setIsSaving(true);
    setSaveSuccess(false);

    try {
      const { 
        title, 
        description, 
        fields, 
        published, 
        workspaceId, 
        banner 
      } = form;

      if (!title) {
        throw new Error("Form title is required");
      }

      const mappedFields = prepareFieldsForAPI(fields);

      const payload = {
        title,
        description: description || "",
        published: published !== undefined ? published : false,
        workspaceId: workspaceId || null,
        banner,
        fields: mappedFields,
      };

      const response = await fetch(`/api/forms/${formId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let errorMessage = `Server returned ${response.status} ${response.statusText}`;
        
        try {
          const errorData = await response.json();
          if (errorData.error) {
            errorMessage = errorData.error;
          }
        } catch (parseError) {
          console.error("Could not parse error response:", parseError);
        }
        
        throw new Error(errorMessage);
      }

      const updatedForm = await response.json();
      setForm(updatedForm);

      // Track form editing memory for admin optimization insights
      if (user?.id) {
        try {
          const formAnalytics = {
            field_count: fields.length,
            field_types: fields.map(f => f.type),
            has_ai_fields: fields.some(f => f.is_ai_field),
            ai_field_count: fields.filter(f => f.is_ai_field).length,
            required_field_count: fields.filter(f => f.required).length,
            has_description: !!description,
            has_banner: !!banner,
            workspace_id: workspaceId,
            is_published: published
          };

          await trackFormInteraction(
            user.id,
            formId,
            title,
            "edited",
            {
              form_analytics: formAnalytics,
              edit_session_timestamp: new Date().toISOString(),
              form_complexity_score: fields.length + (fields.filter(f => f.is_ai_field).length * 2)
            }
          );
        } catch (memoryError) {
          console.warn("Failed to track form editing memory:", memoryError);
        }
      }

      toast({
        title: "Form saved",
        description: "Your form has been saved successfully",
        duration: 2000,
      });

      setSaveSuccess(true);
      setTimeout(() => {
        setSaveSuccess(false);
      }, 2000);
    } catch (error) {
      console.error("Error saving form:", error);
      
      toast({
        title: "Failed to save form",
        description: error instanceof Error ? error.message : "An unknown error occurred",
        variant: "destructive",
        duration: 3000,
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublishChange = async (published: boolean) => {
    if (!form) return;

    setIsPublishing(true);

    try {
      const { 
        title, 
        description, 
        fields, 
        workspaceId, 
        banner 
      } = form;

      if (!title) {
        throw new Error("Form title is required");
      }

      const mappedFields = prepareFieldsForAPI(fields);

      const payload = {
        title,
        description: description || "",
        published,
        workspaceId: workspaceId || null,
        banner,
        fields: mappedFields,
      };

      const response = await fetch(`/api/forms/${formId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to update form");
      }

      const updatedForm = await response.json();
      setForm(updatedForm);

      toast({
        title: published ? "Form published" : "Form unpublished",
        description: published 
          ? "Your form is now live and accepting responses" 
          : "Your form is now in draft mode",
        duration: 2000,
      });
    } catch (error) {
      console.error("Error updating form:", error);
      toast({
        title: "Failed to update form",
        description: error instanceof Error ? error.message : "An unknown error occurred",
        variant: "destructive",
        duration: 3000,
      });
    } finally {
      setIsPublishing(false);
    }
  };

  const getUserId = () => {
    return user?.id || "";
  };

  const handleShareForm = () => {
    setShowShareModal(true);
  };

  const handleCommandInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setCommandInput(value);
    
    if (value.startsWith("/")) {
      setShowCommandMenu(true);
    } else {
      setShowCommandMenu(false);
    }
  };

  const handleCommandSelect = (type: FormField["type"]) => {
    addField(type);
  };

  const handleBannerUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const result = event.target?.result as string;
        setBannerImage(result);
        if (form) {
          setForm({ ...form, banner: result });
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleViewDashboard = () => {
    if (form) {
      router.push(`/dashboard/forms/${form.id}`);
    }
  };

  const handleExportCSV = () => {
    if (!submissions.length || !form) return;
    
    // Get fields to include (excluding headers)
    const fieldsToInclude = form.fields.filter(field => !['h1', 'h2', 'h3'].includes(field.type));
    
    // Create CSV header row
    const headers = ['#', ...fieldsToInclude.map(field => field.label), 'Submitted'];
    
    // Create CSV content rows
    const rows = submissions.map((submission, index) => {
      const rowData = [
        index + 1, // Row number
        ...fieldsToInclude.map(field => {
          const value = submission.data[field.id];
          
          // Handle different data types
          if (value === undefined || value === null || value === '') {
            return '';
          }
          
          if (field.type === 'file' && typeof value === 'object') {
            return value.name || 'File';
          }
          
          if (Array.isArray(value)) {
            return value.join(', ');
          }
          
          if (field.type === 'date' && value) {
            return new Date(value).toLocaleDateString();
          }
          
          return String(value);
        }),
        new Date(submission.createdAt).toLocaleDateString() // Submission date
      ];
      
      return rowData;
    });
    
    // Combine headers and rows
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => {
        // Escape commas and quotes
        const cellStr = String(cell);
        if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
          return `"${cellStr.replace(/"/g, '""')}"`;
        }
        return cellStr;
      }).join(','))
    ].join('\n');
    
    // Create and trigger download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${form.title.replace(/\s+/g, '_')}_submissions_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast({
      title: "CSV Export Started",
      description: `Exporting ${submissions.length} submissions`,
      duration: 3000,
    });
  };

  const handleAIEditInitiated = () => {
    setIsAIRefreshing(true);
    setRefreshKey(prevKey => prevKey + 1);
  };

  const handleEditWithAI = () => {
    if (!form) return;
    setShowAIFormBuilder(true);
  };

  // Fetch threads for this form
  useEffect(() => {
    if (!formId) return;

    const fetchThreads = async () => {
      setLoadingThreads(true);
      try {
        const res = await fetch(`/api/chat?formId=${formId}`);
        if (res.ok) {
          const data = await res.json();
          setThreads(data);
          if (data.length && !selectedThreadId) {
            setSelectedThreadId(data[0].id);
          }
        }
      } catch (err) {
        console.error("Failed to load chat threads", err);
      } finally {
        setLoadingThreads(false);
      }
    };

    fetchThreads();
  }, [formId]);

  const createNewThread = async () => {
    if (!formId) return;
    setCreatingThread(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ formId, title: "New Chat" }),
      });
      if (!res.ok) throw new Error(await res.text());
      const newThread = await res.json();
      setThreads(prev => [newThread, ...prev]);
      setSelectedThreadId(newThread.id);
    } catch (err: any) {
      console.error(err);
      toast({ title: "Error", description: err?.message || "Unable to create chat", variant: "destructive" });
    } finally {
      setCreatingThread(false);
    }
  };

  const updateThreadInList = (updated: any) => {
    if (!updated?.id) return; // Guard against undefined or missing id
    setThreads(prev => prev.map(t => (t?.id === updated.id ? { ...t, title: updated.title, updatedAt: updated.updatedAt } : t)));
  };

  // Add this new function to handle submission click
  const handleSubmissionClick = (submission: Submission) => {
    setSelectedSubmission(submission);
  };

  // Loading states
  if (isLoading && !isAIRefreshing && formId !== "new") {
    return (
      <div className="min-h-screen bg-gray-50/30">
        {/* Header Skeleton */}
        <div className="bg-white border-b border-gray-200/60">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-8 w-16 bg-gray-100 rounded-md animate-pulse"></div>
                <div className="h-6 w-px bg-gray-200"></div>
                <div>
                  <div className="h-6 w-48 bg-gray-100 rounded animate-pulse mb-1"></div>
                  <div className="h-4 w-32 bg-gray-100 rounded animate-pulse"></div>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="h-9 w-24 bg-gray-100 rounded-lg animate-pulse"></div>
                <div className="h-8 w-20 bg-gray-100 rounded-md animate-pulse"></div>
                <div className="h-8 w-20 bg-gray-100 rounded-md animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Skeleton */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6">
          <div className="w-full">
            {/* Tabs Skeleton */}
            <div className="w-full bg-white border border-gray-200/60 rounded-lg p-1 mb-6">
              <div className="grid grid-cols-3 gap-1">
                <div className="h-9 bg-gray-100 rounded animate-pulse"></div>
                <div className="h-9 bg-gray-50 rounded animate-pulse"></div>
                <div className="h-9 bg-gray-50 rounded animate-pulse"></div>
              </div>
            </div>

            {/* Editor Content Skeleton */}
            <div className="bg-white rounded-lg border border-gray-200/60 p-4 sm:p-8">
              {/* Banner Area Skeleton */}
              <div className="mb-6 sm:mb-8 border-2 border-dashed border-gray-200 rounded-lg p-4 sm:p-8">
                <div className="h-6 w-32 bg-gray-100 rounded animate-pulse mx-auto mb-2"></div>
                <div className="h-4 w-48 bg-gray-100 rounded animate-pulse mx-auto"></div>
              </div>

              {/* Form Title Skeleton */}
              <div className="mb-6">
                <div className="h-8 w-64 bg-gray-100 rounded animate-pulse mb-2"></div>
                <div className="h-20 w-full bg-gray-100 rounded-lg animate-pulse"></div>
              </div>

              {/* Form Fields Skeleton */}
              <div className="space-y-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-4 border border-gray-200/60 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="h-5 w-32 bg-gray-100 rounded animate-pulse"></div>
                      <div className="h-8 w-20 bg-gray-100 rounded animate-pulse"></div>
                    </div>
                    <div className="h-10 w-full bg-gray-100 rounded-md animate-pulse mb-2"></div>
                    <div className="h-4 w-24 bg-gray-100 rounded animate-pulse"></div>
                  </div>
                ))}
              </div>

              {/* Add Field Button Skeleton */}
              <div className="mt-8 text-center">
                <div className="h-10 w-32 bg-gray-100 rounded-md animate-pulse mx-auto"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  if (isAIRefreshing) {
    return (
      <div className="min-h-screen bg-gray-50/30">
        {/* Header Skeleton */}
        <div className="bg-white border-b border-gray-200/60">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-8 w-16 bg-gray-100 rounded-md animate-pulse"></div>
                <div className="h-6 w-px bg-gray-200"></div>
                <div>
                  <div className="h-6 w-48 bg-gray-100 rounded animate-pulse mb-1"></div>
                  <div className="h-4 w-32 bg-gray-100 rounded animate-pulse"></div>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="h-9 w-24 bg-gray-100 rounded-lg animate-pulse"></div>
                <div className="h-8 w-20 bg-gray-100 rounded-md animate-pulse"></div>
                <div className="h-8 w-20 bg-gray-100 rounded-md animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Processing Indicator */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          <div className="bg-white rounded-lg border border-purple-200/60 p-6 mb-6">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="relative">
                <Sparkles className="h-6 w-6 text-purple-600 animate-pulse" />
                <div className="absolute -inset-1 rounded-full bg-purple-100 animate-ping opacity-75"></div>
              </div>
              <span className="text-lg font-medium text-purple-900">AI is editing your form</span>
            </div>
            <p className="text-center text-gray-600 mb-4">Applying AI suggestions and refreshing the form structure...</p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-purple-600 h-2 rounded-full animate-pulse" style={{ width: '65%' }}></div>
            </div>
          </div>

          {/* Content Skeleton with AI Glow */}
          <div className="w-full">
            <div className="w-full bg-white border border-gray-200/60 rounded-lg p-1 mb-6">
              <div className="grid grid-cols-3 gap-1">
                <div className="h-9 bg-purple-50 rounded animate-pulse border border-purple-200"></div>
                <div className="h-9 bg-gray-50 rounded animate-pulse"></div>
                <div className="h-9 bg-gray-50 rounded animate-pulse"></div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200/60 p-4 sm:p-8">
              <div className="space-y-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-4 border border-purple-200/40 rounded-lg bg-purple-50/20">
                    <div className="flex items-center justify-between mb-3">
                      <div className="h-5 w-32 bg-purple-100 rounded animate-pulse"></div>
                      <div className="h-8 w-20 bg-purple-100 rounded animate-pulse"></div>
                    </div>
                    <div className="h-10 w-full bg-purple-100 rounded-md animate-pulse mb-2"></div>
                    <div className="h-4 w-24 bg-purple-100 rounded animate-pulse"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!form && formId !== "new") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-150px)] p-4">
        <p className="text-lg text-destructive">Form not found or failed to load.</p>
        <Button onClick={() => router.push('/dashboard')} className="mt-4">Go to Dashboard</Button>
      </div>
    );
  }
  
  if (formId === "new" && !form) {
    return (
      <div className="max-w-4xl mx-auto p-4 space-y-8 text-center">
        <h1 className="text-3xl font-bold mt-8">Create a New Form</h1>
        <p className="text-muted-foreground">Start by adding fields manually or let AI build it for you.</p>
        <div className="mt-6">
            <Button size="lg" onClick={() => {/* Placeholder for manual add field UI */ alert("Manual field addition UI not implemented yet.");}} className="mr-4">
                Add Field Manually
            </Button>
            <Button variant="outline" size="lg" onClick={() => setShowAIFormBuilder(true)}>
                <Sparkles className="h-5 w-5 mr-2" /> Create with AI
            </Button>
        </div>
        {showAIFormBuilder && (
            <AIFormBuilder
                isOpen={showAIFormBuilder}
                onOpenChange={setShowAIFormBuilder}
                existingForm={null} 
                workspaceId={params.workspaceId as string | undefined}
            />
        )}
      </div>
    );
  }

  if (!form) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-150px)] p-4">
            <p className="text-lg text-destructive">An unexpected error occurred. Form data is unavailable.</p>
            <Button onClick={() => router.push('/dashboard')} className="mt-4">Go to Dashboard</Button>
        </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50/30">
      {/* Header */}
      <div className="bg-white border-b border-gray-200/60">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => router.back()}
                className="text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div className="h-6 w-px bg-gray-200"></div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{form.title}</h1>
                <p className="text-sm text-gray-500">{form.workspace?.name || "My Workspace"}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-200/60">
                <Switch 
                  checked={form.published || false}
                  onCheckedChange={(checked) => handlePublishChange(checked)}
                  disabled={isPublishing}
                />
                <span className="text-sm font-medium text-gray-700">
                  {isPublishing ? "Updating..." : form.published ? "Published" : "Draft"}
                </span>
              </div>

              {form.published && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={handleShareForm}
                  className="bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100 hover:text-purple-800"
                >
                  <Share className="h-4 w-4 mr-2" />
                  Share
                </Button>
              )}

              <Button 
                onClick={saveForm}
                disabled={isSaving}
                className="bg-gray-900 hover:bg-gray-800 text-white"
                size="sm"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : saveSuccess ? (
                  <>
                    <Check className="h-4 w-4 mr-2" />
                    Saved
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6">
        {/* Responsive layout - stack on mobile, side-by-side on larger screens */}
        <div className="flex flex-col gap-4 sm:gap-6 h-auto">
          {/* Main Content Area with Tabs - full width on mobile, flex grow on desktop */}
          <div className="w-full">
            <Tabs value={activeTab} onValueChange={(val) => { setActiveTab(val); handleTabChange(val); }} className="w-full h-full flex flex-col">
              <TabsList className="grid w-full grid-cols-3 bg-white border border-gray-200/60 p-1">
                <TabsTrigger 
                  value="editor" 
                  className="flex items-center gap-1 sm:gap-2 data-[state=active]:bg-gray-100 data-[state=active]:text-gray-900 text-xs sm:text-sm"
                >
                  <Edit3 className="h-3 w-3 sm:h-4 sm:w-4" />
                  <span>Editor</span>
                </TabsTrigger>
                <TabsTrigger 
                  value="data" 
                  className="flex items-center gap-1 sm:gap-2 data-[state=active]:bg-gray-100 data-[state=active]:text-gray-900 text-xs sm:text-sm"
                >
                  <Table className="h-3 w-3 sm:h-4 sm:w-4" />
                  <span>Data</span>
                  {submissions.length > 0 && (
                    <Badge variant="secondary" className="ml-1 text-xs hidden sm:inline-flex">
                      {submissions.length}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger 
                  value="analytics" 
                  className="flex items-center gap-1 sm:gap-2 data-[state=active]:bg-gray-100 data-[state=active]:text-gray-900 text-xs sm:text-sm"
                >
                  <BarChart3 className="h-3 w-3 sm:h-4 sm:w-4" />
                  <span>Analytics</span>
                </TabsTrigger>
              </TabsList>

              <div className="flex-1 mt-4 sm:mt-6 overflow-hidden">
                {/* Editor Tab */}
                <TabsContent value="editor" id="editor" className="h-full overflow-auto">
                  <div className="bg-white rounded-lg border border-gray-200/60 p-4 sm:p-8">
                    {/* Banner Section */}
                    {bannerImage ? (
                      <div className="mb-6 sm:mb-8 relative">
                        <img src={bannerImage} alt="Form banner" className="w-full h-32 sm:h-48 object-cover rounded-lg" />
                        <button 
                          className="absolute top-2 right-2 sm:top-3 sm:right-3 bg-white/90 backdrop-blur-sm p-1.5 sm:p-2 rounded-lg shadow-sm hover:bg-white transition-colors"
                          onClick={() => setBannerImage(null)}
                        >
                          <Trash className="h-3 w-3 sm:h-4 sm:w-4 text-gray-600" />
                        </button>
                      </div>
                    ) : (
                      <div className="mb-6 sm:mb-8 border-2 border-dashed border-gray-200 rounded-lg p-4 sm:p-8 text-center hover:border-gray-300 transition-colors">
                        <input
                          type="file"
                          id="banner-upload"
                          className="hidden"
                          accept="image/*"
                          onChange={handleBannerUpload}
                        />
                        <label htmlFor="banner-upload" className="cursor-pointer">
                          <div className="flex flex-col items-center">
                            <Upload className="h-6 w-6 sm:h-8 sm:w-8 text-gray-400 mb-2 sm:mb-3" />
                            <p className="text-xs sm:text-sm text-gray-500 font-medium">Add banner or logo</p>
                            <p className="text-xs text-gray-400 mt-1">Click to upload an image</p>
                          </div>
                        </label>
                      </div>
                    )}

                    {/* Form Title & Description */}
                    <div className="mb-8 sm:mb-12">
                      <Input
                        value={form.title}
                        onChange={handleTitleChange}
                        placeholder="Form title" 
                        className="w-full text-2xl sm:text-4xl font-bold border-none px-0 focus-visible:ring-0 focus-visible:ring-offset-0 mb-4 sm:mb-6 h-auto py-1 sm:py-2 text-gray-900 placeholder:text-gray-400"
                      />
                      <Textarea 
                        value={form.description || ''}
                        onChange={handleDescriptionChange}
                        placeholder="Add a description to help participants understand your form..."
                        className="w-full border-none resize-none px-0 focus-visible:ring-0 focus-visible:ring-offset-0 text-sm sm:text-lg text-gray-600 min-h-[40px] sm:min-h-[60px] placeholder:text-gray-400"
                      />
                    </div>

                    {/* AI Edit Button */}
                    <div className="flex justify-end mb-6">
                      <Button onClick={handleEditWithAI} variant="outline" size="sm">
                        <Sparkles className="h-4 w-4 mr-2" />
                        Edit with AI
                      </Button>
                    </div>

                    {/* Form Fields */}
                    <div className="space-y-4 sm:space-y-6">
                      {form.fields.map((field, index) => (
                        <div
                          key={field.id}
                          className={`group border rounded-lg p-6 transition-all duration-200 ${
                            activeField === field.id 
                              ? "border-blue-300 shadow-sm bg-blue-50/30" 
                              : "border-gray-200 hover:border-gray-300 hover:shadow-sm"
                          }`}
                          onClick={() => setActiveField(field.id)}
                        >
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <Input
                                  value={field.label}
                                  onChange={(e) => updateField(field.id, { label: e.target.value })}
                                  placeholder="Question"
                                  className="text-lg font-medium border-none p-0 focus-visible:ring-0 focus-visible:ring-offset-0 text-gray-900"
                                />
                                <span className="ml-2 text-xs text-gray-400 select-all">ID: {field.id}</span>
                                {field.is_ai_field && (
                                  <Badge className="bg-purple-100 text-purple-700 border-purple-200">
                                    <Sparkles className="h-3 w-3 mr-1" />
                                    AI
                                  </Badge>
                                )}
                              </div>
                              
                              {field.type !== "ai" && (
                                <Input
                                  value={field.placeholder || ''}
                                  onChange={(e) => updateField(field.id, { placeholder: e.target.value })}
                                  placeholder="Add placeholder text..."
                                  className="text-sm text-gray-500 border-none p-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                                />
                              )}
                            </div>
                            
                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  removeField(field.id);
                                }}
                                className="text-gray-400 hover:text-red-600 hover:bg-red-50"
                              >
                                <Trash className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>

                          {/* Field Options for multi-choice fields */}
                          {(field.type === "multiple_choice" || field.type === "dropdown" || field.type === "multi_select" || field.type === "checkbox") && (
                            <div className="space-y-2 ml-4">
                              {field.options?.map((option, optionIndex) => (
                                <div key={optionIndex} className="flex items-center gap-2">
                                  <div className="w-4 h-4 border border-gray-300 rounded-sm"></div>
                                  <Input
                                    value={option}
                                    onChange={(e) => updateOption(field.id, optionIndex, e.target.value)}
                                    className="flex-1 text-sm border-none p-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                                  />
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => removeOption(field.id, optionIndex)}
                                    className="text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                  >
                                    <Trash className="h-3 w-3" />
                                  </Button>
                                </div>
                              ))}
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => addOption(field.id)}
                                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 ml-6"
                              >
                                <Plus className="h-3 w-3 mr-1" />
                                Add option
                              </Button>
                            </div>
                          )}

                          {/* AI Field Configuration */}
                          {field.is_ai_field && (
                            <div className="mt-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
                              <label className="block text-sm font-medium text-purple-900 mb-2">
                                AI Prompt(these field won't be shown to users, only for Admins)
                              </label>
                              <Textarea
                                value={field.ai_metadata_prompt || ''}
                                onChange={(e) => updateField(field.id, { ai_metadata_prompt: e.target.value })}
                                placeholder="Describe what you want AI to analyze or compute based on other form fields..."
                                className="w-full text-sm border-purple-200 focus:border-purple-300 focus:ring-purple-200"
                                rows={3}
                              />
                            </div>
                          )}
                        </div>
                      ))}

                      {/* Add Field Button */}
                      <div className="relative" ref={fieldMenuRef}>
                        <Button
                          variant="outline"
                          onClick={() => setShowFieldMenu(!showFieldMenu)}
                          className="w-full border-dashed border-gray-300 hover:border-gray-400 hover:bg-gray-50 py-8 text-gray-600"
                        >
                          <Plus className="h-5 w-5 mr-2" />
                          Add field
                        </Button>

                        {showFieldMenu && (
                          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 p-2">
                            <div className="grid grid-cols-2 gap-1">
                              {[
                                { type: "text", label: "Text", icon: "T" },
                                { type: "email", label: "Email", icon: "@" },
                                { type: "number", label: "Number", icon: "#" },
                                { type: "phone", label: "Phone", icon: "📞" },
                                { type: "date", label: "Date", icon: "📅" },
                                { type: "link", label: "URL", icon: "🔗" },
                                { type: "multiple_choice", label: "Multiple Choice", icon: "◉" },
                                { type: "dropdown", label: "Dropdown", icon: "▼" },
                                { type: "checkbox", label: "Checkbox", icon: "☑" },
                                { type: "file", label: "File Upload", icon: "📎" },
                                { type: "long_answer", label: "Long Answer", icon: "📝" },
                                { type: "ai", label: "AI Field", icon: "✨" },
                              ].map((fieldType) => (
                                <Button
                                  key={fieldType.type}
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => addField(fieldType.type as FormField["type"])}
                                  className="justify-start text-left p-3 hover:bg-gray-50"
                                >
                                  <span className="mr-3 text-lg">{fieldType.icon}</span>
                                  {fieldType.label}
                                </Button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </TabsContent>

                {/* Data Tab */}
                <TabsContent value="data" id="data" className="h-full overflow-hidden">
                  <div className={`grid gap-6 h-[calc(100vh-250px)] ${showAiChat && isDesktop ? 'lg:grid-cols-[1fr_400px]' : 'lg:grid-cols-1'}`}>
                    {/* Data table */}
                    <div className="bg-white rounded-lg border border-gray-200/60 h-full flex flex-col overflow-hidden">
                      <div className="p-3 sm:p-6 border-b border-gray-200/60 flex-shrink-0">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0">
                          <div>
                            <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                              <h3 className="text-base sm:text-lg font-semibold text-gray-900">Submissions</h3>
                              <div className="flex items-center gap-2">
                                <Badge variant="secondary" className="text-xs">
                                  {submissions.length} {submissions.length === 1 ? 'response' : 'responses'}
                                </Badge>
                                {form.fields.filter(f => f.is_ai_field).length > 0 && (
                                  <Badge className="bg-purple-100 text-purple-700 border-purple-200 text-xs">
                                    <Sparkles className="h-3 w-3 mr-1" />
                                    {form.fields.filter(f => f.is_ai_field).length} AI {form.fields.filter(f => f.is_ai_field).length === 1 ? 'field' : 'fields'}
                                  </Badge>
                                )}
                              </div>
                            </div>
                            <p className="text-xs sm:text-sm text-gray-500 mt-1">
                              Track and analyze your form responses
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={() => setShowAiChat(!showAiChat)}
                              disabled={submissions.length === 0}
                              className={cn(
                                submissions.length === 0 
                                  ? "bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed" 
                                  : showAiChat 
                                    ? "bg-purple-50 border-purple-200 text-purple-700" 
                                    : ""
                              )}
                            >
                              <Sparkles className="h-4 w-4 mr-2" />
                              {submissions.length === 0 
                                ? "Need Submissions to Chat" 
                                : showAiChat 
                                  ? "Hide AI Chat" 
                                  : "Chat with AI"
                              }
                            </Button>
                            <Button variant="outline" size="sm" onClick={handleExportCSV}>
                              Export CSV
                            </Button>
                          </div>
                        </div>
                      </div>

                      <div className="flex-1 overflow-hidden">
                        {submissions.length > 0 ? (
                          <div className="h-full overflow-y-auto overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent hover:scrollbar-thumb-gray-400">
                            <table className="w-full min-w-[640px] sm:min-w-[800px]">
                              <thead className="bg-gray-50/50 sticky top-0 z-10">
                                <tr>
                                  <th className="px-3 py-2 sm:px-6 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-10 sm:w-16 whitespace-nowrap">
                                    #
                                  </th>
                                  {form.fields
                                    .filter(field => !['h1', 'h2', 'h3'].includes(field.type))
                                    .map((field) => (
                                      <th key={field.id} className="px-3 py-2 sm:px-6 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                                        <div className="flex items-center gap-2">
                                          <span className="truncate max-w-[80px] sm:max-w-[150px]" title={field.label}>
                                            {field.label}
                                          </span>
                                          {field.is_ai_field && (
                                            <Badge className="bg-purple-100 text-purple-700 border-purple-200 text-xs">
                                              AI
                                            </Badge>
                                          )}
                                        </div>
                                      </th>
                                    ))}
                                  <th className="px-3 py-2 sm:px-6 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20 sm:w-32 whitespace-nowrap">
                                    Submitted
                                  </th>
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-gray-200/60">
                                {submissions.map((submission, index) => (
                                  <tr 
                                    key={submission.id} 
                                    className="hover:bg-gray-50/50 transition-colors cursor-pointer" 
                                    onClick={() => handleSubmissionClick(submission)}
                                  >
                                    <td className="px-3 py-2 sm:px-6 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500 w-10 sm:w-16">
                                      {index + 1}
                                    </td>
                                    {form.fields
                                      .filter(field => !['h1', 'h2', 'h3'].includes(field.type))
                                      .map((field) => (
                                        <td key={field.id} className="px-3 py-2 sm:px-6 sm:py-4 whitespace-nowrap">
                                          <div className="max-w-[120px] sm:max-w-[200px] truncate text-xs sm:text-sm">
                                            {renderSubmissionValue(submission.data[field.id], field, false)}
                                          </div>
                                        </td>
                                      ))}
                                    <td className="px-3 py-2 sm:px-6 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500 w-20 sm:w-32">
                                      <div className="flex items-center gap-1 sm:gap-2">
                                        <Calendar className="h-3 w-3 sm:h-4 sm:w-4" />
                                        {new Date(submission.createdAt).toLocaleDateString()}
                                      </div>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <div className="h-full flex items-center justify-center">
                            <div className="text-center p-4">
                              <Users className="h-8 w-8 sm:h-12 sm:w-12 text-gray-300 mx-auto mb-3 sm:mb-4" />
                              <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-2">No submissions yet</h3>
                              <p className="text-xs sm:text-sm text-gray-500 mb-4 sm:mb-6">
                                Share your form to start collecting responses
                              </p>
                              <Button onClick={handleShareForm} size="sm" className="sm:px-4 sm:py-2 text-xs sm:text-sm bg-purple-600 hover:bg-purple-700 text-white font-medium">
                                <Share className="h-3 w-3 sm:h-4 sm:w-4 mr-2" />
                                Share Form
                              </Button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* AI Chat - sidebar on desktop */}
                    {showAiChat && isDesktop && (
                      <div className="bg-white rounded-lg border border-gray-200/60 h-full flex flex-col overflow-hidden">
                        {/* Header with thread dropdown */}
                        <div className="px-4 py-3 border-b border-gray-200/60 flex-shrink-0 bg-white">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                <Sparkles className="h-4 w-4 text-purple-600" />
                              </div>
                              <div>
                                <h3 className="text-sm font-medium text-gray-900">AI Assistant</h3>
                                <p className="text-xs text-gray-500">Analyze your form data</p>
                              </div>
                            </div>

                            <div className="flex items-center gap-2">
                              {/* New Chat button - only show when thread is selected */}
                              {selectedThreadId && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={createNewThread}
                                  disabled={creatingThread}
                                  className="h-8 w-8 hover:bg-purple-50 hover:text-purple-600"
                                  title="New Chat"
                                >
                                  <Plus className="h-4 w-4" />
                                </Button>
                              )}
                              
                              {/* Thread dropdown */}
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    className="h-8 w-8 hover:bg-purple-50 hover:text-purple-600"
                                  >
                                    <History className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-56">
                                  <div className="px-2 py-2 text-xs font-medium text-gray-500">Chat History</div>
                                  {loadingThreads ? (
                                    <div className="p-3 flex items-center justify-center">
                                      <Loader2 className="h-4 animate-spin text-purple-600" />
                                    </div>
                                  ) : threads.length === 0 ? (
                                    <DropdownMenuItem disabled className="text-sm text-gray-500">
                                      No previous chats
                                    </DropdownMenuItem>
                                  ) : (
                                    threads.map(thread => (
                                      <DropdownMenuItem
                                        key={thread.id}
                                        onClick={() => setSelectedThreadId(thread.id)}
                                        className={cn(
                                          "text-sm",
                                          selectedThreadId === thread.id && "bg-purple-50 text-purple-700"
                                        )}
                                      >
                                        {thread.title}
                                      </DropdownMenuItem>
                                    ))
                                  )}
                                  {/* Only show New Chat in dropdown when no thread is selected */}
                                  {!selectedThreadId && (
                                    <DropdownMenuItem 
                                      onClick={submissions.length > 0 ? createNewThread : undefined} 
                                      disabled={creatingThread || submissions.length === 0}
                                      className={cn(
                                        "text-sm border-t mt-1",
                                        submissions.length === 0 
                                          ? "text-gray-400 cursor-not-allowed" 
                                          : "text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                                      )}
                                    >
                                      <Plus className="h-3 w-3 mr-2" /> 
                                      {submissions.length === 0 ? "New Chat (Need Submissions)" : "New Chat"}
                                    </DropdownMenuItem>
                                  )}
                                </DropdownMenuContent>
                              </DropdownMenu>
                              
                              {/* Close button */}
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setShowAiChat(false)}
                                className="h-8 w-8 hover:bg-gray-100"
                              >
                                <ChevronDown className="h-4 w-4 rotate-90" />
                              </Button>
                            </div>
                          </div>
                        </div>

                        {/* Chat body */}
                        <div className="flex-1 overflow-hidden">
                          {selectedThreadId ? (
                            <ChatUI threadId={selectedThreadId} className="h-full" onThreadUpdate={updateThreadInList} />
                          ) : loadingThreads ? (
                            <div className="h-full flex items-center justify-center">
                              <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
                            </div>
                          ) : submissions.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center gap-4 text-center p-6">
                              <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
                                <MessageSquare className="h-6 w-6 text-gray-400" />
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">No Submissions Yet</p>
                                <p className="text-sm text-gray-500 mt-1 mb-4">You need form submissions before you can start chatting about your data</p>
                                <Button 
                                  size="sm" 
                                  disabled={true}
                                  className="bg-gray-200 text-gray-400 cursor-not-allowed"
                                >
                                  <MessageSquare className="h-4 w-4 mr-2" />
                                  Chat Disabled
                                </Button>
                              </div>
                            </div>
                          ) : (
                            <div className="h-full flex flex-col items-center justify-center gap-4 text-center p-6">
                              <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                                <MessageSquare className="h-6 w-6 text-purple-600" />
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">Start a New Chat</p>
                                <p className="text-sm text-gray-500 mt-1 mb-4">Ask questions about your form submissions</p>
                                <Button 
                                  onClick={createNewThread} 
                                  size="sm" 
                                  disabled={creatingThread}
                                  className="bg-purple-600 hover:bg-purple-700 text-white"
                                >
                                  {creatingThread ? (
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                  ) : (
                                    <Plus className="h-4 w-4 mr-2" />
                                  )}
                                  New Chat
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                  {/* Modal for mobile/tablet */}
                  <Dialog open={showAiChat && !isDesktop} onOpenChange={setShowAiChat}>
                    <DialogContent className="max-w-lg w-full p-0 overflow-hidden">
                      <div className="bg-white flex flex-col min-h-[500px] h-[80vh] rounded-lg">
                        <div className="px-4 py-3 border-b border-gray-200/60 flex-shrink-0">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                <Sparkles className="h-4 w-4 text-purple-600" />
                              </div>
                              <div>
                                <h3 className="text-sm font-medium text-gray-900">AI Assistant</h3>
                                <p className="text-xs text-gray-500">Analyze your form data</p>
                              </div>
                            </div>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setShowAiChat(false)}
                              className="h-8 w-8 hover:bg-gray-100"
                            >
                              <ChevronDown className="h-4 w-4 rotate-90" />
                            </Button>
                          </div>
                        </div>
                        <div className="flex-1 overflow-hidden">
                          {selectedThreadId ? (
                            <ChatUI threadId={selectedThreadId} className="h-full" onThreadUpdate={updateThreadInList} />
                          ) : loadingThreads ? (
                            <div className="h-full flex items-center justify-center">
                              <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
                            </div>
                          ) : submissions.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center gap-4 text-center p-6">
                              <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
                                <MessageSquare className="h-6 w-6 text-gray-400" />
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">No Submissions Yet</p>
                                <p className="text-sm text-gray-500 mt-1 mb-4">You need form submissions before you can start chatting about your data</p>
                                <Button 
                                  size="sm" 
                                  disabled={true}
                                  className="bg-gray-200 text-gray-400 cursor-not-allowed"
                                >
                                  <MessageSquare className="h-4 w-4 mr-2" />
                                  Chat Disabled
                                </Button>
                              </div>
                            </div>
                          ) : (
                            <div className="h-full flex flex-col items-center justify-center gap-4 text-center p-6">
                              <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                                <MessageSquare className="h-6 w-6 text-purple-600" />
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">Start a New Chat</p>
                                <p className="text-sm text-gray-500 mt-1 mb-4">Ask questions about your form submissions</p>
                                <Button 
                                  onClick={createNewThread} 
                                  size="sm" 
                                  disabled={creatingThread}
                                  className="bg-purple-600 hover:bg-purple-700 text-white"
                                >
                                  {creatingThread ? (
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                  ) : (
                                    <Plus className="h-4 w-4 mr-2" />
                                  )}
                                  New Chat
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                </TabsContent>

                {/* Analytics Tab */}
                <TabsContent value="analytics" id="analytics" className="h-full overflow-auto">
                  <AnalyticsPage formId={formId} submissionCount={submissions.length} />
                </TabsContent>
              </div>
            </Tabs>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showShareModal && (
        <FormShareModal
          isOpen={showShareModal}
          onOpenChange={setShowShareModal}
          formId={formId}
          isPublished={form.published || false}
          onPublishChange={handlePublishChange}
        />
      )}

      {showAIFormBuilder && (
        <AIFormBuilder
          isOpen={showAIFormBuilder}
          onOpenChange={setShowAIFormBuilder}
          existingForm={{
            id: form.id,
            title: form.title,
            description: form.description,
            schema: form.fields,
          }}
          workspaceId={form.workspaceId}
          onEditComplete={handleAIEditInitiated}
        />
      )}

      {/* Add Submission Modal */}
      <Dialog open={selectedSubmission !== null} onOpenChange={(open) => !open && setSelectedSubmission(null)}>
        <DialogContent className="max-w-4xl w-full max-h-[90vh] flex flex-col">
          <DialogHeader className="flex-shrink-0">
            <DialogTitle>Submission Details</DialogTitle>
          </DialogHeader>
          <div className="flex-1 overflow-y-auto py-4 space-y-4">
            {selectedSubmission && form.fields
              .filter(field => !['h1', 'h2', 'h3'].includes(field.type))
              .map((field) => (
                <div key={field.id} className="grid grid-cols-3 gap-4">
                  <div className="text-sm font-medium text-gray-500 flex-shrink-0">
                    {field.label}
                    {field.is_ai_field && (
                      <Badge className="ml-2 bg-purple-100 text-purple-700 border-purple-200">AI</Badge>
                    )}
                  </div>
                  <div className="col-span-2 text-sm text-gray-900 min-w-0">
                    {renderSubmissionValue(selectedSubmission.data[field.id], field, true)}
                  </div>
                </div>
              ))}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t">
              <div className="text-sm font-medium text-gray-500">Submitted</div>
              <div className="col-span-2 text-sm text-gray-900">
                {new Date(selectedSubmission?.createdAt || '').toLocaleString()}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}