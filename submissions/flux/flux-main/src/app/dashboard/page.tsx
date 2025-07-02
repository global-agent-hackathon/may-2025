/* eslint-disable @typescript-eslint/no-unused-vars */
'use client'

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from "@clerk/nextjs"
import { useData } from '@/contexts/DataContext';
import { toast } from '@/hooks/use-toast';
import { Plus, MoreHorizontal, FolderIcon, Trash2, MessageSquare, Sparkles } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { 
  Card, 
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle 
} from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

import { workspaceService } from '@/lib/services/workspace-service';
import { WorkspaceModal } from "@/components/features/workspace/workspace-modal";
import { DashboardHeader } from '@/components/layout/header/dashboard-header';
import { FormCreateModal } from '@/components/forms/form-create-modal';
import { MemoryUsageIndicator } from '@/components/memory/MemoryUsageIndicator';

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useUser();
  const { forms, workspaces, isLoading, refetchData, forceRefresh } = useData();
  const [isWorkspaceModalOpen, setIsWorkspaceModalOpen] = useState(false);
  const [isFormCreateModalOpen, setIsFormCreateModalOpen] = useState(false);
  const [formActionInProgress, setFormActionInProgress] = useState<Record<string, boolean>>({});
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string | undefined>();

  // Function to create a new form
  const handleCreateForm = () => {
    if (workspaces.length > 0) {
      // Set the first workspace as default
      setSelectedWorkspaceId(workspaces[0].id);
      setIsFormCreateModalOpen(true);
    } else {
      // If no workspaces, open workspace modal first
      setIsWorkspaceModalOpen(true);
    }
  };

  // Function to open workspace modal
  const handleCreateWorkspace = () => {
    setIsWorkspaceModalOpen(true);
  };

  const handleDeleteForm = async (e: React.MouseEvent, formId: string) => {
    e.stopPropagation();
    
    // Prevent multiple clicks
    if (formActionInProgress[formId]) return;
    
    setFormActionInProgress(prev => ({ ...prev, [formId]: true }));
    
    try {
      // Use the trash API endpoint to move the form to trash
      const response = await fetch(`/api/forms/${formId}/trash`, {
        method: 'PATCH',
      });
      
      if (!response.ok) {
        throw new Error('Failed to move form to trash');
      }
      
      // Refresh data to update UI
      await forceRefresh();
      
      toast({
        title: 'Form moved to trash',
        description: 'The form has been moved to trash.',
        duration: 3000,
      });
    } catch (error) {
      console.error('Error moving form to trash:', error);
      toast({
        title: 'Error',
        description: 'Failed to move form to trash',
        variant: 'destructive',
        duration: 3000,
      });
    } finally {
      setFormActionInProgress(prev => ({ ...prev, [formId]: false }));
    }
  };

  // Handle successful form creation
  const handleFormCreateSuccess = (formId: string) => {
    router.push(`/dashboard/forms/${formId}`);
  };

  return (
    <>
      <DashboardHeader />

      <div className="flex-1 overflow-auto bg-white">
        <div className="max-w-6xl mx-auto px-6 py-8">
          {/* Header Section */}
          <div className="mb-10">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">Home</h1>
                <p className="text-sm text-gray-500">Manage your workspaces and forms</p>
              </div>
              <div className="flex items-center space-x-4">
                <Button 
                  onClick={handleCreateWorkspace}
                  className="bg-gray-900 hover:bg-gray-800 text-white font-medium px-4 py-2 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                  size="sm"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  New Workspace
                </Button>
              </div>
            </div>
          </div>

          {/* Workspaces Section and Memory Usage Indicator */}
          <div className="flex items-start space-x-4 mb-12">
            <div className="flex-1">
              <div className="flex items-center mb-6">
                <h2 className="text-xs font-medium text-gray-500 uppercase tracking-wider">Workspaces</h2>
                <div className="ml-4 flex-1 h-px bg-gray-200"></div>
              </div>
              
              {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="p-5 bg-white border border-gray-100 rounded-lg">
                      <div className="flex items-start justify-between mb-3">
                        <div className="h-5 w-32 bg-gray-100 rounded animate-pulse" />
                        <div className="h-4 w-4 bg-gray-50 rounded animate-pulse opacity-0" />
                      </div>
                      <div className="h-4 w-16 bg-gray-50 rounded animate-pulse" />
                    </div>
                  ))}
                </div>
              ) : workspaces.length === 0 ? (
                <div className="text-center py-12 bg-gray-50/50 rounded-lg border border-gray-200/60">
                  <FolderIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No workspaces yet</h3>
                  <p className="text-gray-500 mb-6 max-w-sm mx-auto">
                    Create your first workspace to organize your forms and collaborate with your team.
                  </p>
                  <Button 
                    onClick={handleCreateWorkspace}
                    className="bg-purple-600 hover:bg-purple-700 text-white font-medium px-6 py-2.5 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Create Workspace
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {workspaces.map((workspace) => (
                    <div
                      key={workspace.id}
                      onClick={() => router.push(`/dashboard/workspace/${workspace.id}`)}
                      className="group p-5 bg-white border border-gray-200/60 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all duration-200 cursor-pointer"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-gray-900 truncate group-hover:text-gray-700 transition-colors">
                            {workspace.name}
                          </h3>
                        </div>
                        <div className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <MoreHorizontal className="h-4 w-4 text-gray-400" />
                        </div>
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <span>{workspace.formCount || 0} form{workspace.formCount !== 1 ? 's' : ''}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <MemoryUsageIndicator context="dashboard" className="w-64" />
          </div>

          {/* Recent Forms Section */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <h2 className="text-xs font-medium text-gray-500 uppercase tracking-wider">Recent Forms</h2>
                <div className="ml-4 flex-1 h-px bg-gray-200"></div>
              </div>
              {forms.length > 0 && (
                <Button 
                  onClick={handleCreateForm}
                  variant="ghost"
                  size="sm"
                  className="text-gray-600 hover:text-gray-900 hover:bg-gray-50/80"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  New Form
                </Button>
              )}
            </div>
            
            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="flex items-center justify-between p-4 rounded-lg">
                    <div className="flex items-center gap-4 flex-1">
                      <div className="w-2 h-2 rounded-full bg-gray-100 animate-pulse" />
                      <div className="space-y-2 flex-1">
                        <div className="h-4 w-48 bg-gray-100 rounded animate-pulse" />
                        <div className="flex items-center gap-3">
                          <div className="h-3 w-20 bg-gray-50 rounded animate-pulse" />
                          <div className="h-3 w-24 bg-gray-50 rounded animate-pulse" />
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <div className="h-8 w-8 bg-gray-50 rounded animate-pulse opacity-0" />
                      <div className="h-8 w-8 bg-gray-50 rounded animate-pulse opacity-0" />
                    </div>
                  </div>
                ))}
              </div>
            ) : forms.length === 0 ? (
              <div className="text-center py-12 bg-gray-50/50 rounded-lg border border-gray-200/60">
                <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No forms yet</h3>
                <p className="text-gray-500 mb-6 max-w-sm mx-auto">
                  Create your first form to start collecting responses from your audience.
                </p>
                <Button 
                  onClick={handleCreateForm}
                  className="bg-purple-600 hover:bg-purple-700 text-white font-medium px-6 py-2.5 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Create Form
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                {forms.map((form) => (
                  <div
                    key={form.id}
                    onClick={() => router.push(`/dashboard/forms/${form.id}`)}
                    className="group flex items-center justify-between p-4 bg-white border border-gray-200/60 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all duration-200 cursor-pointer"
                  >
                    <div className="flex items-center gap-4 flex-1 min-w-0">
                      <div className="w-2 h-2 rounded-full bg-gray-300 flex-shrink-0"></div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="font-medium text-gray-900 truncate group-hover:text-gray-700 transition-colors">
                            {form.title}
                          </h3>
                          {!form.published && (
                            <span className="px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600 rounded-md">
                              Draft
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-500">
                          Updated {new Date(form.updatedAt).toLocaleDateString(undefined, { 
                            day: 'numeric', 
                            month: 'short',
                            year: new Date(form.updatedAt).getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
                          })} • {form.submissionCount || 0} submission{(form.submissionCount || 0) !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-gray-500 hover:text-gray-700 hover:bg-gray-100/80"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/dashboard/forms/${form.id}`);
                        }}
                      >
                        <MessageSquare className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-gray-500 hover:text-red-600 hover:bg-red-50"
                        onClick={(e) => handleDeleteForm(e, form.id)}
                        disabled={formActionInProgress[form.id]}
                      >
                        {formActionInProgress[form.id] ? (
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Form Create Modal */}
      <FormCreateModal
        isOpen={isFormCreateModalOpen}
        onOpenChange={setIsFormCreateModalOpen}
        workspaceId={selectedWorkspaceId}
        onSuccess={handleFormCreateSuccess}
      />

      {/* Workspace Modal */}
      <WorkspaceModal 
        isOpen={isWorkspaceModalOpen}
        onOpenChange={setIsWorkspaceModalOpen}
        onSuccess={() => {
          forceRefresh();
        }}
      />
    </>
  );
}
