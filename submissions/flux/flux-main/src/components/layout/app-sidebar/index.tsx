"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useUser } from "@clerk/nextjs"
import {
  Home,
  Search,
  Plus,
  Settings,
  Trash2,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Star,
  Info,
  MoreHorizontal,
  FolderOpen,
  Inbox,
  Menu,
  X,
  Brain,
} from "lucide-react"
import { useQuery, useMutation, useQueryClient, useQueries } from "@tanstack/react-query"
import { useMemo, useEffect } from "react"
import { useState } from "react"
import { Sheet, SheetTrigger, SheetContent } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

import { UserProfile } from "@/components/features/user/user-profile"
import { cn } from "@/lib/utils"
import { WorkspaceModal } from "@/components/features/workspace/workspace-modal"
import { RainbowButton } from "@/components/magicui/rainbow-button"
import { BorderBeam } from "@/components/magicui/border-beam"
import { FormCreateModal } from "@/components/forms/form-create-modal"

interface NavItemProps {
  href: string
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  children: React.ReactNode
  active?: boolean
  onClick?: () => void
  badge?: React.ReactNode
}

interface NavSectionProps {
  title: string
  children: React.ReactNode
  collapsible?: boolean
  defaultCollapsed?: boolean
}

interface FavoriteProps {
  id: string;
  formId: string;
  createdAt: Date;
  form: {
    id: string;
    title: string;
    description?: string;
    published?: boolean;
    workspace?: {
      id: string;
      name: string;
    }
  };
}

// Type for favorites from DB which need to be transformed
interface FavoriteFromDB {
  id: string;
  userId: string;
  formId: string;
  createdAt: Date;
  updatedAt: Date;
  form?: {
    id: string;
    title: string;
    description?: string;
    published?: boolean;
    workspace?: {
      id: string;
      name: string;
    }
  };
}

interface WorkspaceProps {
  id: string
  name: string
  emoji?: string
  forms?: Array<{
    id: string
    title: string
  }>;
}

interface WorkspaceFromDB {
  id: string
  name: string
  emoji?: string | null
  userId: string
  createdAt: Date
  updatedAt: Date
}

interface FormFromDB {
  id: string
  title: string
  description?: string | null
  isDeleted: boolean
  userId: string
  [key: string]: any
}

interface UserData {
  id: string;
  externalId: string;
  email: string;
  name?: string;
  imageUrl?: string;
}

const NavItem = ({ href, icon: Icon, children, active, onClick, badge }: NavItemProps) => {
  const content = (
    <div className={cn(
      "group flex items-center gap-3 px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-150",
      "hover:bg-gray-50/80 active:bg-gray-100/50",
      active 
        ? "bg-gray-100/70 text-gray-900 shadow-sm" 
        : "text-gray-600 hover:text-gray-900"
    )}>
      <Icon className={cn(
        "h-4 w-4 transition-colors duration-150",
        active ? "text-gray-700" : "text-gray-500 group-hover:text-gray-700"
      )} />
      <span className="flex-1 truncate">{children}</span>
      {badge && (
        <span className="px-1.5 py-0.5 text-xs font-medium bg-purple-100 text-purple-700 rounded-md">
          {badge}
        </span>
      )}
    </div>
  )

  if (onClick) {
    return (
      <button onClick={onClick} className="w-full text-left">
        {content}
      </button>
    )
  }

  return <Link href={href}>{content}</Link>
}

const NavSection = ({ 
  title, 
  children, 
  collapsible = false, 
  defaultCollapsed = false 
}: NavSectionProps) => {
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed)
  
  return (
    <div className="my-2">
      <div className="flex items-center justify-between px-3 py-1 mb-1">
        {collapsible ? (
          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="flex items-center text-xs uppercase tracking-wider text-muted-foreground font-normal w-full"
          >
            {isCollapsed ? (
              <ChevronRight className="h-3 w-3 mr-1" />
            ) : (
              <ChevronDown className="h-3 w-3 mr-1" />
            )}
            {title}
          </button>
        ) : (
          <span className="text-xs uppercase tracking-wider text-muted-foreground font-normal">{title}</span>
        )}
      </div>
      {!isCollapsed && (
        <div className="space-y-1">{children}</div>
      )}
    </div>
  )
}

