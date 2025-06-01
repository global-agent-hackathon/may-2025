/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Sparkles, AlertCircle, Brain, TrendingUp, Lightbulb, Clock, Target, Zap } from "lucide-react";
import { trackFormInteraction, extractContextualKeywords, searchMemoriesWithContext, getEnhancedFormContext } from "@/lib/memory"
import { useUser } from "@clerk/nextjs"
import { useMemory } from "@/hooks/useMemory";
import { MemorySmartSuggestions } from './MemorySmartSuggestions';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "@/hooks/use-toast";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { getDbUserId } from "@/lib/auth-service";

// Form schema
const formBuilderSchema = z.object({
  prompt: z.string().min(3, "Please enter a description for your form"),
});

type FormBuilderValues = z.infer<typeof formBuilderSchema>;

interface AIFormBuilderProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  workspaceId?: string;
  existingForm?: {
    id: string;
    title: string;
    description?: string;
    schema: any; // This will be the array of fields
  } | null;
  onEditComplete?: (formId?: string) => void; // Callback for when an edit is successfully submitted
}

// You might already have a more detailed Field interface from your FormData type
// For now, a simple one for the example generator:
interface BasicField {
  id: string;
  label?: string; // Label might be optional or named differently in your actual schema
  required?: boolean;
  // Add other properties if your example generator logic uses them
}

