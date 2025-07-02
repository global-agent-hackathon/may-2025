"use client";

import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { SendIcon, Code } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  createdAt: string;
}

interface ChatThreadProps {
  threadId: string;
}

export function ChatThread({ threadId }: ChatThreadProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [sqlQuery, setSqlQuery] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Fetch messages on thread change
  useEffect(() => {
    const fetchMessages = async () => {
      try {
        setIsFetching(true);
        const response = await fetch(`/api/chat/${threadId}/messages`);
        if (!response.ok) {
          throw new Error("Failed to fetch messages");
        }
        
        const data = await response.json();
        setMessages(data);
      } catch (error) {
        console.error("Error fetching messages:", error);
      } finally {
        setIsFetching(false);
      }
    };

    if (threadId) {
      fetchMessages();
    }
  }, [threadId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "inherit";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [input]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;
    
    try {
      setIsLoading(true);
      
      // Send message to API
      const response = await fetch(`/api/chat/${threadId}/agent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }
      
      const data = await response.json();
      
      // Store SQL query if provided
      if (data.sourceQuery) {
        setSqlQuery(data.sourceQuery);
      }
      
      // Reset input and update messages
      setInput("");
      setMessages((prev) => [
        ...prev,
        data.userMessage,
        data.assistantMessage,
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle key press in textarea
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <ScrollArea className="flex-1 p-4">
        {isFetching ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-pulse text-muted-foreground">Loading messages...</div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex justify-center items-center h-full">
            <div className="text-center text-muted-foreground">
              <p>No messages yet.</p>
              <p className="text-sm">Start the conversation by asking a question about this submission.</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex items-start gap-3 rounded-lg p-4",
                  message.role === "user"
                    ? "ml-auto max-w-[80%] bg-primary text-primary-foreground"
                    : "max-w-[80%] bg-muted"
                )}
              >
                {message.role === "assistant" && (
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>AI</AvatarFallback>
                  </Avatar>
                )}
                <div className="flex-1 overflow-hidden">
                  <div className="prose dark:prose-invert prose-sm">
                    {message.content}
                  </div>
                </div>
                {message.role === "user" && (
                  <Avatar className="h-8 w-8 ml-2">
                    <AvatarFallback>U</AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </ScrollArea>

      {/* Input area */}
      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Textarea
            ref={textareaRef}
            placeholder="Ask a question about this submission..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            className="flex-1 resize-none min-h-[40px] max-h-[200px]"
            disabled={isLoading}
          />
          <div className="flex flex-col gap-2">
            <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
              <SendIcon className="h-4 w-4" />
            </Button>
            
            {sqlQuery && (
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline" size="icon" title="View SQL Query">
                    <Code className="h-4 w-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>SQL Query</DialogTitle>
                  </DialogHeader>
                  <div className="bg-muted rounded-md p-4 overflow-auto">
                    <pre className="text-sm whitespace-pre-wrap">{sqlQuery}</pre>
                  </div>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </form>
        
        {isLoading && (
          <div className="text-sm text-muted-foreground mt-2">
            Generating response...
          </div>
        )}
      </div>
    </div>
  );
} 