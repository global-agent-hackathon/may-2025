"use client";

import { Suspense } from "react"
import { HydrationBoundary, QueryClient, dehydrate } from "@tanstack/react-query"
import { DashboardHeader } from "@/components/layout/header/dashboard-header"
import { WorkspaceContent } from "@/components/features/workspace/workspace-content"
import { getWorkspace } from "@/lib/api/workspace"
import { Skeleton } from "@/components/ui/skeleton"

interface PageProps {
  params: Promise<{
    id: string
  }>
}

export default async function WorkspaceDetailPage({ params }: PageProps) {
  const { id } = await params;
  const queryClient = new QueryClient()

  // Prefetch workspace data
  queryClient.prefetchQuery({
    queryKey: ["workspace", id],
    queryFn: () => getWorkspace(id)
  })

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <DashboardHeader workspaceId={id} />
      
      <main className="flex-1">
        <HydrationBoundary state={dehydrate(queryClient)}>
          <Suspense fallback={<WorkspaceLoading />}>
            <div className="container mx-auto py-8 px-4 md:px-8 max-w-7xl">
              <WorkspaceContent workspaceId={id} />
            </div>
          </Suspense>
        </HydrationBoundary>
      </main>
    </div>
  )
}

function WorkspaceLoading() {
  return (
    <div className="container mx-auto py-8 px-4 md:px-8 max-w-7xl">
      {/* Header skeleton */}
      <div className="flex items-center justify-between mb-8">
        <div className="space-y-2">
          <Skeleton className="h-8 w-[200px]" />
          <Skeleton className="h-4 w-[300px]" />
        </div>
        <div className="flex items-center gap-2">
          <Skeleton className="h-9 w-9 rounded-md" />
          <Skeleton className="h-9 w-[120px] rounded-md" />
        </div>
      </div>

      {/* Search bar skeleton */}
      <div className="mb-6">
        <Skeleton className="h-10 w-full max-w-md" />
      </div>

      {/* Forms grid skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="group relative">
            <Skeleton className="h-[140px] w-full rounded-lg" />
          </div>
        ))}
      </div>
    </div>
  )
}
