"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { AIFormBuilder } from "@/components/forms/ai-form-builder";
import { Sparkles } from "lucide-react";
import { FormCreateModal } from "@/components/forms/form-create-modal";
import { useRouter } from "next/navigation";

export default function FormsPage() {
  const router = useRouter();
  const [showFormCreate, setShowFormCreate] = useState(false);
  const [showAIFormBuilder, setShowAIFormBuilder] = useState(false);

  const handleCreateForm = () => {
    setShowFormCreate(true);
  };

  const handleCreateAIForm = () => {
    setShowAIFormBuilder(true);
  };
  
  const handleFormCreated = (formId: string) => {
    // Refresh the page to show the new form
    router.refresh();
    // Navigate to the form editor
    router.push(`/dashboard/forms/${formId}`);
  };

  return (
    <div className="container mx-auto py-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Forms</h1>
        <div className="flex items-center gap-2">
          <Button onClick={handleCreateForm}>
            Create Form
          </Button>
          <Button variant="outline" onClick={handleCreateAIForm} className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            AI Builder
          </Button>
        </div>
      </div>

      {/* Form creation modal */}
      <FormCreateModal
        isOpen={showFormCreate}
        onOpenChange={setShowFormCreate}
        onSuccess={handleFormCreated}
      />
      
      {/* AI form builder modal */}
      <AIFormBuilder
        isOpen={showAIFormBuilder}
        onOpenChange={setShowAIFormBuilder}
      />
    </div>
  );
} 