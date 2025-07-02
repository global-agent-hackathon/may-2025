'use client'

import React from 'react';
import { usePathname } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/header/dashboard-header';
import { AppSidebar } from "@/components/layout/app-sidebar"

// This layout wrapper will handle rendering the header with proper breadcrumbs
// based on the route path
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname();
  
  // Extract path segments
  const segments = pathname.split('/').filter(Boolean);
  
  // Default props
  let headerProps = {};
  
  // Handle /dashboard/workspace route
  if (segments.length === 2 && segments[1] === 'workspace') {
    headerProps = {
      workspaceName: 'My workspaces',
      // For this special case, we're using a static breadcrumb
    };
  }
  
  // On specific routes like workspace/[id] or forms/[id], 
  // we'll need to fetch the actual data 
  // This would be better done in the specific page components
  // and passed via context, but for demo purposes, let's just render the layout
  
  return (
    <div className="flex h-screen overflow-hidden">
      <AppSidebar />
      <main className="flex-1 overflow-auto">
        {/* Remove DashboardHeader from layout since it's in each page */}
        {children}
      </main>
    </div>
  )
} 