"use client"

import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2, UserCircle2, AlertTriangle, Download, Table as TableIcon } from "lucide-react";
import { useUser } from "@clerk/clerk-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "@/components/ui/table"
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Define the structure for our rich content
interface TextContentBlock {
  type: "text";
  text: string;
}

interface CSVContentBlock {
  type: "csv";
  data: string;
  description?: string;
}

// Legacy structure for backwards compatibility
interface StructuredContentText {
  type: "text";
  data: string;
}

interface StructuredContentTableData {
  headers: string[];
  rows: (string | number | boolean | null)[][];
}

interface StructuredContentTable {
  type: "table";
  data: StructuredContentTableData;
}

interface StructuredContentError {
    type: "error";
    data: string;
}

type StructuredContent = StructuredContentText | StructuredContentTable | StructuredContentError;
type ContentBlock = TextContentBlock | CSVContentBlock;

// Update Message type
type Message = {
  id: string;
  content: string | StructuredContent | ContentBlock | { content_blocks: ContentBlock[] }; // Support all possible formats
  role: "user" | "assistant";
  createdAt: string;
};

// Parse CSV data to a table structure
const parseCSV = (csvData: string): StructuredContentTableData => {
    if (!csvData?.trim()) {
        return { headers: [], rows: [] };
    }

    const lines = csvData.trim().split('\n');
    if (lines.length === 0) {
        return { headers: [], rows: [] };
    }

    // Parse headers and rows
    const headers = lines[0].split(',').map(h => h.trim());
    const rows = lines.slice(1).map(line => 
        line.split(',').map(cell => {
            const trimmed = cell.trim();
            // Try to convert to number if appropriate
            if (/^-?\d+(\.\d+)?$/.test(trimmed)) {
                return parseFloat(trimmed);
            }
            // Handle boolean values
            if (trimmed.toLowerCase() === 'true') return true;
            if (trimmed.toLowerCase() === 'false') return false;
            // Handle null values
            if (trimmed.toLowerCase() === 'null' || trimmed === '') return null;
            // Otherwise keep as string
            return trimmed;
        })
    );

    return { headers, rows };
};

const markdownComponents = {
  a: ({ href, children, ...props }: any) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-purple-600 underline hover:text-purple-800 transition-colors"
      {...props}
    >
      {children}
    </a>
  ),
  table: ({ children, ...props }: any) => (
    <div className="my-4 w-full max-w-[400px] rounded-md border bg-white">
      <div className="overflow-x-auto overflow-y-auto max-h-[250px]">
        <Table className="text-xs" {...props}>
          {children}
        </Table>
      </div>
    </div>
  ),
  thead: ({ children, ...props }: any) => (
    <TableHeader className="bg-gray-50 sticky top-0" {...props}>
      {children}
    </TableHeader>
  ),
  tbody: ({ children, ...props }: any) => (
    <TableBody className="bg-white" {...props}>
      {children}
    </TableBody>
  ),
  tr: ({ children, ...props }: any) => (
    <TableRow className="border-b border-gray-100" {...props}>
      {children}
    </TableRow>
  ),
  th: ({ children, ...props }: any) => (
    <TableHead className="font-medium px-1 py-1 text-xs whitespace-nowrap max-w-[80px] truncate" {...props}>
      {children}
    </TableHead>
  ),
  td: ({ children, ...props }: any) => (
    <TableCell className="px-1 py-1 text-xs whitespace-nowrap max-w-[80px] truncate" {...props}>
      {children}
    </TableCell>
  ),
};

