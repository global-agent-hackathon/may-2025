"use client"

import * as React from "react"
import { useState, useEffect, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useData } from "@/contexts/DataContext"
import { DashboardHeader } from "@/components/layout/header/dashboard-header"
import { AIFormBuilder } from "@/components/forms/ai-form-builder"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select"

interface Workspace {
  id: string;
  name: string;
}

function AIBuilderContent() {
  const { workspaces, isLoading } = useData()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string | undefined>()
  const [aiBuilderOpen, setAiBuilderOpen] = useState(false)

  // Pre-select workspace from URL parameter
  useEffect(() => {
    const workspaceParam = searchParams.get('workspace')
    if (workspaceParam && workspaces.some((ws: Workspace) => ws.id === workspaceParam)) {
      setSelectedWorkspaceId(workspaceParam)
    }
  }, [searchParams, workspaces])

  if (isLoading) {
    return (
      <React.Fragment>
        <DashboardHeader />
        <div className="max-w-xl mx-auto px-4 py-10 space-y-6">
          {/* Title skeleton */}
          <div className="h-8 w-56 bg-gray-100 rounded animate-pulse" />
          
          {/* Label skeleton */}
          <div className="space-y-2">
            <div className="h-4 w-32 bg-gray-50 rounded animate-pulse" />
            <div className="h-10 w-full bg-gray-50 rounded animate-pulse" />
          </div>
          
          {/* Button skeleton */}
          <div className="h-10 w-36 bg-gray-100 rounded animate-pulse" />
        </div>
      </React.Fragment>
    )
  }

  if (workspaces.length === 0) {
    return (
      <div className="p-8 space-y-4">
        <p className="text-gray-600">You don't have any workspaces yet. Create one first to start building forms with AI.</p>
        <Button onClick={() => router.push("/dashboard/workspace")}> <Plus className="h-4 w-4 mr-2"/> Create Workspace</Button>
      </div>
    )
  }

  return (
    <React.Fragment>
      <DashboardHeader />
      <div className="max-w-xl mx-auto px-4 py-10 space-y-6">
        <h1 className="text-3xl font-bold mb-4">Create Form with AI</h1>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Select workspace</label>
          <Select
            value={selectedWorkspaceId}
            onValueChange={(val: string) => setSelectedWorkspaceId(val)}
          >
            <SelectTrigger className="w-full" id="workspace">
              <SelectValue placeholder="Choose workspace..." />
            </SelectTrigger>
            <SelectContent>
              {workspaces.map((ws: Workspace) => (
                <SelectItem key={ws.id} value={ws.id}>{ws.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button
          disabled={!selectedWorkspaceId}
          onClick={() => setAiBuilderOpen(true)}
        >
          <Plus className="h-4 w-4 mr-2" />
          Start AI Builder
        </Button>
      </div>

      <AIFormBuilder
        isOpen={aiBuilderOpen}
        onOpenChange={setAiBuilderOpen}
        workspaceId={selectedWorkspaceId}
      />
    </React.Fragment>
  )
}

export default function AIBuilderPage() {
  return (
    <Suspense fallback={
      <div className="max-w-xl mx-auto px-4 py-10 space-y-6">
        <div className="h-8 w-56 bg-gray-100 rounded animate-pulse" />
        <div className="space-y-2">
          <div className="h-4 w-32 bg-gray-50 rounded animate-pulse" />
          <div className="h-10 w-full bg-gray-50 rounded animate-pulse" />
        </div>
        <div className="h-10 w-36 bg-gray-100 rounded animate-pulse" />
      </div>
    }>
      <AIBuilderContent />
    </Suspense>
  )
} 