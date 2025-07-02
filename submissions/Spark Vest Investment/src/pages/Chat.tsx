import { useState, useRef, KeyboardEvent } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import { MessageSquare, Send, Bot, ChevronDown, BotIcon } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { AssistantType, Message } from '@/lib/types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Markdown from 'react-markdown'
// import remarkGfm from 'remark-gfm';

const presetPrompts = [
  "What's the current market sentiment for Bitcoin?",
  "Explain the concept of DeFi in simple terms",
  "What are the key factors affecting crypto prices?",
  "How do I create a diversified crypto portfolio?",
  "What are the risks of cryptocurrency investing?",
];

const Chat = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [assistantType, setAssistantType] = useState<AssistantType>('general');
  const { user } = useAuth();
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const server_url = import.meta.env.VITE_PUBLIC_SERVER_URL;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleAssistantChange = (value: string) => {
    setAssistantType(value as AssistantType);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(query);
    }
  };

  const callChatAPI = async (prompt: string): Promise<string> => {
    try {
      const endpoint = assistantType === 'general'
        ? `${server_url}chat`
        : `${server_url}agent`;

      const response = await fetch(`${endpoint}?query=${encodeURIComponent(prompt)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Handle the case where response is in {question, answer} format
      if (data.answer) {
        return data.answer;
      }
      // Handle the case where response is in {response} format
      else if (data.response) {
        return data.response;
      }
      // Fallback for unknown formats - try to get any string content
      else if (typeof data === 'object') {
        return JSON.stringify(data);
      }

      else if (data.response === "error") {
        return "Couldn't parse the response. Please try again.";
      }

      return "Sorry, I couldn't process your request.";
    } catch (error) {
      console.error('API Error:', error);
      return error instanceof Error
        ? `Error: ${error.message}`
        : "An unexpected error occurred. Please try again.";
    }
  };

  const handleSubmit = async (promptText: string) => {
    if (!promptText.trim() || !user || loading) return;

    setLoading(true);
    try {
      // Add user message immediately for better UX
      setMessages(prevMessages => [...prevMessages, { query: promptText.trim(), response: "..." }]);
      setQuery('');

      // Call the appropriate API based on selected assistant type
      const aiResponse = await callChatAPI(promptText.trim());

      // Update messages with the actual response (replacing the "...")
      setMessages(prevMessages => {
        const newMessages = [...prevMessages];
        // Replace the last message's response
        if (newMessages.length > 0) {
          newMessages[newMessages.length - 1] = {
            query: promptText.trim(),
            response: aiResponse
          };
        }
        return newMessages;
      });

      // Store the interaction in the database
      const { error } = await supabase
        .from('ai_queries')
        .insert([
          {
            user_id: user.id,
            query: promptText.trim(),
            response: aiResponse,
            assistant_type: assistantType
          }
        ]);

      if (error) throw error;

      // Scroll to the bottom of the messages
      setTimeout(scrollToBottom, 100);
    } catch (error) {
      console.error('Error:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to process your request. Please try again."
      });
      // Remove the last message with "..." if there was an error
      setMessages(prevMessages => {
        if (prevMessages.length > 0 && prevMessages[prevMessages.length - 1].response === "...") {
          return prevMessages.slice(0, -1);
        }
        return prevMessages;
      });
    } finally {
      setLoading(false);
      // Focus back on the input field
      inputRef.current?.focus();
    }
  };

  return (
    <div className="container max-w-4xl mx-auto py-8">
      <Card className="glass-panel">
        <CardHeader>
          <div className="flex flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Bot className="h-6 w-6 text-primary" />
              <CardTitle>AI Investment Assistant</CardTitle>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Assistant Type:</span>
              <Select value={assistantType} onValueChange={handleAssistantChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select Assistant" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="general">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-6" />
                AI Assistant
              </div>
            </SelectItem>
            <SelectItem value="financial">
              <div className="flex items-center gap-2">
                <BotIcon className="h-4 w-4" />
                Financial Analyst
              </div>
            </SelectItem>
          </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            Ask me anything about cryptocurrency, market analysis, or investment strategies.
          </p>

          <div className="h-[500px] overflow-y-auto mb-4 space-y-4 pr-2">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground p-8">
                <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No messages yet. Start by asking a question or selecting a preset prompt above.</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className="space-y-2">
                  <div className="bg-primary/10 p-3 rounded-lg">
                    <p className="text-sm whitespace-pre-wrap">{msg.query}</p>
                  </div>
                  <div className="bg-muted p-3 rounded-lg">
                    <p className="text-sm whitespace-pre-wrap">
                      {msg.response === "..." ? (
                        <span className="inline-flex items-center">
                          <span className="animate-pulse">Thinking</span>
                          <span className="animate-pulse delay-100">.</span>
                          <span className="animate-pulse delay-200">.</span>
                          <span className="animate-pulse delay-300">.</span>
                        </span>
                      ) : (
                        <Markdown>{msg.response}</Markdown>
                      )}
                    </p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit(query);
            }}
            className="flex gap-2"
          >
            <Input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask ${assistantType === 'general' ? 'anything' : 'about investments'}...`}
              disabled={loading}
              className="flex-1"
            />
            <div className="flex-shrink-0 relative">
              <Button
                type="submit"
                disabled={loading}
                className="relative"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </form>
          <p className="text-xs text-muted-foreground mt-2">
            Press Enter to send, Shift+Enter for a new line
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Chat;
