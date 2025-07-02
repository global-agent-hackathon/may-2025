"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PlusIcon, MessagesSquare } from "lucide-react";
import { ChatThread } from "@/components/features/chat/chat-thread";
import { useRouter } from "next/navigation";

interface ChatSectionProps {
  formId: string;
  existingThreads: any[];
}

export function ChatSection({ formId, existingThreads = [] }: ChatSectionProps) {
  const [threads, setThreads] = useState(existingThreads);
  const [selectedThread, setSelectedThread] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    if (threads.length > 0) {
      setSelectedThread(threads[0].id);
    }
  }, [threads]);

  const createNewThread = async () => {
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          formId,
          title: "New Chat",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create thread");
      }

      const newThread = await response.json();
      setThreads((prev) => [newThread, ...prev]);
      setSelectedThread(newThread.id);
      router.refresh();
    } catch (error) {
      console.error("Error creating thread:", error);
    }
  };

  return (
    <div className="flex flex-col space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Chat</h2>
        <Button onClick={createNewThread} size="sm">
          <PlusIcon className="h-4 w-4 mr-2" />
          New Thread
        </Button>
      </div>

      {threads.length === 0 ? (
        <div className="text-center py-8">
          <MessagesSquare className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="font-medium mb-2">No chat threads yet</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Start a new chat to ask questions about this submission
          </p>
          <Button onClick={createNewThread}>
            <PlusIcon className="h-4 w-4 mr-2" />
            New Thread
          </Button>
        </div>
      ) : (
        <Tabs value={selectedThread || undefined} className="w-full">
          <TabsList className="w-full justify-start">
            {threads.map((thread) => (
              <TabsTrigger
                key={thread.id}
                value={thread.id}
                onClick={() => setSelectedThread(thread.id)}
              >
                {thread.title}
              </TabsTrigger>
            ))}
          </TabsList>
          {threads.map((thread) => (
            <TabsContent key={thread.id} value={thread.id}>
              <ChatThread threadId={thread.id} />
            </TabsContent>
          ))}
        </Tabs>
      )}
    </div>
  );
} 