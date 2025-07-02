/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from "@clerk/nextjs"
import { Undo, Trash2, AlertCircle, RotateCcw, Loader2, Search, MoreVertical } from 'lucide-react';

import { workspaceService } from '@/lib/services/workspace-service';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from '@/components/ui/dialog';
import { toast } from '@/components/ui/use-toast';
import prisma from '@/lib/db';

interface UserData {
  id: string;
  externalId: string;
  email: string;
  name?: string;
  imageUrl?: string;
}

interface FormItemProps {
  id: string;
  title: string;
  description?: string | null;
  updatedAt: Date;
  workspace?: {
    id: string;
    name: string;
  };
}

// Demo data for fallback
const DEMO_TRASH_ITEMS: FormItemProps[] = [
  {
    id: "1",
    title: "Sample Deleted Form",
    description: "This is a sample form shown because we couldn't load the real trash items.",
    updatedAt: new Date(),
    workspace: {
      id: "1",
      name: "Sample Workspace"
    }
  }
];

interface TrashItem {
  id: string;
  title: string;
  description?: string | null;
  updatedAt: Date;
  workspace?: {
    id: string;
    name: string;
  };
}

export default function TrashPage() {
  const { user: clerkUser, isLoaded } = useUser();
  const router = useRouter();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [trashItems, setTrashItems] = useState<FormItemProps[]>([]);
  const [filteredItems, setFilteredItems] = useState<FormItemProps[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showEmptyTrashDialog, setShowEmptyTrashDialog] = useState(false);
  const [actionInProgress, setActionInProgress] = useState<Record<string, boolean>>({});

  // Get the current user data from API
  useEffect(() => {
    const fetchCurrentUser = async () => {
      if (!isLoaded || !clerkUser) return;
      
      try {
        const response = await fetch('/api/user');
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.error || 'Failed to fetch user data');
        }
        
        const userData = await response.json();
        setUserData(userData);
        return userData;
      } catch (error) {
        console.error('Error fetching current user:', error);
        setError(error instanceof Error ? error.message : 'Unknown error');
        setIsLoading(false);
        return null;
      }
    };
    
    fetchCurrentUser();
  }, [clerkUser, isLoaded]);

  // Load trash items once we have the user data
  useEffect(() => {
    const fetchTrashItems = async () => {
      if (!userData) return;
      
      try {
        // Use the direct API endpoint for trash items
        const response = await fetch('/api/trash');
        if (!response.ok) {
          throw new Error('Failed to fetch trash items');
        }
        
        const items = await response.json();
        setTrashItems(items);
        setFilteredItems(items);
      } catch (error) {
        console.error('Failed to fetch trash items:', error);
        setError('Failed to load trash items. Please try again later.');
        // Don't use demo data in production
        setTrashItems([]);
        setFilteredItems([]);
      } finally {
        setIsLoading(false);
      }
    };

    if (userData) {
      fetchTrashItems();
    }
  }, [userData]);

  // Filter items based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredItems(trashItems);
      return;
    }
    
    const lowerQuery = searchQuery.toLowerCase();
    const filtered = trashItems.filter(
      item => 
        item.title.toLowerCase().includes(lowerQuery) || 
        (item.description && item.description.toLowerCase().includes(lowerQuery)) ||
        (item.workspace?.name && item.workspace.name.toLowerCase().includes(lowerQuery))
    );
    
    setFilteredItems(filtered);
  }, [searchQuery, trashItems]);

  const handleRestore = async (formId: string) => {
    setActionInProgress(prev => ({ ...prev, [formId]: true }));
    
    try {
      // Use direct API call to restore form
      const response = await fetch(`/api/forms/${formId}/restore`, {
        method: 'PATCH',
      });
      
      if (!response.ok) {
        throw new Error('Failed to restore item');
      }
      
      // Update UI without refetching
      setTrashItems(trashItems.filter(item => item.id !== formId));
      setFilteredItems(filteredItems.filter(item => item.id !== formId));
      
      toast({
        title: "Item restored",
        description: "The item has been restored successfully.",
      });
    } catch (error) {
      console.error('Failed to restore item:', error);
      toast({
        title: "Failed to restore",
        description: "There was an error restoring this item.",
        variant: "destructive",
      });
    } finally {
      setActionInProgress(prev => ({ ...prev, [formId]: false }));
    }
  };

  const handleDelete = async (formId: string) => {
    setActionInProgress(prev => ({ ...prev, [formId]: true }));
    
    try {
      // Use direct API call to delete form permanently
      const response = await fetch('/api/trash/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ formId }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete item');
      }
      
      // Update UI without refetching
      setTrashItems(trashItems.filter(item => item.id !== formId));
      setFilteredItems(filteredItems.filter(item => item.id !== formId));
      
      toast({
        title: "Item deleted permanently",
        description: "The item has been permanently deleted.",
      });
    } catch (error) {
      console.error('Failed to delete item:', error);
      toast({
        title: "Failed to delete",
        description: "There was an error deleting this item.",
        variant: "destructive",
      });
    } finally {
      setActionInProgress(prev => ({ ...prev, [formId]: false }));
    }
  };

  const handleEmptyTrash = async () => {
    if (!userData) return;
    
    setIsLoading(true);
    
    try {
      // Use direct API call to empty trash
      const response = await fetch('/api/trash/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ emptyTrash: true }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to empty trash');
      }
      
      setTrashItems([]);
      setFilteredItems([]);
      
      toast({
        title: "Trash emptied",
        description: "All items have been permanently deleted.",
      });
    } catch (error) {
      console.error('Failed to empty trash:', error);
      toast({
        title: "Failed to empty trash",
        description: "There was an error emptying the trash.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
      setShowEmptyTrashDialog(false);
    }
  };

  // Format relative time
  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const pastDate = new Date(date);
    const diffMs = now.getTime() - pastDate.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 30) {
      return `${diffDays} days ago`;
    } else {
      return pastDate.toLocaleDateString();
    }
  };

  if (isLoading && trashItems.length === 0) {
    return (
      <div className="container mx-auto py-8 max-w-6xl">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Trash</h1>
        </div>
        
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8 max-w-6xl">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Trash</h1>
        </div>
        
        <div className="bg-destructive/10 p-4 rounded-md flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-destructive">Error Loading Trash</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 max-w-6xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Trash</h1>
        
        {trashItems.length > 0 && (
          <Button 
            variant="destructive" 
            size="sm"
            onClick={() => setShowEmptyTrashDialog(true)}
            disabled={isLoading}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Empty Trash
          </Button>
        )}
      </div>
      
      {trashItems.length === 0 ? (
        <div className="bg-muted/40 rounded-md p-8 flex flex-col items-center justify-center">
          <div className="bg-muted rounded-full p-4">
            <Trash2 className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-2 mt-4">No Forms in Trash</h3>
          <p className="text-muted-foreground max-w-md text-center">
            Items you move to trash will appear here. Forms in trash will be permanently deleted after 30 days.
          </p>
          <Button 
            variant="outline" 
            className="mt-4"
            onClick={() => router.push('/dashboard')}
          >
            Go to Dashboard
          </Button>
        </div>
      ) : (
        <>
          <div className="flex mb-4">
            <div className="relative w-full max-w-sm">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search trash..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          
          <div className="bg-white rounded-md border shadow-sm overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Workspace</TableHead>
                  <TableHead>Deleted</TableHead>
                  <TableHead className="w-[100px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredItems.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-medium">
                      {item.title}
                      {item.description && (
                        <p className="text-xs text-muted-foreground truncate max-w-xs">
                          {item.description}
                        </p>
                      )}
                    </TableCell>
                    <TableCell>
                      {item.workspace?.name || "—"}
                    </TableCell>
                    <TableCell>
                      {formatTimeAgo(item.updatedAt)}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleRestore(item.id)}
                          disabled={actionInProgress[item.id]}
                          title="Restore"
                        >
                          {actionInProgress[item.id] ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <RotateCcw className="h-4 w-4" />
                          )}
                        </Button>
                        
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              disabled={actionInProgress[item.id]}
                            >
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem 
                              className="text-destructive focus:text-destructive"
                              onClick={() => handleDelete(item.id)}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete permanently
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </>
      )}
      
      {/* Empty Trash Confirmation Dialog */}
      <Dialog open={showEmptyTrashDialog} onOpenChange={setShowEmptyTrashDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Empty Trash?</DialogTitle>
            <DialogDescription>
              This action cannot be undone. All items in the trash will be permanently deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button
              variant="destructive"
              onClick={handleEmptyTrash}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Empty Trash
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 