export function AIFormBuilder({
  isOpen,
  onOpenChange,
  workspaceId,
  existingForm,
  onEditComplete,
}: AIFormBuilderProps) {
  const router = useRouter();
  const { user } = useUser()
  const { searchMemories, getFormHistory } = useMemory();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [memoryEnhanced, setMemoryEnhanced] = useState(false);
  const [fluxEnhanced, setFluxEnhanced] = useState(false);
  const [memoryInsights, setMemoryInsights] = useState<any>(null);
  const [loadingFluxEnhancement, setLoadingFluxEnhancement] = useState(false);

  const isEditing = !!existingForm;

  const form = useForm<FormBuilderValues>({
    resolver: zodResolver(formBuilderSchema),
    defaultValues: {
      prompt: isEditing ? `I want to change my form titled "${existingForm?.title}".\n\nSpecific changes I want to make:\n` : "",
    },
  });

  // Watch the form prompt value
  const prompt = form.watch("prompt");

  // Remove automatic memory loading - only load when user requests it
  const enhancePromptWithMemory = async () => {
    if (!user?.id || !prompt.trim()) {
      toast({
        title: "Add a prompt first",
        description: "Please describe your form before enhancing with memory.",
        variant: "destructive"
      });
      return;
    }
    
    console.log("[MEMORY_ENHANCE] Starting memory enhancement process with prompt:", prompt.substring(0, 50) + "...");
    setLoadingInsights(true);
    try {
      console.log("[MEMORY_ENHANCE] Making API request to /api/ai/enhance-prompt-memory");
      const response = await fetch('/api/ai/enhance-prompt-memory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          // No need to include userId - backend will use the authenticated user
        }),
      });

      console.log("[MEMORY_ENHANCE] API response status:", response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("[MEMORY_ENHANCE] API error response:", errorText);
        throw new Error('Failed to enhance prompt with memory');
      }

      const data = await response.json();
      console.log("[MEMORY_ENHANCE] API response data:", data);
      
      if (data.enhancedPrompt && data.enhancedPrompt !== prompt.trim()) {
        console.log("[MEMORY_ENHANCE] Setting enhanced prompt in form");
        form.setValue("prompt", data.enhancedPrompt);
        setMemoryEnhanced(true);
        
        // Set memory insights for display
        if (data.memoryInsights) {
          console.log("[MEMORY_ENHANCE] Setting memory insights:", data.memoryInsights);
          setMemoryInsights({
            memoryInsights: data.memoryInsights,
            successfulPatterns: data.successfulPatterns || [],
            source: data.source
          });
        }
        
        toast({
          title: "Prompt Enhanced with Memory!",
          description: `Applied ${data.improvements?.length || 0} memory-based improvements from your successful forms.`,
        });
      } else if (data.source === "no_memory") {
        console.log("[MEMORY_ENHANCE] No memory patterns available");
        toast({
          title: "No memory patterns available",
          description: "Create a few more forms to build up successful patterns for enhancement.",
        });
      } else {
        console.log("[MEMORY_ENHANCE] Prompt already optimized");
        toast({
          title: "Prompt already optimized",
          description: "Your prompt already incorporates the best patterns from your form history.",
        });
      }
    } catch (error) {
      console.error("[MEMORY_ENHANCE] Error enhancing prompt with memory:", error);
      toast({
        title: "Memory enhancement failed",
        description: "Could not enhance prompt with memory. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoadingInsights(false);
      console.log("[MEMORY_ENHANCE] Enhancement process completed");
    }
  };

  const enhancePromptWithFlux = async () => {
    if (!user?.id || !prompt.trim()) {
      toast({
        title: "Add a prompt first",
        description: "Please describe your form before enhancing with Flux.",
        variant: "destructive"
      });
      return;
    }

    setLoadingFluxEnhancement(true);
    try {
      // Check if the API requires a database user ID instead of a Clerk ID
      // The enhance-prompt endpoint appears to use Clerk ID directly (not DB ID)
      const response = await fetch('/api/ai/enhance-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          userId: user.id, // Using Clerk ID directly here
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to enhance prompt');
      }

      const data = await response.json();
      
      if (data.enhancedPrompt && data.enhancedPrompt !== prompt.trim()) {
        form.setValue("prompt", data.enhancedPrompt);
        setFluxEnhanced(true);
        
        toast({
          title: "Prompt Enhanced with Flux!",
          description: `Applied ${data.improvements?.length || 0} improvements to make your prompt more specific and actionable.`,
        });
      } else {
        toast({
          title: "Prompt already optimized",
          description: "Your prompt is already well-structured for form generation.",
        });
      }
    } catch (error) {
      console.error("Failed to enhance prompt with Flux:", error);
      toast({
        title: "Enhancement failed",
        description: "Could not enhance prompt with Flux. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoadingFluxEnhancement(false);
    }
  };

  const generateEditingExamples = () => {
    if (!existingForm || !existingForm.schema || existingForm.schema.length === 0) {
      return [
        "Add a new text field for 'Comments'.",
        "Make the first field required.",
        "Remove the last field.",
      ];
    }

    const examples = [];
    const fields: BasicField[] = existingForm.schema as BasicField[];

    if (fields[0]?.label) {
      examples.push(`Change the label of the field "${fields[0].label}" to "New ${fields[0].label}".`);
    }

    const fieldToToggle = fields.find((f: BasicField) => f.label); 
    if (fieldToToggle?.label) {
      examples.push(`Make the field "${fieldToToggle.label}" ${fieldToToggle.required ? 'optional' : 'required'}.`);
    }
    
    if (fields.length > 0 && fields[0]?.label) {
        examples.push(`Add a new text field for "Notes" after the "${fields[0].label}" field.`);
    }

    if (fields.length > 1 && fields[fields.length -1]?.label) {
        examples.push(`Remove the field "${fields[fields.length -1].label}".`);
    } else if (fields[0]?.label) {
        examples.push(`Remove the field "${fields[0].label}".`);
    }

    return examples.length > 0 ? examples.slice(0, 4) : ["Add a new field called 'Feedback Rating' with options: Good, Average, Poor."];
  };

  const placeholderText = isEditing 
    ? `Describe the changes you want to make. For example: "Add a field for job title after the name field" or "Make the email field optional."`
    : "Describe the form you want to create. For example: Create a customer feedback form for our new product.";

  const examplePrompts = isEditing
    ? generateEditingExamples()
    : [
        "Create a customer feedback form for our new product",
        "Make a job application form for a software engineering position", 
        "Build an event registration form for our upcoming workshop",
        "Design a simple contact form",
      ];

  const setExamplePrompt = (promptText: string) => {
    const currentPrompt = form.getValues().prompt;
    form.setValue("prompt", isEditing ? `${currentPrompt}${promptText}\n` : promptText);
  };

  const handleSuggestionApply = (suggestion: string) => {
    const currentPrompt = form.getValues().prompt;
    const newPrompt = currentPrompt + (currentPrompt ? '. ' : '') + suggestion;
    form.setValue("prompt", newPrompt);
  };

  async function onSubmit(values: FormBuilderValues) {
    setIsLoading(true);
    setError(null);

    try {
      // Get enhanced memory context using contextual keywords
      let memoryContext = "";
      if (user?.id && !isEditing) {
        try {
          // Extract keywords from the prompt for better context search
          const keywords = extractContextualKeywords(values.prompt);
          console.log("Extracted keywords:", keywords);
          
          // Get enhanced context based on similar successful forms
          memoryContext = await getEnhancedFormContext(user.id, values.prompt);
          
          // Also get specific examples of similar forms
          const contextMemories = await searchMemoriesWithContext(user.id, values.prompt, 3, "form_interaction");
          if (contextMemories?.memories?.length) {
            const examples = contextMemories.memories
              .filter(m => m.metadata?.ai_form_analytics?.success_score >= 7)
              .map(m => `Successful example: ${m.memory}`)
              .join('. ');
            
            if (examples) {
              memoryContext += ` ${examples}`;
            }
          }
          
          console.log("Memory context generated:", memoryContext.slice(0, 200) + "...");
        } catch (e) {
          console.warn("Failed to get memory context:", e);
        }
      }

      const aiResponse = await fetch("/api/ai/form-builder", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: values.prompt,
          workspaceId: workspaceId,
          memoryContext: memoryContext, // Pass enhanced memory context to AI
          existingFormSchema: existingForm ? {
            title: existingForm.title,
            description: existingForm.description,
            fields: existingForm.schema
          } : undefined,
        }),
      });

      if (!aiResponse.ok) {
        const errorData = await aiResponse.json();
        throw new Error(errorData.error || "Failed to get AI suggestions");
      }

      const aiData = await aiResponse.json();
      console.log("[AIFormBuilder] Data received from AI API:", JSON.stringify(aiData, null, 2));
      
      let submissionResponse;
      if (existingForm) {
        console.log("[AIFormBuilder] Updating form ID:", existingForm.id, "with AI fields:", JSON.stringify(aiData.fields, null, 2));
        submissionResponse = await fetch(`/api/forms/${existingForm.id}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: aiData.title,
            description: aiData.description,
            fields: aiData.fields,
          }),
        });
      } else {
        console.log("[AIFormBuilder] Creating new form with AI fields:", JSON.stringify(aiData.fields, null, 2));
        submissionResponse = await fetch(
          workspaceId ? `/api/workspace/${workspaceId}/forms` : "/api/forms",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              title: aiData.title,
              description: aiData.description,
              workspaceId: workspaceId,
              schema: aiData.fields,
            }),
          }
        );
      }

      if (!submissionResponse.ok) {
        const errorData = await submissionResponse.json();
        throw new Error(errorData.error || (existingForm ? "Failed to update form" : "Failed to save form"));
      }

      const finalFormData = await submissionResponse.json();

      // Enhanced memory tracking with success metrics
      if (user?.id) {
        try {
          const aiFormAnalytics = {
            creation_method: "ai",
            prompt_length: values.prompt.length,
            generated_field_count: aiData.fields.length,
            generated_field_types: aiData.fields.map((f: any) => f.type),
            has_ai_fields: aiData.fields.some((f: any) => f.is_ai_field),
            ai_field_count: aiData.fields.filter((f: any) => f.is_ai_field).length,
            is_edit: !!existingForm,
            workspace_id: workspaceId,
            generation_timestamp: new Date().toISOString(),
            prompt_complexity_score: values.prompt.split(' ').length,
            title_generated: aiData.title !== (existingForm?.title || ""),
            description_generated: aiData.description !== (existingForm?.description || ""),
            used_memory_context: !!memoryContext,
            memory_context_length: memoryContext.length,
            success_score: aiData.fields.length >= 3 ? 10 : aiData.fields.length * 3 // Simple success metric
          };

          await trackFormInteraction(
            user.id,
            finalFormData.id,
            aiData.title,
            existingForm ? "edited" : "created",
            {
              ai_form_analytics: aiFormAnalytics,
              original_prompt: values.prompt.substring(0, 200),
              memory_enhanced: true
            }
          );
        } catch (memoryError) {
          console.warn("Failed to track AI form creation memory:", memoryError);
        }
      }

      console.log("[AIFormBuilder] Form saved successfully:", finalFormData.id);

      toast({
        title: isEditing ? "Form updated!" : "Form created!",
        description: `Your ${isEditing ? 'updated' : 'new'} form "${aiData.title}" is ready.`,
      });

      onOpenChange(false);

      if (isEditing && onEditComplete) {
        onEditComplete();
      } else {
        router.push(`/dashboard/forms/${finalFormData.id}`);
      }
    } catch (error) {
      console.error("[AIFormBuilder] Error:", error);
      setError(error instanceof Error ? error.message : "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Brain className="mr-2 h-5 w-5 text-purple-600" />
            {isEditing ? "Edit Form with AI" : "Create Form with AI"}
            {memoryInsights && (
              <Badge variant="secondary" className="ml-2">
                <Sparkles className="h-3 w-3 mr-1" />
                Memory-Enhanced
              </Badge>
            )}
          </DialogTitle>
          <DialogDescription>
            {isEditing 
              ? "Describe the changes for your existing form. Our AI will suggest modifications."
              : "Describe the form you want to create. Our AI will generate it for you with smart suggestions from memory."}
          </DialogDescription>
        </DialogHeader>

        {/* Single Column Layout */}
        <div className="space-y-4">
          {/* Memory Insights Panel */}
          {memoryInsights && (
            <Card className="bg-gradient-to-r from-purple-50 to-purple-50 border-purple-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center">
                  <Brain className="h-4 w-4 mr-2 text-purple-600" />
                  Memory Enhancement Applied
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {memoryInsights.memoryInsights && (
                  <div className="p-3 bg-white rounded-lg border">
                    <div className="text-sm font-medium mb-2">Memory Insights:</div>
                    <div className="text-xs text-muted-foreground">
                      {memoryInsights.memoryInsights}
                    </div>
                  </div>
                )}

                {memoryInsights.successfulPatterns?.length > 0 && (
                  <div>
                    <div className="text-xs font-medium mb-2">Applied Successful Patterns:</div>
                    <div className="flex flex-wrap gap-1">
                      {memoryInsights.successfulPatterns.slice(0, 3).map((pattern: string, index: number) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          Pattern {index + 1}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="text-center">
                  <Badge variant="outline" className="text-xs">
                    Enhanced from {memoryInsights.source === "memory_agent" ? "Memory Agent" : "Memory Patterns"}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          )}

          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Label htmlFor="prompt">
                {isEditing ? 'How would you like to modify this form?' : 'Describe your form'}
              </Label>
              <Textarea
                id="prompt"
                placeholder={placeholderText}
                {...form.register("prompt")}
                className="min-h-[120px] mt-2"
                disabled={isLoading}
              />
              <div className="flex justify-between items-center mt-2">
                <div className="text-xs text-muted-foreground">
                  {prompt.length} characters
                </div>
                {memoryInsights && (
                  <Badge variant="outline" className="text-xs">
                    Memory Enhanced
                  </Badge>
                )}
              </div>
            </div>

            {/* Enhancement Buttons */}
            {prompt.trim().length > 10 && (
              <div className="grid grid-cols-2 gap-3">
                {/* Memory Enhancement Button */}
                {!memoryEnhanced && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={enhancePromptWithMemory}
                    disabled={loadingInsights}
                    className="border-purple-200 text-purple-700 hover:bg-purple-50"
                  >
                    {loadingInsights ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Enhancing...
                      </>
                    ) : (
                      <>
                        <Brain className="mr-2 h-4 w-4" />
                        Enhance with Memory
                      </>
                    )}
                  </Button>
                )}
                
                {/* Flux Enhancement Button */}
                {!fluxEnhanced && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={enhancePromptWithFlux}
                    disabled={loadingFluxEnhancement}
                    className="border-blue-200 text-blue-700 hover:bg-blue-50"
                  >
                    {loadingFluxEnhancement ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Enhancing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Enhance with Flux
                      </>
                    )}
                  </Button>
                )}
                
                {/* Show enhanced badges when both are enhanced */}
                {memoryEnhanced && fluxEnhanced && (
                  <div className="col-span-2 flex justify-center">
                    <Badge variant="secondary" className="text-xs">
                      Enhanced with Memory + Flux
                    </Badge>
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-start">
                <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <Button type="submit" disabled={!prompt.trim() || isLoading} className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {isEditing ? "Updating Form..." : "Generating Form..."}
                </>
              ) : (
                <>
                  <Zap className="mr-2 h-4 w-4" />
                  {isEditing ? "Update Form" : "Generate Form"}
                  {(memoryEnhanced || fluxEnhanced) && (
                    <Badge variant="secondary" className="ml-2 text-xs">
                      {memoryEnhanced && fluxEnhanced ? "Memory + Flux Enhanced" : 
                       memoryEnhanced ? "Memory Enhanced" : "Flux Enhanced"}
                    </Badge>
                  )}
                </>
              )}
            </Button>

            {/* Example Prompts */}
            {!isEditing && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm flex items-center">
                    <Lightbulb className="h-4 w-4 mr-2" />
                    Example Prompts
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {examplePrompts.slice(0, 3).map((example, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => form.setValue("prompt", example)}
                      className="w-full text-left p-2 text-xs bg-gray-50 hover:bg-gray-100 rounded border transition-colors"
                    >
                      {example}
                    </button>
                  ))}
                </CardContent>
              </Card>
            )}
          </form>
        </div>
      </DialogContent>
    </Dialog>
  );
} 