export function AppSidebar() {
  const router = useRouter()
  const pathname = usePathname()
  const { user, isLoaded } = useUser()
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()
  const [isWorkspaceModalOpen, setIsWorkspaceModalOpen] = React.useState(false)
  const [workspaceToEdit, setWorkspaceToEdit] = React.useState<WorkspaceProps | null>(null)
  const [expandedWorkspaces, setExpandedWorkspaces] = React.useState<Record<string, boolean>>({})
  const [isFormCreateModalOpen, setIsFormCreateModalOpen] = React.useState(false)
  const [selectedWorkspaceId, setSelectedWorkspaceId] = React.useState<string | null>(null)
  const [searchQuery, setSearchQuery] = React.useState("")
  const [isSearchFocused, setIsSearchFocused] = React.useState(false)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = React.useState(false)

  // Handle responsive layouts
  useEffect(() => {
    // Function to check if viewport is small enough to collapse sidebar
    const checkScreenSize = () => {
      setIsSidebarCollapsed(window.innerWidth < 1024);
    };
    
    // Initial check
    checkScreenSize();
    
    // Add event listener for window resize
    window.addEventListener('resize', checkScreenSize);
    
    // Cleanup
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // Fetch user data
  const { data: userData, isError: isUserError } = useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const response = await fetch('/api/user', {
        headers: {
          'Cache-Control': 'no-cache',  // Ensure fresh user data
        }
      });
      if (!response.ok) throw new Error('Failed to fetch user data');
      return response.json();
    },
    enabled: isLoaded && !!user,
  })

  // Fetch workspaces - no longer dependent on userData
  const { data: workspaces = [] as WorkspaceProps[], isLoading: isWorkspacesLoading } = useQuery({
    queryKey: ['workspaces'],
    queryFn: async () => {
      const response = await fetch('/api/workspace', {
        headers: {
          'Cache-Control': 'public, max-age=10, stale-while-revalidate=60',  // Cache for 10s, stale for 60s
        }
      });
      if (!response.ok) throw new Error('Failed to fetch workspaces');
      const data: WorkspaceFromDB[] = await response.json();
      return data.map(workspace => ({
        id: workspace.id,
        name: workspace.name,
        emoji: workspace.emoji || undefined,
        forms: []
      }));
    },
    enabled: isLoaded && !!user,  // Only need Clerk auth, not userData
    gcTime: 5 * 60 * 1000,  // Keep in cache for 5 minutes
    staleTime: 10 * 1000,  // Consider data fresh for 10 seconds
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  })

  // Fetch favorites in parallel with workspaces
  const { data: favorites = [], isLoading: isFavoritesLoading } = useQuery({
    queryKey: ['favorites'],
    queryFn: async () => {
      const response = await fetch('/api/favorites', {
        headers: {
          'Cache-Control': 'public, max-age=30, stale-while-revalidate=60',  // Cache for 30s, stale for 60s
        }
      });
      if (!response.ok) throw new Error('Failed to fetch favorites');
      const data: FavoriteFromDB[] = await response.json();
      return data
        .filter(fav => fav.form)
        .map(fav => ({
          id: fav.id,
          formId: fav.formId,
          createdAt: fav.createdAt,
          form: fav.form!
        }));
    },
    enabled: isLoaded && !!user,  // Only need Clerk auth, not userData
    gcTime: 5 * 60 * 1000,  // Keep in cache for 5 minutes
    staleTime: 30 * 1000,  // Consider data fresh for 30 seconds
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  })

  // Search forms query
  const { data: searchResults = [], isLoading: isSearchLoading } = useQuery({
    queryKey: ['search', searchQuery],
    queryFn: async () => {
      if (!searchQuery.trim()) return [];
      const response = await fetch(`/api/forms/search?q=${encodeURIComponent(searchQuery)}`);
      if (!response.ok) throw new Error('Failed to search forms');
      return response.json();
    },
    enabled: isLoaded && !!user && searchQuery.trim().length > 0,
    staleTime: 10 * 1000, // Consider data fresh for 10 seconds
  })

  interface WorkspaceFormsData {
    forms: FormFromDB[];
    deletedForms: FormFromDB[];
    activeForms: FormFromDB[];
  }

  // Fetch forms for each expanded workspace independently
  const workspaceFormsQueries = useQueries({
    queries: workspaces
      .filter(workspace => expandedWorkspaces[workspace.id])
      .map(workspace => ({
        queryKey: ['workspace', workspace.id, 'forms'],
        queryFn: async (): Promise<WorkspaceFormsData> => {
          const response = await fetch(`/api/workspace/${workspace.id}/forms`);
          if (!response.ok) throw new Error('Failed to fetch workspace forms');
          const data: FormFromDB[] = await response.json();
          return {
            forms: data,
            deletedForms: data.filter((form: FormFromDB) => form.isDeleted),
            activeForms: data.filter((form: FormFromDB) => !form.isDeleted)
          };
        },
        enabled: expandedWorkspaces[workspace.id],
        staleTime: 0,
        cacheTime: 5 * 60 * 1000, // 5 minutes
        refetchOnMount: true,
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        retry: 3,
        retryDelay: 1000
      }))
  });

  // Update workspaceForms to handle loading state
  const workspaceForms = useMemo(() => {
    const formsMap: Record<string, FormFromDB[]> = {};
    workspaces
      .filter(workspace => expandedWorkspaces[workspace.id])
      .forEach((workspace, index) => {
        const query = workspaceFormsQueries[index];
        // Include loading state in the check
        if (!query.isLoading && !query.isError && query.data) {
          formsMap[workspace.id] = pathname === '/dashboard/trash' 
            ? query.data.deletedForms 
            : query.data.activeForms;
        }
      });
    return formsMap;
  }, [workspaces, workspaceFormsQueries, expandedWorkspaces, pathname]);

  // Update toggleWorkspaceExpansion to handle expansion better
  const toggleWorkspaceExpansion = (workspaceId: string) => {
    setExpandedWorkspaces(prev => {
      const newState = {
        ...prev,
        [workspaceId]: !prev[workspaceId]
      };
      
      if (newState[workspaceId]) {
        // If expanding, immediately invalidate and refetch
        queryClient.invalidateQueries({ 
          queryKey: ['workspace', workspaceId, 'forms'],
          exact: true,
          refetchType: 'all'
        });
      }
      
      return newState;
    });
  };

  // Add loading state check for workspace forms
  const isWorkspaceFormsLoading = (workspaceId: string): boolean => {
    const queryIndex = workspaces
      .filter(w => expandedWorkspaces[w.id])
      .findIndex(w => w.id === workspaceId);
    
    if (queryIndex === -1) return false;
    const query = workspaceFormsQueries[queryIndex];
    return query?.isLoading || false;
  };

  // Optimized mutation with optimistic updates
  const toggleFavoriteMutation = useMutation({
    mutationFn: async (formId: string) => {
      const response = await fetch('/api/favorites/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ formId }),
      });
      if (!response.ok) throw new Error('Failed to toggle favorite');
      return response.json();
    },
    onMutate: async (formId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['favorites'] });
      
      // Snapshot the previous value
      const previousFavorites = queryClient.getQueryData(['favorites']);
      
      // Optimistically update favorites
      queryClient.setQueryData(['favorites'], (old: FavoriteProps[] = []) => {
        const exists = old.some(fav => fav.formId === formId);
        if (exists) {
          return old.filter(fav => fav.formId !== formId);
        }
        // You'll need the form data to add it - this is simplified
        return [...old];
      });
      
      return { previousFavorites };
    },
    onError: (err, formId, context) => {
      // Rollback on error
      if (context?.previousFavorites) {
        queryClient.setQueryData(['favorites'], context.previousFavorites);
      }
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  })

  const handleCreateForm = (workspaceId: string) => {
    if (!workspaceId) return;
    setSelectedWorkspaceId(workspaceId);
    setIsFormCreateModalOpen(true);
  };

  const handleFormCreateSuccess = (formId: string) => {
    router.push(`/dashboard/forms/${formId}`);
    if (selectedWorkspaceId) {
      queryClient.invalidateQueries({ 
        queryKey: ['workspace', selectedWorkspaceId, 'forms']
      });
    }
  };

  const handleCreateWorkspace = () => {
    setIsWorkspaceModalOpen(true);
  };

  const handleEditWorkspace = (workspace: WorkspaceProps) => {
    setWorkspaceToEdit(workspace);
    setIsWorkspaceModalOpen(true);
  };

  // Separate loading states for different sections
  const isUserLoading = !isLoaded || !userData
  const isInitialLoading = isUserLoading || isFavoritesLoading
  const isLoadingWorkspaces = isUserLoading || isWorkspacesLoading

  // Sidebar markup
  const sidebar = (
    <aside className={`${isSidebarCollapsed ? 'w-16' : 'w-64'} h-full flex flex-col bg-white border-r border-gray-200/60 transition-all duration-300`}>
      <div className="border-b border-gray-200/60 py-2.5 px-3 flex items-center justify-between">
        {!isSidebarCollapsed ? (
          <UserProfile />
        ) : (
          <div className="w-full flex justify-center">
            <Button
              variant="ghost"
              size="icon"
              className="h-10 w-10 rounded-full hover:bg-gray-100"
              onClick={() => setIsSidebarCollapsed(false)}
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </div>
        )}
      </div>
      
      {isUserError && !isSidebarCollapsed && (
        <div className="mx-3 mb-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg">
          <p className="text-xs text-amber-800 font-medium">Error loading data</p>
        </div>
      )}
      
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {/* Search Bar - Only show on expanded sidebar */}
        {!isSidebarCollapsed && (
          <div className="mt-4 mb-4 relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search forms..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setTimeout(() => setIsSearchFocused(false), 200)}
                className="pl-10 pr-8 py-2 text-sm bg-gray-50/80 border-gray-200/60 rounded-lg focus:bg-white focus:border-gray-300 transition-all duration-150"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
            
            {/* Search Results */}
            {isSearchFocused && searchQuery.trim() && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200/60 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
                {isSearchLoading ? (
                  <div className="p-3">
                    <div className="space-y-2">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="h-8 bg-gray-100/60 rounded animate-pulse" />
                      ))}
                    </div>
                  </div>
                ) : searchResults.length === 0 ? (
                  <div className="p-3 text-sm text-gray-500 text-center">
                    No forms found for "{searchQuery}"
                  </div>
                ) : (
                  <div className="py-2">
                    {searchResults.map((form: any) => (
                      <Link
                        key={form.id}
                        href={`/dashboard/forms/${form.id}`}
                        onClick={() => {
                          setSearchQuery("");
                          setIsSearchFocused(false);
                        }}
                        className="flex items-center gap-3 px-3 py-2 text-sm hover:bg-gray-50/80 transition-colors duration-150"
                      >
                        <div className="w-1.5 h-1.5 rounded-full bg-gray-400 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="truncate font-medium text-gray-900">{form.title}</div>
                          {form.workspace && (
                            <div className="truncate text-xs text-gray-500">{form.workspace.name}</div>
                          )}
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Main navigation */}
        <div className={`space-y-0.5 mb-6 ${isSidebarCollapsed ? 'flex flex-col items-center' : ''}`}>
          {/* Create Forms Button */}
          <Link href="/dashboard/ai" className="block mb-3">
            {isSidebarCollapsed ? (
              <Button
                className="w-10 h-10 rounded-full bg-purple-600 hover:bg-purple-700 text-white shadow-sm hover:shadow-md transition-all duration-200"
                size="icon"
              >
                <Sparkles className="h-4 w-4" />
              </Button>
            ) : (
              <Button 
                className="relative overflow-hidden w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2.5 px-4 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md group" 
                size="sm"
              >
                <div className="flex items-center gap-2.5">
                  <Sparkles className="h-4 w-4" />
                  <span className="flex-1">Create Forms</span>
                  <span className="px-1.5 py-0.5 text-xs font-medium bg-white/20 text-white rounded-md">
                    AI
                  </span>
                </div>
                <BorderBeam
                  size={80}
                  initialOffset={40}
                  className="from-transparent via-purple-300 to-transparent"
                  transition={{
                    type: "spring",
                    stiffness: 80,
                    damping: 30,
                  }}
                />
              </Button>
            )}
          </Link>
          
          {isSidebarCollapsed ? (
            <>
              <Link 
                href="/dashboard" 
                className={`w-10 h-10 mb-1 rounded-full flex items-center justify-center ${pathname === "/dashboard" ? 'bg-gray-100' : 'hover:bg-gray-50'}`}
              >
                <Home className={`h-5 w-5 ${pathname === "/dashboard" ? 'text-gray-700' : 'text-gray-500'}`} />
              </Link>
              <Link 
                href="/dashboard/submissions" 
                className={`w-10 h-10 mb-1 rounded-full flex items-center justify-center ${pathname === "/dashboard/submissions" ? 'bg-gray-100' : 'hover:bg-gray-50'}`}
              >
                <Inbox className={`h-5 w-5 ${pathname === "/dashboard/submissions" ? 'text-gray-700' : 'text-gray-500'}`} />
              </Link>
              <Link 
                href="/dashboard/memory" 
                className={`w-10 h-10 mb-1 rounded-full flex items-center justify-center ${pathname === "/dashboard/memory" ? 'bg-gray-100' : 'hover:bg-gray-50'}`}
              >
                <Brain className={`h-5 w-5 ${pathname === "/dashboard/memory" ? 'text-gray-700' : 'text-gray-500'}`} />
              </Link>
            </>
          ) : (
            <>
              <NavItem href="/dashboard" icon={Home} active={pathname === "/dashboard"}>
                Home
              </NavItem>
              <NavItem href="/dashboard/submissions" icon={Inbox} badge="AI">
                Form Submissions
              </NavItem>
              <NavItem href="/dashboard/memory" icon={Brain} active={pathname === "/dashboard/memory"}>
                Memory
              </NavItem>
            </>
          )}
        </div>
        
        {/* Collapsed favorites section */}
        {isSidebarCollapsed ? (
          <div className="flex flex-col items-center mb-6">
            <div className="w-10 h-10 mb-1 rounded-full flex items-center justify-center bg-gray-50">
              <Star className="h-5 w-5 text-gray-500" />
            </div>
            {!isInitialLoading && favorites.length > 0 && (
              <div className="text-xs font-medium text-gray-600 mt-1">{favorites.length}</div>
            )}
          </div>
        ) : (
          /* Full favorites section */
          <div className="mb-6">
            <div className="flex items-center px-3 py-2 mb-1">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Favorites</span>
            </div>
            {isInitialLoading ? (
              <div className="space-y-1">
                {[1, 2].map((i) => (
                  <div key={i} className="h-8 bg-gray-100/60 rounded-md animate-pulse" />
                ))}
              </div>
            ) : favorites.length === 0 ? (
              <div className="px-3 py-3">
                <div className="p-3 bg-gray-50/80 rounded-lg border border-gray-100">
                  <div className="flex items-start gap-2.5">
                    <Star className="h-4 w-4 text-gray-400 shrink-0 mt-0.5" />
                    <div className="text-xs">
                      <p className="font-medium text-gray-700 mb-1">No favorites yet</p>
                      <p className="text-gray-500 leading-relaxed">Star forms to quickly access them here.</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-0.5">
                {favorites.map((favorite) => (
                  <Link
                    key={favorite.id}
                    href={`/dashboard/forms/${favorite.form.id}`}
                    className={cn(
                      "flex items-center gap-3 px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-150 min-w-0",
                      "hover:bg-gray-50/80 active:bg-gray-100/50",
                      pathname === `/dashboard/forms/${favorite.form.id}` 
                        ? "bg-gray-100/70 text-gray-900 shadow-sm" 
                        : "text-gray-600 hover:text-gray-900"
                    )}
                  >
                    <Star className="h-4 w-4 text-amber-500 fill-amber-500 flex-shrink-0" />
                    <span className="flex-1 truncate">{favorite.form.title}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        )}
        
        {/* Workspaces - collapsed view for small screens */}
        {isSidebarCollapsed ? (
          <div className="flex flex-col items-center mb-6">
            <div className="w-10 h-10 mb-1 rounded-full flex items-center justify-center bg-gray-50">
              <FolderOpen className="h-5 w-5 text-gray-500" />
            </div>
            {!isLoadingWorkspaces && workspaces.length > 0 && (
              <div className="text-xs font-medium text-gray-600 mt-1">{workspaces.length}</div>
            )}
          </div>
        ) : (
          /* Full workspaces section */
          <div className="mb-6">
            <div className="flex items-center justify-between px-3 py-2 mb-1">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Workspaces</span>
              {!isLoadingWorkspaces && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 rounded-md hover:bg-gray-100/80 text-gray-500 hover:text-gray-700"
                  onClick={handleCreateWorkspace}
                >
                  <Plus className="h-3.5 w-3.5" />
                </Button>
              )}
            </div>
            
            {isLoadingWorkspaces ? (
              <div className="space-y-1">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-3 px-3">
                    <div className="h-4 w-4 bg-gray-100/60 rounded animate-pulse" />
                    <div className="h-8 flex-1 bg-gray-100/60 rounded-md animate-pulse" />
                  </div>
                ))}
              </div>
            ) : workspaces.length === 0 ? (
              <div className="px-3 py-3">
                <div className="p-3 bg-gray-50/80 rounded-lg border border-gray-100">
                  <div className="flex items-start gap-2.5">
                    <Info className="h-4 w-4 text-gray-400 shrink-0 mt-0.5" />
                    <div className="text-xs">
                      <p className="font-medium text-gray-700 mb-1">No workspaces</p>
                      <p className="text-gray-500 leading-relaxed mb-2">Create a workspace to organize your forms.</p>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="p-0 h-auto text-xs font-medium text-blue-600 hover:text-blue-700" 
                        onClick={handleCreateWorkspace}
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Create workspace
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {workspaces.map((workspace) => (
                  <div key={workspace.id} className="mb-1">
                    <div className="flex items-center group">
                      <button
                        onClick={() => toggleWorkspaceExpansion(workspace.id)}
                        className="p-1 hover:bg-gray-100/80 rounded-sm transition-colors duration-150"
                      >
                        {expandedWorkspaces[workspace.id] ? (
                          <ChevronDown className="h-3.5 w-3.5 text-gray-500" />
                        ) : (
                          <ChevronRight className="h-3.5 w-3.5 text-gray-500" />
                        )}
                      </button>
                      <Link 
                        href={`/dashboard/workspace/${workspace.id}`}
                        className="flex items-center gap-2 px-2 py-1.5 text-sm font-medium rounded-md transition-all duration-150 text-gray-600 hover:text-gray-900 hover:bg-gray-50/80 flex-grow min-w-0"
                      >
                        <span className="truncate">{workspace.name}</span>
                      </Link>
                      <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 rounded-md hover:bg-gray-100/80 text-gray-500 hover:text-gray-700"
                          onClick={() => handleEditWorkspace(workspace)}
                        >
                          <MoreHorizontal className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 rounded-md hover:bg-gray-100/80 text-gray-500 hover:text-gray-700"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCreateForm(workspace.id);
                          }}
                        >
                          <Plus className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                    {expandedWorkspaces[workspace.id] && (
                      <div className="ml-6 mb-2 space-y-0.5">
                        {!workspaceForms[workspace.id] ? (
                          <div className="space-y-1 py-1">
                            {[1, 2].map((i) => (
                              <div key={i} className="flex items-center gap-2 px-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-gray-200 animate-pulse" />
                                <div className="h-6 flex-1 bg-gray-100/60 rounded animate-pulse" />
                              </div>
                            ))}
                          </div>
                        ) : !workspaceForms[workspace.id]?.length ? (
                          <div className="px-2 py-1.5 text-xs text-gray-500 font-medium">
                            No forms
                          </div>
                        ) : (
                          workspaceForms[workspace.id].map((form) => (
                            <div key={form.id} className="flex items-center group">
                              <Link
                                href={`/dashboard/forms/${form.id}`}
                                className={cn(
                                  "flex items-center gap-2.5 px-2 py-1.5 text-sm font-medium rounded-md transition-all duration-150 flex-grow min-w-0",
                                  pathname === `/dashboard/forms/${form.id}`
                                    ? "bg-gray-100/70 text-gray-900 shadow-sm"
                                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50/80"
                                )}
                              >
                                <div className="w-1.5 h-1.5 rounded-full bg-gray-400 flex-shrink-0" />
                                <span className="truncate">{form.title}</span>
                              </Link>
                              <button
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  toggleFavoriteMutation.mutate(form.id);
                                }}
                                className="h-6 w-6 rounded-md hover:bg-gray-100/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-150"
                                title={favorites.some(f => f.formId === form.id) ? "Remove from favorites" : "Add to favorites"}
                              >
                                <Star className={cn(
                                  "h-3.5 w-3.5 transition-colors duration-150",
                                  favorites.some(f => f.formId === form.id) 
                                    ? "text-amber-500 fill-amber-500" 
                                    : "text-gray-400 hover:text-amber-500"
                                )} />
                              </button>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </div>
                ))}
                
                <NavItem 
                  href="/dashboard/workspace" 
                  icon={FolderOpen}
                  active={pathname === "/dashboard/workspace"}
                >
                  View all workspaces
                </NavItem>
              </>
            )}
          </div>
        )}
      </div>
      
      {/* Bottom section */}
      <div className={`border-t border-gray-200/60 p-3 ${isSidebarCollapsed ? 'flex flex-col items-center' : ''}`}>
        {isSidebarCollapsed ? (
          <>
            <Link 
              href="/dashboard/settings" 
              className="w-10 h-10 mb-2 rounded-full flex items-center justify-center hover:bg-gray-50"
            >
              <Settings className="h-5 w-5 text-gray-500" />
            </Link>
            <Link 
              href="/dashboard/trash" 
              className="w-10 h-10 mb-3 rounded-full flex items-center justify-center hover:bg-gray-50"
            >
              <Trash2 className="h-5 w-5 text-gray-500" />
            </Link>
            <Link href="/pricing">
              <Button 
                className="w-10 h-10 rounded-full bg-gray-900 hover:bg-gray-800 text-white flex items-center justify-center" 
                size="icon"
              >
                <span className="text-xs font-bold">PRO</span>
              </Button>
            </Link>
          </>
        ) : (
          <>
            <div className="space-y-0.5 mb-3">
              <NavItem href="/dashboard/settings" icon={Settings}>
                Settings
              </NavItem>
              <NavItem href="/dashboard/trash" icon={Trash2}>
                Trash
              </NavItem>
            </div>
            
            <Link href="/pricing" className="block">
              <Button 
                className="relative overflow-hidden w-full bg-gray-900 hover:bg-gray-800 text-white font-medium py-2.5 px-4 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md" 
                size="sm"
              >
                Upgrade to Pro
                <BorderBeam
                  size={80}
                  initialOffset={40}
                  className="from-transparent via-yellow-500 to-transparent"
                  transition={{
                    type: "spring",
                    stiffness: 80,
                    damping: 30,
                  }}
                />
              </Button>
            </Link>
          </>
        )}
      </div>

      {/* Modals */}
      <FormCreateModal
        isOpen={isFormCreateModalOpen}
        onOpenChange={setIsFormCreateModalOpen}
        workspaceId={selectedWorkspaceId || undefined}
        onSuccess={handleFormCreateSuccess}
      />
      
      <WorkspaceModal
        workspace={workspaceToEdit as { id: string; name: string; } | undefined}
        isOpen={isWorkspaceModalOpen}
        onOpenChange={(open) => {
          setIsWorkspaceModalOpen(open);
          if (!open) setWorkspaceToEdit(null);
        }}
        onSuccess={() => {
          if (workspaceToEdit) {
            setExpandedWorkspaces(prev => ({ ...prev, [workspaceToEdit.id]: true }));
          }
          queryClient.invalidateQueries({ queryKey: ['workspaces'] });
        }}
      />
    </aside>
  )

  return (
    <>
      {/* Mobile Drawer */}
      <div className="md:hidden">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="fixed top-4 left-4 z-50">
              <Menu className="h-6 w-6" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="p-0">
            {sidebar}
          </SheetContent>
        </Sheet>
      </div>
      
      {/* Desktop sidebar */}
      <div className="hidden md:block relative">
        {sidebar}
        
        {/* Toggle button that appears on hover for desktop - show only when sidebar is not collapsed on its own due to screen size */}
        {!isSidebarCollapsed && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsSidebarCollapsed(true)}
            className="absolute top-20 right-0 translate-x-1/2 h-8 w-8 rounded-full bg-white border border-gray-200/60 shadow-sm opacity-0 hover:opacity-100 focus:opacity-100 transition-opacity duration-200"
            aria-label="Collapse sidebar"
          >
            <ChevronDown className="h-4 w-4 -rotate-90" />
          </Button>
        )}
      </div>
    </>
  )
} 