import React, { useState } from 'react';
import { useRouter } from "next/navigation";
import { Edit, MoreHorizontal, Trash2 } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from '@/hooks/use-toast';

interface WorkspaceCardProps {
  workspace: {
    id: string;
    name: string;
    formCount: number | undefined;
    createdAt: Date;
    updatedAt: Date;
  };
  onEdit: (workspace: any) => void;
  onDelete: (workspaceId: string) => void;
}

export function WorkspaceCard({ workspace, onEdit, onDelete }: WorkspaceCardProps) {
  const router = useRouter();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  
  const formattedDate = new Date(workspace.updatedAt).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
  
  const handleClick = () => {
    router.push(`/dashboard/workspace/${workspace.id}`);
  };

  const handleDeleteWorkspace = async () => {
    try {
      // First, move all forms in this workspace to trash
      const formsResponse = await fetch(`/api/workspace/${workspace.id}/forms`);
      if (formsResponse.ok) {
        const forms = await formsResponse.json();
        
        // Move each form to trash
        for (const form of forms) {
          await fetch(`/api/forms/${form.id}/trash`, {
            method: 'PATCH',
          });
        }
      }
      
      // Then delete the workspace
      const response = await fetch(`/api/workspace/${workspace.id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete workspace');
      }
      
      // Call the parent's onDelete handler to update UI
      onDelete(workspace.id);
      setShowDeleteDialog(false);
      
      toast({
        title: 'Workspace deleted',
        description: `The workspace "${workspace.name}" has been deleted and its forms moved to trash.`,
        duration: 3000,
      });
    } catch (error) {
      console.error('Error deleting workspace:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete workspace',
        variant: 'destructive',
        duration: 3000,
      });
    }
  };
  
  return (
    <>
      <Card 
        className="border border-border hover:border-primary/20 hover:shadow-sm transition-all cursor-pointer"
        onClick={handleClick}
      >
        <CardHeader className="pb-2 flex flex-row justify-between items-start">
          <div>
            <CardTitle className="text-lg">
              {workspace.name}
            </CardTitle>
            <CardDescription>
              Last updated {formattedDate}
            </CardDescription>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={(e) => {
                e.stopPropagation();
                onEdit(workspace);
              }}>
                <Edit className="h-4 w-4 mr-2" />
                Edit workspace
              </DropdownMenuItem>
              <DropdownMenuItem 
                className="text-destructive focus:text-destructive"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowDeleteDialog(true);
                }}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete workspace
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {!workspace.formCount || workspace.formCount === 0
              ? 'No forms'
              : workspace.formCount === 1
                ? '1 form'
                : `${workspace.formCount} forms`}
          </p>
        </CardContent>
      </Card>
      
      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Workspace</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this workspace? All forms in this workspace will be moved to trash and can be restored later.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteWorkspace}>
              Delete Workspace
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
} 