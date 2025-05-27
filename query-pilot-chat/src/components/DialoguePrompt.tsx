import React from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "./ui/alert-dialog";

interface DialoguePromptProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const DialoguePrompt: React.FC<DialoguePromptProps> = ({
  isOpen,
  onConfirm,
  onCancel,
}) => {
  return (
    <AlertDialog open={isOpen}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Practice Dialogue</AlertDialogTitle>
          <AlertDialogDescription>
            Would you like to practice a conversation using these words?
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={onCancel}>No, thanks</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}>Yes, let's practice</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};