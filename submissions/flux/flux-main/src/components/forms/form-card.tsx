import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Share, Trash2, Edit, MoreHorizontal, ClipboardCopy, Eye } from 'lucide-react'

import { 
  Card, 
  CardContent,
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { toast } from '@/hooks/use-toast'

interface FormCardProps {
  form: {
    id: string
    title: string
    description?: string | null
    published: boolean
    responseCount?: number
    updatedAt: Date
  }
  onDelete: (formId: string) => void
}

export function FormCard({ form, onDelete }: FormCardProps) {
  const router = useRouter()
  const [showShareDialog, setShowShareDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  
  const formattedDate = new Date(form.updatedAt).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
  
  const shareUrl = `${window.location.origin}/forms/${form.id}`
  
  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareUrl)
    toast({
      title: 'Link copied to clipboard',
      duration: 3000,
    })
  }
  
  const handleEditForm = (e: React.MouseEvent) => {
    e.stopPropagation()
    router.push(`/dashboard/forms/${form.id}`)
  }
  
  const handleViewResponses = (e: React.MouseEvent) => {
    e.stopPropagation()
    router.push(`/dashboard/forms/${form.id}/responses`)
  }
  
  const handleDeleteForm = (e: React.MouseEvent) => {
    e.stopPropagation()
    setShowDeleteDialog(true)
  }
  
  const confirmDelete = async () => {
    try {
      // Use the trash API endpoint to move the form to trash
      const response = await fetch(`/api/forms/${form.id}/trash`, {
        method: 'PATCH',
      });
      
      if (!response.ok) {
        throw new Error('Failed to move form to trash');
      }
      
      // Call the parent component's onDelete handler to update UI
      onDelete(form.id);
      setShowDeleteDialog(false);
      
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
    }
  }

  return (
    <>
      <Card 
        className="border border-border hover:border-primary/20 hover:shadow-sm transition-all cursor-pointer"
        onClick={handleEditForm}
      >
        <CardHeader className="pb-2 flex flex-row justify-between items-start">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              {form.title}
              {form.published && (
                <Badge variant="secondary" className="text-xs">Published</Badge>
              )}
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
              <DropdownMenuItem onClick={handleEditForm}>
                <Edit className="h-4 w-4 mr-2" />
                Edit form
              </DropdownMenuItem>
              <DropdownMenuItem onClick={(e) => {
                e.stopPropagation()
                setShowShareDialog(true)
              }}>
                <Share className="h-4 w-4 mr-2" />
                Share form
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleViewResponses}>
                <Eye className="h-4 w-4 mr-2" />
                View responses
              </DropdownMenuItem>
              <DropdownMenuItem 
                className="text-destructive focus:text-destructive"
                onClick={handleDeleteForm}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete form
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </CardHeader>
        <CardContent>
          {form.description && (
            <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
              {form.description}
            </p>
          )}
          <p className="text-sm text-muted-foreground">
            {form.responseCount === 0 || form.responseCount === undefined
              ? 'No responses'
              : form.responseCount === 1
                ? '1 response'
                : `${form.responseCount} responses`}
          </p>
        </CardContent>
      </Card>
      
      {/* Share Form Dialog */}
      <Dialog open={showShareDialog} onOpenChange={setShowShareDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Share Form</DialogTitle>
            <DialogDescription>
              Copy the link below to share your form with others.
            </DialogDescription>
          </DialogHeader>
          <div className="flex items-center gap-2 mt-4">
            <input
              type="text"
              value={shareUrl}
              readOnly
              className="flex-1 p-2 text-sm border rounded-md"
            />
            <Button size="sm" onClick={handleCopyLink}>
              <ClipboardCopy className="h-4 w-4 mr-2" />
              Copy
            </Button>
          </div>
          {!form.published && (
            <p className="text-sm text-amber-600 mt-2">
              Note: This form is not published yet. Recipients won't be able to submit responses.
            </p>
          )}
        </DialogContent>
      </Dialog>
      
      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Move to Trash</DialogTitle>
            <DialogDescription>
              Are you sure you want to move this form to trash? You can restore it from the trash later.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              Move to Trash
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
} 