// Helper to render content
const RenderMessageContent: React.FC<{ content: any; isAssistant?: boolean }> = ({ content, isAssistant }) => {
    // Handle the new content blocks format
    if (content && content.content_blocks && Array.isArray(content.content_blocks)) {
        return (
            <div className="space-y-4">
                {content.content_blocks.map((block: ContentBlock, i: number) => (
                    <RenderContentBlock key={i} block={block} isAssistant={isAssistant} />
                ))}
            </div>
        );
    }
    
    // Handle direct content block (should be rare)
    if (content && typeof content === 'object' && 'type' in content) {
        if (content.type === 'text' && 'text' in content) {
            return isAssistant ? (
                <div className="prose prose-sm dark:prose-invert">{React.createElement((ReactMarkdown as any), { components: markdownComponents, remarkPlugins: [remarkGfm] }, content.text)}</div>
            ) : (
                <p className="text-sm whitespace-pre-wrap">{content.text}</p>
            );
        }
        if (content.type === 'csv' && 'data' in content) {
            return <RenderCSVBlock csvBlock={content as CSVContentBlock} />;
        }
    }
    
    // Legacy format handling
    if (typeof content === 'string') {
        return isAssistant ? (
            <div className="prose prose-sm dark:prose-invert">{React.createElement((ReactMarkdown as any), { components: markdownComponents, remarkPlugins: [remarkGfm] }, content)}</div>
        ) : (
            <p className="text-sm whitespace-pre-wrap">{content}</p>
        );
    }
    
    // Legacy structured content
    if (content && typeof content === 'object') {
        if (content.type === "text" && 'data' in content) {
            return isAssistant ? (
                <div className="prose prose-sm dark:prose-invert">{React.createElement((ReactMarkdown as any), { components: markdownComponents, remarkPlugins: [remarkGfm] }, content.data)}</div>
            ) : (
                <p className="text-sm whitespace-pre-wrap">{content.data}</p>
            );
        }
        if (content.type === "table" && 'data' in content) {
            const { headers, rows } = content.data as StructuredContentTableData;
            return <RenderTableData headers={headers} rows={rows} />;
        }
        if (content.type === "error" && 'data' in content) {
            return (
                <div className="p-3 rounded-lg bg-red-100 border border-red-300 text-red-700 flex items-center">
                    <AlertTriangle className="h-5 w-5 mr-2 flex-shrink-0" />
                    <p className="text-sm">Error: {content.data}</p>
                </div>
            );
        }
    }
    
    // Fallback for unknown content format
    return <p className="text-sm whitespace-pre-wrap">[Unsupported content format]</p>;
};

// Render a specific content block
const RenderContentBlock: React.FC<{ block: ContentBlock; isAssistant?: boolean }> = ({ block, isAssistant }) => {
    switch (block.type) {
        case "text":
            return isAssistant ? (
                <div className="prose prose-sm dark:prose-invert">{React.createElement((ReactMarkdown as any), { components: markdownComponents, remarkPlugins: [remarkGfm] }, block.text)}</div>
            ) : (
                <p className="text-sm whitespace-pre-wrap">{block.text}</p>
            );
        case "csv":
            return <RenderCSVBlock csvBlock={block} />;
        default:
            return <p className="text-sm whitespace-pre-wrap">[Unsupported block type]</p>;
    }
};

