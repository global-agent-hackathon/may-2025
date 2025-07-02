import React, { useState } from 'react';
import { ClipboardCopy, Check } from 'lucide-react';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { toast } from '@/hooks/use-toast';

interface FormShareModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  formId: string;
  isPublished: boolean;
  onPublishChange: (published: boolean) => Promise<void>;
}

export function FormShareModal({
  isOpen,
  onOpenChange,
  formId,
  isPublished,
  onPublishChange
}: FormShareModalProps) {
  const [isCopied, setIsCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [publishToggle, setPublishToggle] = useState(isPublished);
  
  const shareUrl = typeof window !== 'undefined' 
    ? `${window.location.origin}/forms/${formId}`
    : `/forms/${formId}`;
  
  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setIsCopied(true);
      
      toast({
        title: 'Link copied',
        duration: 2000,
      });
      
      // Reset copied state after 2 seconds
      setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
      toast({
        title: 'Failed to copy',
        variant: 'destructive',
      });
    }
  };
  
  const handlePublishToggle = async () => {
    setIsLoading(true);
    
    try {
      // Toggle the published state locally first
      const newPublishState = !publishToggle;
      setPublishToggle(newPublishState);
      
      // Call the parent handler to update the published state
      await onPublishChange(newPublishState);
      
      toast({
        title: newPublishState ? 'Form published' : 'Form unpublished',
        duration: 2000,
      });
    } catch (error) {
      console.error('Failed to update publish state:', error);
      // Revert the toggle if the API call failed
      setPublishToggle(publishToggle);
      
      toast({
        title: 'Failed to update',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Share</DialogTitle>
        </DialogHeader>
        
        <div className="flex items-center justify-between mt-2">
          <div className="flex items-center gap-2">
            <Switch
              checked={publishToggle}
              
              onCheckedChange={handlePublishToggle}
              disabled={isLoading}
            />
            <span className="text-sm ">
              {publishToggle ? 'Published' : 'Unpublished'}
            </span>
          </div>
        </div>
        
        {!publishToggle && (
          <div className="text-xs text-amber-600 mt-1">
            Recipients can't submit responses to unpublished forms
          </div>
        )}
        
        <div className="flex items-center space-x-2 mt-3">
          <input
            className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring "
            value={shareUrl}
            readOnly
          />
          <Button size="sm" className="px-2 h-9 bg-purple-600 hover:bg-purple-700 text-white font-medium" onClick={handleCopyLink}>
            {isCopied ? (
              <Check className="h-4 w-4" />
            ) : (
              <ClipboardCopy className="h-4 w-4" />
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
} 