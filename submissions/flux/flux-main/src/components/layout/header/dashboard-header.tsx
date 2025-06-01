'use client'

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { Search, Sparkles, Settings, ChevronRight } from 'lucide-react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useData } from '@/contexts/DataContext';

// Define specific props for dynamic breadcrumbs
interface DashboardHeaderProps {
  workspaceId?: string;
  workspaceName?: string;
  formId?: string;
  formName?: string;
  breadcrumbs?: Array<{
    label: string;
    href: string;
  }>;
}

export function DashboardHeader({
  workspaceId,
  workspaceName,
  formId,
  formName,
  breadcrumbs
}: DashboardHeaderProps) {
  const router = useRouter();
  const pathname = usePathname(); // Get current path
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const { searchForms, searchWorkspaces } = useData();

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowSearchResults(false);
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    if (value.length > 0) {
      setShowSearchResults(true);
    } else {
      setShowSearchResults(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/dashboard/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setShowSearchResults(false);
    }
  };

  // Search results
  const matchingForms = debouncedQuery ? searchForms(debouncedQuery).slice(0, 5) : [];
  const matchingWorkspaces = debouncedQuery ? searchWorkspaces(debouncedQuery).slice(0, 3) : [];
  const hasResults = matchingForms.length > 0 || matchingWorkspaces.length > 0;

  // Determine breadcrumb parts based on props and path
  const showWorkspace = workspaceId && workspaceName && pathname.includes(`/workspace/${workspaceId}`);
  const showForm = formId && formName && pathname.includes(`/forms/${formId}`);
  const isBaseDashboard = pathname === '/dashboard';

  return (
    <header className="sticky top-0 z-50 w-full bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        <div className="mr-4 flex items-center">
          {/* Logo and App Name */}
          <Link href="/dashboard" className="mr-1 flex items-center space-x-2">
            <Image src="/logo.png" alt="Flux Logo" width={24} height={24} />
            <span className="font-medium font-bold">Flux</span>
          </Link>
          
          {/* Custom Breadcrumbs or Dynamic Breadcrumbs */}
          <nav className="flex items-center space-x-1 text-sm text-muted-foreground">
          <ChevronRight className="h-4 w-4 text-muted-foreground mx-1" />

            {isBaseDashboard ? (
              <span className="font-medium text-foreground">Home</span>
            ) : breadcrumbs ? (
              breadcrumbs.map((crumb, index) => (
                <React.Fragment key={index}>
                  {index > 0 && <ChevronRight className="h-4 w-4" />}
                  <Link 
                    href={crumb.href}
                    className="font-medium text-foreground hover:text-foreground/80"
                  >
                    {crumb.label}
                  </Link>
                </React.Fragment>
              ))
            ) : (
              // Use default breadcrumb logic
              <>
                
                {/* Show Workspace Name if applicable */} 
                {(showWorkspace || showForm) && workspaceId && workspaceName && (
                  <>
                    
                    <Link 
                      href={`/dashboard/workspace/${workspaceId}`}
                      className="font-medium text-foreground hover:text-foreground/80"
                    >
                      {workspaceName}
                    </Link>
                  </>
                )}

                {/* Show Form Name if applicable */}
                {showForm && formName && (
                  <>
                    <ChevronRight className="h-4 w-4" />
                    {/* Form name is usually not a link itself */}
                    <span className="font-medium text-foreground">{formName}</span> 
                  </>
                )}
              </>
            )}
          </nav>
        </div>

        {/* Right side actions - Search Bar + Icons */}
        <div className="flex flex-1 items-center justify-end space-x-2">
          {/* Search Input Form with Dropdown Results */}
          <div className="relative mr-2 w-full max-w-xs" onClick={(e) => e.stopPropagation()}>
            <form onSubmit={handleSearchSubmit}>
              <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search..."
                className="w-full pl-8 h-9" // Adjust padding and height
                value={searchQuery}
                onChange={handleSearchChange}
                onFocus={() => {
                  if (searchQuery.trim().length > 0) {
                    setShowSearchResults(true);
                  }
                }}
              />
            </form>
            
            {/* Search Results Dropdown */}
            {showSearchResults && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-md shadow-lg border border-gray-200 py-2 z-50">
                {!hasResults && debouncedQuery && (
                  <div className="px-4 py-2 text-sm text-gray-500">
                    No results found for "{debouncedQuery}"
                  </div>
                )}
                
                {matchingWorkspaces.length > 0 && (
                  <>
                    <div className="px-3 py-1 text-xs font-medium text-gray-500">
                      Workspaces
                    </div>
                    {matchingWorkspaces.map((workspace) => (
                      <div 
                        key={workspace.id}
                        className="px-4 py-2 hover:bg-gray-50 cursor-pointer text-sm"
                        onClick={() => {
                          router.push(`/dashboard/workspace/${workspace.id}`);
                          setShowSearchResults(false);
                          setSearchQuery('');
                        }}
                      >
                        <div className="font-medium">{workspace.name}</div>
                        <div className="text-xs text-gray-500">
                          {workspace.formCount || 0} form{workspace.formCount !== 1 ? 's' : ''}
                        </div>
                      </div>
                    ))}
                  </>
                )}
                
                {matchingForms.length > 0 && (
                  <>
                    <div className="px-3 py-1 text-xs font-medium text-gray-500 mt-2">
                      Forms
                    </div>
                    {matchingForms.map((form) => (
                      <div 
                        key={form.id}
                        className="px-4 py-2 hover:bg-gray-50 cursor-pointer text-sm"
                        onClick={() => {
                          router.push(`/dashboard/forms/${form.id}`);
                          setShowSearchResults(false);
                          setSearchQuery('');
                        }}
                      >
                        <div className="font-medium">{form.title}</div>
                        <div className="text-xs text-gray-500">
                          {!form.published && 'Draft • '}
                          Last edited: {new Date(form.updatedAt).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </>
                )}
                
                {hasResults && (
                  <div className="px-4 py-2 border-t border-gray-100 mt-2">
                    <button 
                      className="text-xs text-blue-600 hover:text-blue-800"
                      onClick={() => {
                        router.push(`/dashboard/search?q=${encodeURIComponent(searchQuery.trim())}`);
                        setShowSearchResults(false);
                      }}
                    >
                      View all results
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* AI Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push('/dashboard/ai')}
            aria-label="AI Features"
          >
            <Sparkles className="h-4 w-4" />
          </Button>

          {/* Settings Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push(formId ? `/dashboard/forms/${formId}/settings` : '/dashboard/settings')}
            aria-label="Settings"
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
} 