import { useState, useEffect } from "react";
import { Plus, MessageCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { ChatUI } from "./ChatUI";

type Thread = {
  id: string;
  title: string;
  updatedAt: string;
  formId: string;
};

type FormResponse = {
  id: string;
  formId: string;
  createdAt: string;
};

type ChatThreadManagerProps = {
  formId: string;
  className?: string;
};

export function ChatThreadManager({ formId, className }: ChatThreadManagerProps) {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [selectedThread, setSelectedThread] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creatingThread, setCreatingThread] = useState(false);
  const [formResponses, setFormResponses] = useState<FormResponse[]>([]);

  // Get form responses and threads
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Get form responses for checking if any exist
        const response = await fetch(`/api/forms/${formId}/responses`);
        if (!response.ok) {
          throw new Error("Failed to fetch form responses");
        }
        const data = await response.json();
        setFormResponses(data);
        
        // Always try to fetch threads for this form
        await fetchThreads();
      } catch (error) {
        console.error("Error loading data:", error);
        setLoading(false);
      }
    };

    if (formId) {
      loadData();
    }
  }, [formId]);

  // Fetch threads for this form
  const fetchThreads = async () => {
    try {
      const response = await fetch(`/api/chat?formId=${formId}`);
      if (response.ok) {
        const data = await response.json();
        setThreads(data);
        
        // Auto-select the first thread if available
        if (data.length > 0 && !selectedThread) {
          setSelectedThread(data[0].id);
        }
      }
    } catch (error) {
      console.error("Failed to load threads:", error);
    } finally {
      setLoading(false);
    }
  };

  const createNewThread = async () => {
    setCreatingThread(true);
    try {
      console.log("Creating new thread for form ID:", formId);
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          formId: formId,
          title: "New Chat",
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response from server:", errorText);
        throw new Error(`Failed to create thread: ${response.status} ${errorText}`);
      }

      const newThread = await response.json();
      console.log("New thread created:", newThread);
      setThreads((prev) => [newThread, ...prev]);
      setSelectedThread(newThread.id);
    } catch (error: any) {
      console.error("Error creating new thread:", error);
      toast({
        title: "Error",
        description: `Failed to create a new chat thread: ${error?.message || "Unknown error"}`,
        variant: "destructive",
      });
    } finally {
      setCreatingThread(false);
    }
  };

  const updateThreadInList = (updatedThread: any) => {
    setThreads((prev) => 
      prev.map((thread) => 
        thread.id === updatedThread.id 
          ? { ...thread, title: updatedThread.title, updatedAt: updatedThread.updatedAt }
          : thread
      )
    );
  };

  return (
    <div className={cn("flex flex-col h-full rounded-xl bg-background/80 shadow-sm overflow-hidden", className)}>
      <div className="flex flex-1">
        {/* Thread list sidebar */}
        <div className="w-56 bg-muted/5 flex flex-col border-r">
          <Button
            variant="secondary"
            className="m-2 flex items-center text-xs w-[calc(100%-1rem)]"
            onClick={createNewThread}
            disabled={creatingThread}
          >
            {creatingThread ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Plus className="h-4 w-4 mr-2" />
            )}
            New Chat
          </Button>
          <Separator className="bg-border/50" />
          <div className="flex-1 overflow-auto">
            {loading ? (
              <div className="flex items-center justify-center h-24">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : formResponses.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                You can create a chat thread and ask questions about this form, even without submissions yet.
              </div>
            ) : threads.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No chat threads yet
              </div>
            ) : (
              <div className="py-2">
                {threads.map((thread) => (
                  <button
                    key={thread.id}
                    className={cn(
                      "w-full text-left px-3 py-2 text-sm flex items-center gap-2 hover:bg-muted/50",
                      selectedThread === thread.id && "bg-muted font-medium"
                    )}
                    onClick={() => setSelectedThread(thread.id)}
                  >
                    <MessageCircle className="h-4 w-4 flex-shrink-0" />
                    <div className="truncate flex-1">{thread.title}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 flex flex-col bg-background">
          {loading ? (
            <div className="flex h-full items-center justify-center text-center p-4">
              <div>
                <Loader2 className="h-12 w-12 mx-auto mb-2 text-muted-foreground animate-spin" />
                <h3 className="text-lg font-medium">Loading chat data...</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Getting your conversations ready
                </p>
              </div>
            </div>
          ) : selectedThread ? (
            <ChatUI threadId={selectedThread} className="border-0" onThreadUpdate={updateThreadInList} />
          ) : (
            <div className="flex h-full items-center justify-center text-center p-4">
              <div>
                {formResponses.length === 0 ? (
                  <>
                    <MessageCircle className="h-12 w-12 mx-auto mb-2 text-muted-foreground" />
                    <h3 className="text-lg font-medium">Ready to start chatting</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      Create a chat thread to start asking questions about this form
                    </p>
                  </>
                ) : (
                  <>
                    <MessageCircle className="h-12 w-12 mx-auto mb-2 text-muted-foreground" />
                    <h3 className="text-lg font-medium">No chat selected</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {threads.length > 0 ? "Select an existing chat or create a new one" : "Create a new chat to get started"}
                    </p>
                    <Button
                      variant="outline"
                      className="mt-4 bg-primary/10 hover:bg-primary/20 border-primary/20 text-primary hover:text-primary"
                      onClick={createNewThread}
                      disabled={creatingThread}
                    >
                      {creatingThread ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Plus className="h-4 w-4 mr-2" />
                      )}
                      New Chat
                    </Button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 