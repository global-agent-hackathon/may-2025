"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useData } from "@/contexts/DataContext"
import { DashboardHeader } from "@/components/layout/header/dashboard-header"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { MessageSquare } from "lucide-react"

export default function SubmissionsPage() {
  const { forms, workspaces, isLoading } = useData()
  const router = useRouter()
  const [workspaceFilter, setWorkspaceFilter] = useState<string>('all')

  if (isLoading) {
    return (
      <>
        <DashboardHeader breadcrumbs={[{ label: "Form submissions", href: "/dashboard/submissions" }]} />
        <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
          {/* Title skeleton */}
          <div className="h-8 w-48 bg-gray-100 rounded animate-pulse" />

          {/* Filter skeleton */}
          <div className="h-10 w-60 bg-gray-50 rounded animate-pulse" />

          {/* Table skeleton */}
          <div className="space-y-4">
            <div className="border rounded-lg">
              {/* Table header */}
              <div className="flex items-center px-4 py-3 border-b bg-gray-50/50">
                <div className="h-4 w-20 bg-gray-100 rounded animate-pulse" />
                <div className="ml-auto h-4 w-24 bg-gray-100 rounded animate-pulse" />
              </div>
              {/* Table rows */}
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="flex items-center px-4 py-4 border-b last:border-b-0">
                  <div className="h-4 w-40 bg-gray-50 rounded animate-pulse" />
                  <div className="ml-auto flex items-center gap-4">
                    <div className="h-4 w-8 bg-gray-50 rounded animate-pulse" />
                    <div className="h-8 w-32 bg-gray-50 rounded animate-pulse" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </>
    )
  }

  const filteredForms = workspaceFilter === 'all'
    ? forms
    : forms.filter((f) => f.workspaceId === workspaceFilter)

  return (
    <>
      <DashboardHeader breadcrumbs={[{ label: "Form submissions", href: "/dashboard/submissions" }]} />
      <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
        <h1 className="text-3xl font-bold">Form submissions</h1>

        {/* Workspace filter */}
        <div className="flex items-center gap-4">
          <Select value={workspaceFilter} onValueChange={setWorkspaceFilter}>
            <SelectTrigger className="w-60">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All workspaces</SelectItem>
              {workspaces.map((ws) => (
                <SelectItem key={ws.id} value={ws.id}>{ws.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Forms list */}
        {filteredForms.length === 0 ? (
          <p className="text-gray-500 mt-6">No forms found.</p>
        ) : (
          <Table className="mt-4">
            <TableHeader>
              <TableRow>
                <TableHead>Form</TableHead>
                <TableHead className="text-right">Submissions</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredForms.map((form) => (
                <FormRow key={form.id} formId={form.id} title={form.title} submissionCount={form.submissionCount} />
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </>
  )
}

interface FormRowProps {
  formId: string
  title: string
  submissionCount?: number
}

function FormRow({ formId, title, submissionCount }: FormRowProps) {
  const router = useRouter()

  return (
    <TableRow>
      <TableCell>{title}</TableCell>
      <TableCell className="text-right">{submissionCount ?? 0}</TableCell>
      <TableCell className="text-right">
        <Button size="sm" variant="outline" onClick={() => router.push(`/dashboard/forms/${formId}#data`)}>
          <MessageSquare className="h-4 w-4 mr-1" /> Check Submissions
        </Button>
      </TableCell>
    </TableRow>
  )
} 