// Render CSV data
const RenderCSVBlock: React.FC<{ csvBlock: CSVContentBlock }> = ({ csvBlock }) => {
    const { data, description } = csvBlock;
    const tableData = parseCSV(data);
    
    // Function to download CSV
    const downloadCSV = () => {
        const blob = new Blob([data], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'data.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };
    
    return (
        <div className="space-y-2 w-full max-w-[400px]">
            {description && (
                <div className="text-xs text-muted-foreground mb-1">{description}</div>
            )}
            <div className="rounded-md border border-border overflow-hidden bg-white">
                <div className="bg-muted/30 p-2 flex justify-between items-center">
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <TableIcon className="h-3.5 w-3.5" />
                        <span>Data Table</span>
                    </div>
                    <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-6 w-6" 
                        onClick={downloadCSV}
                        title="Download CSV"
                    >
                        <Download className="h-3.5 w-3.5" />
                    </Button>
                </div>
                <div className="overflow-x-auto overflow-y-auto max-h-[250px]">
                    <Table className="text-xs">
                        <TableHeader className="bg-gray-50 sticky top-0">
                            <TableRow>
                                {tableData.headers.map((header, idx) => (
                                    <TableHead key={idx} className="px-1 py-1 text-left font-medium text-gray-500 uppercase tracking-wider text-xs whitespace-nowrap max-w-[80px] truncate">
                                        {header}
                                    </TableHead>
                                ))}
                            </TableRow>
                        </TableHeader>
                        <TableBody className="bg-white">
                            {tableData.rows.map((row, rowIdx) => (
                                <TableRow key={rowIdx} className="border-b border-gray-100">
                                    {row.map((cell, cellIdx) => (
                                        <TableCell key={cellIdx} className="px-1 py-1 text-xs whitespace-nowrap max-w-[80px] truncate">
                                            {typeof cell === 'boolean' ? (cell ? 'Yes' : 'No') : (cell === null || cell === undefined ? '-' : String(cell))}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            </div>
        </div>
    );
};

// Render table data (used by both CSV and legacy table formats)
const RenderTableData: React.FC<{ headers: string[], rows: any[][] }> = ({ headers, rows }) => {
    return (
        <div className="w-full max-w-[400px]">
            <div className="overflow-x-auto overflow-y-auto max-h-[250px]">
                <Table className="text-xs">
                    <TableHeader className="bg-gray-50 sticky top-0">
                        <TableRow>
                            {headers.map((header, idx) => (
                                <TableHead key={idx} className="px-1 py-1 text-left font-medium text-gray-500 uppercase tracking-wider text-xs whitespace-nowrap max-w-[80px] truncate">
                                    {header}
                                </TableHead>
                            ))}
                        </TableRow>
                    </TableHeader>
                    <TableBody className="bg-white">
                        {rows.map((row, rowIdx) => (
                            <TableRow key={rowIdx} className="border-b border-gray-100">
                                {row.map((cell, cellIdx) => (
                                    <TableCell key={cellIdx} className="px-1 py-1 text-xs whitespace-nowrap max-w-[80px] truncate">
                                        {typeof cell === 'boolean' ? (cell ? 'Yes' : 'No') : (cell === null || cell === undefined ? '-' : String(cell))}
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
};

interface ChatUIProps {
  threadId: string;
  className?: string;
  onThreadUpdate?: (thread: any) => void;
}

export function ChatUI({ threadId, className, onThreadUpdate }: ChatUIProps) {
  const { user } = useUser();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [loadingMessages, setLoadingMessages] = useState(true);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchMessages = async () => {
      setLoadingMessages(true);
      try {
        const response = await fetch(`/api/chat/${threadId}/messages`);
        if (response.ok) {
          const data = await response.json();
          setMessages(data);
        }
      } catch (error) {
        console.error('Failed to fetch messages:', error);
      } finally {
        setLoadingMessages(false);
      }
    };

    if (threadId) {
      fetchMessages();
    }
  }, [threadId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setIsLoading(true);

    // Optimistically add user message
    const tempUserMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: userMessage,
      createdAt: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      const response = await fetch(`/api/chat/${threadId}/agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();
      // Expecting data.userMessage and data.assistantMessage from the agent endpoint
      setMessages(prev => [
        ...prev.slice(0, -1),
        ...(data.userMessage ? [data.userMessage] : []),
        ...(data.assistantMessage ? [data.assistantMessage] : [])
      ]);

      if (onThreadUpdate && data.thread?.id) {
        onThreadUpdate(data.thread);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove optimistic message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn("flex flex-col h-full bg-white", className)}>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loadingMessages ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-4 space-y-4">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
              <span className="text-sm font-semibold text-purple-600">Flux</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Flux</p>
              <p className="text-sm text-gray-500 mt-1">Ask me anything about your form submissions!</p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3 max-w-[90%]",
                  message.role === "assistant" ? "mr-auto" : "ml-auto flex-row-reverse"
                )}
              >
                <div className="flex flex-col gap-1">
                  {message.role === "assistant" && (
                    <div className="text-xs font-medium text-gray-600 px-1">Flux</div>
                  )}
                  <div
                    className={cn(
                      "rounded-2xl px-4 py-2 text-sm",
                      message.role === "assistant"
                        ? "bg-gray-100 text-gray-900"
                        : "bg-purple-600 text-white"
                    )}
                  >
                    <RenderMessageContent content={message.content} isAssistant={message.role === "assistant"} />
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3 max-w-[90%] animate-pulse">
                <div className="flex flex-col gap-1">
                  <div className="text-xs font-medium text-gray-600 px-1">Flux</div>
                  <div className="rounded-2xl px-4 py-2 text-sm bg-gray-100 text-gray-900">
                    <span className="opacity-70">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your submissions..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button 
            type="submit" 
            size="icon"
            disabled={isLoading || !input.trim()}
            className={cn(
              "bg-purple-600 hover:bg-purple-700 text-white",
              isLoading && "opacity-50 cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </form>
    </div>
  );
} 