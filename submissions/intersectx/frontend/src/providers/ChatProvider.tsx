import { createContext, useContext, useState, useRef, useEffect } from 'react';
import type { ReactNode } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../lib/api-client';
import { API_ENDPOINTS } from '../lib/api-types';
import type { ChatThreadWithMessages, MessageResponse, CreateThreadResponse, DeleteThreadResponse } from '../lib/api-types';

// Types based on API.md
export interface Thread {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  lastMessage?: {
    content: string;
    sender: 'user' | 'assistant';
    timestamp: string;
  };
  createdBy?: string;
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
}

export interface Reference {
  title: string;
  url: string;
}

export interface MessageMetadata {
  attachments?: Attachment[];
  references?: Reference[];
  associatedDocuments?: {
    id: string;
    name: string;
    insights: string[];
  }[];
  tools?: any[];
  formatted_tool_calls?: any[];
  citations?: any[];
  messages?: {
    role: string;
    content: string;
  }[];
  model?: string;
}

export interface Message {
  id: string;
  type: 'human' | 'ai' | 'tool';
  content: string;
  timestamp?: string;
  metadata?: MessageMetadata;
  user_id?: string;
  user_name?: string;
  iframe_url?: string[];
}

interface ChatContextType {
  messages: Message[];
  threads: Thread[];
  currentThreadId: string | null;
  isLoading: boolean;
  error: Error | null;
  hideToolCalls: boolean;
  submit: (content: string, attachmentIds?: string[]) => void;
  submitWithStream: (content: string, attachmentIds?: string[]) => void;
  // Special function for suggestion buttons to ensure human messages appear
  submitSuggestion: (content: string) => void;
  stop: () => void;
  createNewThread: () => Promise<string | null>;
  switchThread: (threadId: string) => void;
  deleteThread: (threadId: string) => Promise<boolean>;
  uploadFiles: (files: File[]) => Promise<Attachment[]>;
  setHideToolCalls: (hide: boolean) => void;
  clearCurrentThread: () => void;
  // Function to reset thread fetch flag when needed
  resetThreadFetchFlag: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}

interface ChatProviderProps {
  children: ReactNode;
}

export function ChatProvider({ children }: ChatProviderProps) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [hideToolCalls, setHideToolCalls] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const activeOperationThreadIdRef = useRef<string | null>(null);
  // Ref to track if we've already fetched threads initially
  const hasInitialFetchRef = useRef(false);

  // Fetch threads on mount and only when needed
  useEffect(() => {
    // Only fetch threads if user is logged in and we haven't fetched them yet
    if (user && !hasInitialFetchRef.current) {
      console.log('Initial thread fetch triggered');
      // Set flag to true to prevent duplicate fetches
      hasInitialFetchRef.current = true;
      
      // Load threads when user changes or on initial mount
      fetchThreads().catch(error => {
        console.error('Error loading threads:', error);
      });
    }
  }, [user]);
  
  // Function to reset thread fetch flag - can be called when needed
  const resetThreadFetchFlag = () => {
    hasInitialFetchRef.current = false;
  };

  // Fetch all threads
  const fetchThreads = async () => {
    try {
      // Add user_id to the request if available
      const endpoint = user?.email ? `${API_ENDPOINTS.THREADS}?user_id=${encodeURIComponent(user.email)}` : API_ENDPOINTS.THREADS;
      const threadsData = await apiClient.get<ChatThreadWithMessages[]>(endpoint);
      
      // Convert API threads to our internal format
      const formattedThreads: Thread[] = threadsData.map((thread) => ({
        id: thread.id,
        title: thread.id.substring(0, 8) || `Chat ${new Date(thread.created_at || '').toLocaleDateString()}`,
        createdAt: thread.created_at || new Date().toISOString(),
        updatedAt: thread.updated_at || new Date().toISOString(),
        messageCount: thread.message_count || thread.messages?.length || 0,
        lastMessage: thread.last_message ? {
          content: thread.last_message.content || '',
          sender: thread.last_message.sender as 'user' | 'assistant',
          timestamp: thread.last_message.timestamp || new Date().toISOString()
        } : thread.messages?.length > 0 ? {
          content: thread.messages[thread.messages.length - 1].content,
          sender: thread.messages[thread.messages.length - 1].sender,
          timestamp: thread.messages[thread.messages.length - 1].timestamp
        } : undefined,
        createdBy: thread.created_by
      }));
      
      setThreads(formattedThreads);
    } catch (err) {
      console.error("Error fetching threads:", err);
      setError(err instanceof Error ? err : new Error('Failed to fetch threads'));
    }
  };

  // Create a new chat thread
  const createNewThread = async (): Promise<string | null> => {
    try {
      // Start loading but don't clear messages yet to prevent UI flicker
      setIsLoading(true);
      
      console.log('Creating new thread via API');
      // Add user_id to the request if available
      const endpoint = user?.email ? `${API_ENDPOINTS.THREADS}?user_id=${encodeURIComponent(user.email)}` : API_ENDPOINTS.THREADS;
      // Pass an empty object as the data parameter since the post method requires it
      const response = await apiClient.post<CreateThreadResponse>(endpoint, {});
      
      // Extract the thread ID from the response
      const newThreadId = response.thread_id;
      if (!newThreadId) {
        throw new Error('Failed to create thread - no ID returned');
      }
      
      // Create a basic thread object to show in the UI immediately
      const newThread: Thread = {
        id: newThreadId,
        title: newThreadId.substring(0, 8),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        messageCount: 0
      };
      
      // Batch state updates to reduce renders
      // First update the threads list
      setThreads(prev => [newThread, ...prev]);
      // Then set current thread ID
      setCurrentThreadId(newThreadId);
      // Finally clear messages in a single render cycle
      setMessages([]);
      
      console.log(`New thread created with ID: ${newThreadId}`);
      return newThreadId;
    } catch (err) {
      console.error("Error creating new thread:", err);
      setError(err instanceof Error ? err : new Error('Failed to create new thread'));
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Delete a thread
  const deleteThread = async (threadId: string): Promise<boolean> => {
    try {
      // Store the current threads before deletion for optimistic updates
      const currentThreads = [...threads];
      
      // Optimistically update UI first
      setThreads(prev => prev.filter(thread => thread.id !== threadId));
      
      // If current thread was deleted, reset current thread and clear messages
      if (currentThreadId === threadId) {
        setCurrentThreadId(null);
        setMessages([]);
      }
      
      // Add user_id to the request if available
      const endpoint = user?.email ? `${API_ENDPOINTS.THREAD(threadId)}?user_id=${encodeURIComponent(user.email)}` : API_ENDPOINTS.THREAD(threadId);
      const { success } = await apiClient.delete<DeleteThreadResponse>(endpoint);
      
      if (success) {
        console.log(`Thread ${threadId} deleted successfully`);
        return true;
      } else {
        // If deletion failed, restore the threads
        console.error(`Failed to delete thread ${threadId}`);
        setThreads(currentThreads);
        return false;
      }
    } catch (err) {
      console.error("Error deleting thread:", err);
      setError(err instanceof Error ? err : new Error('Failed to delete thread'));
      return false;
    }
  };

  // Track the last loaded thread to prevent redundant API calls
  const lastLoadedThreadRef = useRef<string | null>(null);
  // Track if we're currently loading a thread to prevent concurrent loads
  const isLoadingThreadRef = useRef<boolean>(false);
  // Track the last time a thread was loaded to implement debouncing
  const lastLoadTimeRef = useRef<Record<string, number>>({});
  // Minimum time between thread load attempts (in milliseconds)
  const THREAD_LOAD_DEBOUNCE_MS = 1000;
  
  // Switch to an existing thread with optimized loading
  const switchThread = async (threadId: string) => {
    // Don't do anything if we're trying to switch to the current thread and it's already loaded
    if (threadId === currentThreadId && lastLoadedThreadRef.current === threadId) {
      console.log(`Thread ${threadId} is already active and loaded`);
      return;
    }
    
    // Check if we're already loading a thread
    if (isLoadingThreadRef.current) {
      console.log(`Already loading a thread, ignoring request to load ${threadId}`);
      return;
    }
    
    // Implement debouncing - prevent rapid consecutive calls
    const now = Date.now();
    const lastLoadTime = lastLoadTimeRef.current[threadId] || 0;
    if (now - lastLoadTime < THREAD_LOAD_DEBOUNCE_MS) {
      console.log(`Debouncing thread load for ${threadId}, last loaded ${now - lastLoadTime}ms ago`);
      return;
    }
    
    // Mark that we're loading a thread and update last load time
    isLoadingThreadRef.current = true;
    lastLoadTimeRef.current[threadId] = now;
    
    try {
      // Set loading state and clear any previous errors
      setIsLoading(true);
      setError(null);
      
      // If switching to a different thread, immediately update thread ID and clear messages
      if (threadId !== currentThreadId) {
        setCurrentThreadId(threadId);
        setMessages([]);
      }
      
      // Fetch thread data from API
      let threadData: ChatThreadWithMessages;
      try {
        // Add user_id to the request if available
        const endpoint = user?.email ? `${API_ENDPOINTS.THREAD(threadId)}?user_id=${encodeURIComponent(user.email)}` : API_ENDPOINTS.THREAD(threadId);
        threadData = await apiClient.get<ChatThreadWithMessages>(endpoint);
      } catch (err: any) {
        console.error(`Error fetching thread ${threadId}:`, err);
        
        // If it's a 404 error, this might be a new thread that doesn't exist on the server yet
        // Instead of showing an error, set up an empty thread experience
        if (err.status === 404) {
          console.log(`Thread ${threadId} not found on server, treating as new empty thread`);
          
          // Set empty messages array to trigger the default welcome page
          setMessages([]);
          
          // Mark thread as loaded to prevent repeated attempts
          lastLoadedThreadRef.current = threadId;
          return;
        } else {
          // For other errors, show the error message
          setError(new Error(`Error loading thread: ${err.message || 'Unknown error'}`));
          return;
        }
      }
      
      // Convert API messages to app format
      const apiMessages = threadData.messages || [];
      const formattedMessages: Message[] = apiMessages.map(msg => ({
        id: msg.id || uuidv4(),
        type: msg.sender === 'user' ? 'human' : msg.sender === 'assistant' ? 'ai' : 'tool',
        content: msg.content || '',
        timestamp: msg.timestamp || new Date().toISOString(),
        iframe_url: msg.iframe_url,
        metadata: msg.metadata,
        user_id: msg.user_id,
        user_name: msg.user_name
      }));
      
      // Update threads state
      setThreads(prev => 
        prev.map(thread => 
          thread.id === threadId
            ? {
                ...thread,
                title: threadData.id.substring(0, 8) || thread.title,
                createdAt: threadData.created_at || thread.createdAt,
                updatedAt: threadData.updated_at || thread.updatedAt,
                messageCount: formattedMessages.length,
                createdBy: threadData.created_by || thread.createdBy
              }
            : thread
        )
      );
      
      // Update messages state
      const finalMessages: Message[] = formattedMessages.length > 0 
        ? formattedMessages 
        : [];
      
      setMessages(finalMessages);
      
      // Mark this thread as successfully loaded
      lastLoadedThreadRef.current = threadId;
    } catch (error) {
      console.error(`Unexpected error in switchThread for ${threadId}:`, error);
      setError(new Error('An unexpected error occurred while loading the thread.'));
    } finally {
      setIsLoading(false);
      isLoadingThreadRef.current = false;
    }
  };

  // Submit a message to the current thread (non-streaming)
  const submit = async (content: string, attachmentIds?: string[]) => {
    if (!content.trim()) return;
    
    // First, immediately add the user message to the UI for better responsiveness
    const userMessage: Message = {
      id: uuidv4(),
      type: 'human',
      content,
      timestamp: new Date().toISOString(),
      user_id: user?.email,
      user_name: user ? `${user.first_name} ${user.last_name}`.trim() : undefined,
      metadata: attachmentIds && attachmentIds.length > 0 ? {
        attachments: attachmentIds.map(id => ({ id, name: '', type: '', size: 0, url: '' }))
      } : undefined
    };
    
    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    let threadId = currentThreadId;
    
    try {
      // If no current thread, create one first
      if (!threadId) {
        console.log('No thread ID found - creating new thread');
        // Store the user message before creating a new thread
        const tempUserMessage = userMessage;
        threadId = await createNewThread();
        
        if (!threadId) {
          throw new Error('Failed to create thread - threadId is null');
        }
        
        console.log(`New thread created with ID: ${threadId}`);
        
        // Re-add the user message after thread creation
        // This is needed because createNewThread resets the messages array
        setMessages([tempUserMessage]);
      }
      
      // Make API call to send message and get response
      console.log(`Sending message to thread ${threadId} via API endpoint: ${API_ENDPOINTS.MESSAGES(threadId)}`);
      
      const requestPayload = {
        content: content,
        attachments: attachmentIds ? attachmentIds.map(id => ({ id })) : undefined,
        user_id: user?.email,
        user_name: user ? `${user.first_name} ${user.last_name}`.trim() : undefined
      };
      
      const data = await apiClient.post<MessageResponse>(
        API_ENDPOINTS.MESSAGES(threadId), 
        requestPayload
      );
      
      // Add AI response to messages
      const aiMessage: Message = {
        id: data.id || uuidv4(),
        type: 'ai',
        content: data.content || 'I received your message but couldn\'t generate a response.',
        timestamp: data.timestamp || new Date().toISOString(),
        iframe_url: data.iframe_url,
        metadata: data.metadata,
        user_id: data.user_id,
        user_name: data.user_name
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Update thread
      setThreads(prev => prev.map(thread => {
        if (thread.id === threadId) {
          return {
            ...thread,
            messageCount: thread.messageCount + 2, // +2 for user and AI message
            updatedAt: new Date().toISOString(),
            lastMessage: {
              content: aiMessage.content.substring(0, 50) + (aiMessage.content.length > 50 ? '...' : ''),
              sender: 'assistant',
              timestamp: new Date().toISOString()
            }
          };
        }
        return thread;
      }));
    } catch (err) {
      console.error(`Error submitting message:`, err);
      setError(err instanceof Error ? err : new Error('Failed to submit message'));
      
      // Fallback error message
      const errorMessage = `Error connecting to the backend. Please check your backend server.`;
      
      const aiMessage: Message = {
        id: uuidv4(),
        type: 'ai',
        content: errorMessage,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Submit a message to the current thread (with streaming)
  const submitWithStream = async (content: string, attachmentIds?: string[]) => {
    if (!content.trim()) return;
    
    // First, create and add the user message immediately for better UI responsiveness
    const userMessage: Message = {
      id: uuidv4(),
      type: 'human',
      content,
      timestamp: new Date().toISOString(),
      user_id: user?.email,
      user_name: user ? `${user.first_name} ${user.last_name}`.trim() : undefined,
      metadata: attachmentIds && attachmentIds.length > 0 ? {
        attachments: attachmentIds.map(id => ({ id, name: '', type: '', size: 0, url: '' }))
      } : undefined
    };
    
    // Add user message to UI immediately and ensure it persists
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    let threadId = currentThreadId;
    
    // If no current thread, create one first
    if (!threadId) {
      try {
        // Store the user message before creating a new thread
        const tempUserMessage = userMessage;
        threadId = await createNewThread();
        if (!threadId) throw new Error("Failed to create thread");
        
        // Re-add the user message after thread creation
        // This is needed because createNewThread resets the messages array
        setMessages([tempUserMessage]);
        
        // Add a placeholder for the loading indicator to appear for the first message
        const placeholderId = uuidv4();
        setMessages(prev => [
          ...prev,
          { 
            id: placeholderId, 
            type: 'ai', 
            content: '', 
            timestamp: new Date().toISOString() 
          }
        ]);
      } catch (err) {
        console.error("Failed to create thread:", err);
        setIsLoading(false);
        return;
      }
    }
    
    // Cancel any previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create new AbortController
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;
    
    try {
      const requestPayload = {
        content: content,
        attachments: attachmentIds ? attachmentIds.map(id => ({ id })) : undefined,
        user_id: user?.email,
        user_name: user ? `${user.first_name} ${user.last_name}`.trim() : undefined
      };
      
      // Create a placeholder message for the streaming response
      const placeholderId = uuidv4();
      setMessages(prev => [
        ...prev, 
        { 
          id: placeholderId, 
          type: 'ai' as const, // Use const assertion for type safety
          content: '',
          timestamp: new Date().toISOString()
        }
      ]);
      
      // Stream using a single POST request with stream=true
      const token = localStorage.getItem('token');
      const streamUrl = `${import.meta.env.VITE_BACKEND_URL || 'https://api.intersectx.com'}${API_ENDPOINTS.MESSAGES(threadId)}?stream=true`;
      
      try {
        const response = await fetch(streamUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          body: JSON.stringify(requestPayload),
          signal // Attach the abort signal
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        // Process the stream manually
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let streamedContent = '';
        let buffer = '';
        
        if (!reader) {
          throw new Error('Stream reader not available');
        }
        
        // Process the stream
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            setIsLoading(false);
            abortControllerRef.current = null;
            break;
          }
          
          // Decode the chunk and add to buffer
          buffer += decoder.decode(value, { stream: true });
          
          // Process each line in the buffer
          let lineIndex;
          while ((lineIndex = buffer.indexOf('\n')) !== -1) {
            const line = buffer.slice(0, lineIndex).trim();
            buffer = buffer.slice(lineIndex + 1);
            
            if (!line) continue; // Skip empty lines
            
            // Handle SSE format lines starting with "data: "
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              
              if (data === '[DONE]') {
                // Stream completed - only update thread state once at the end
                setIsLoading(false);
                abortControllerRef.current = null;
                
                // Update the thread after streaming is complete
                setThreads(prev => prev.map(thread => {
                  if (thread.id === threadId) {
                    return {
                      ...thread,
                      messageCount: thread.messageCount + 2, // +2 for user and AI message
                      updatedAt: new Date().toISOString(),
                      lastMessage: {
                        content: streamedContent.substring(0, 50) + (streamedContent.length > 50 ? '...' : ''),
                        sender: 'assistant',
                        timestamp: new Date().toISOString()
                      }
                    };
                  }
                  return thread;
                }));
                
                break;
              }
              
              try {
                const chunk = JSON.parse(data);
                if (chunk.content !== null) {
                  // Update local variable first
                  streamedContent += chunk.content;
                  
                  // Throttle updates to prevent too many re-renders
                  setMessages(prev => {
                    // Find the message to update
                    const updatedMessages = prev.map(msg => 
                      msg.id === placeholderId 
                        ? { 
                            ...msg, 
                            content: streamedContent,
                            // Include iframe_url if present in the chunk
                            ...(chunk.iframe_url ? { iframe_url: chunk.iframe_url } : {})
                          } 
                        : msg
                    );
                    return updatedMessages;
                  });
                }
              } catch (err) {
                console.error('Error parsing stream chunk:', err, data);
              }
            }
          }
        }
      } catch (err) {
        console.error("Error with streaming message:", err);
        
        // Don't show error if it was intentionally aborted
        if (err instanceof Error && err.name === 'AbortError') {
          console.log('Request was aborted');
          return;
        }
        
        setError(err instanceof Error ? err : new Error('Failed to stream message'));
        
        // Add error message
        const errorMessage = `Error connecting to the backend. Please check your backend server.`;
        
        // Update the placeholder with the error message
        setMessages(prev => {
          return prev.map(msg => 
            msg.id === placeholderId 
              ? { ...msg, content: errorMessage } 
              : msg
          );
        });
      }
      
      setIsLoading(false);
      abortControllerRef.current = null;
    } catch (err) {
      console.error("Error in submitWithStream:", err);
      setIsLoading(false);
      
      // Show error message to user
      if (!(err instanceof Error && err.name === 'AbortError')) {
        setError(err instanceof Error ? err : new Error('Failed to process message'));
        
        // Add error message to the UI
        setMessages(prev => [
          ...prev, 
          {
            id: uuidv4(),
            type: 'ai' as const,
            content: 'Error connecting to the backend. Please check your backend server.',
            timestamp: new Date().toISOString()
          }
        ]);
      }
    }
  };

  // Upload files
  const uploadFiles = async (files: File[]): Promise<Attachment[]> => {
    try {
      setIsLoading(true);
      
      // Use proper typing for the options parameter
      const options: { threadId?: string } = currentThreadId ? { threadId: currentThreadId } : {};
      // Use a default company name since we don't have company in the user object
      const companyName = 'venture-insights';
      const data = await apiClient.uploadFiles<{ attachments: Attachment[] }>(files, companyName, options);
      
      return data.attachments;
    } catch (err) {
      console.error("Error uploading files:", err);
      setError(err instanceof Error ? err : new Error('Failed to upload files'));
      
      // Return mock attachments if upload fails
      return files.map(file => ({
        id: uuidv4(),
        name: file.name,
        type: file.type,
        size: file.size,
        url: URL.createObjectURL(file) // Create local URL for the file
      }));
    } finally {
      setIsLoading(false);
    }
  };

  // Stop ongoing conversation
  const stop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
  };

  // Clear current thread
  const clearCurrentThread = () => {
    console.log('[ChatProvider.clearCurrentThread] Clearing current thread selection.');
    setCurrentThreadId(null);
    setMessages([]);
    setError(null);
    activeOperationThreadIdRef.current = null; // Also clear active operation
  };

  // Special function for suggestion buttons to ensure human messages always appear
  const submitSuggestion = async (content: string) => {
    if (!content.trim()) return;
    
    // First create a unique ID for the message
    const messageId = uuidv4();
    
    // Create the user message object
    const userMessage: Message = {
      id: messageId,
      type: 'human',
      content,
      timestamp: new Date().toISOString(),
      user_id: user?.email,
      user_name: user ? `${user.first_name} ${user.last_name}`.trim() : undefined
    };
    
    // Force immediate UI update with the human message before any async operations
    // This ensures the message appears right away
    setMessages(prev => [...prev, userMessage]);
    
    // Add a small delay to ensure the UI updates before continuing
    await new Promise(resolve => setTimeout(resolve, 10));
    
    // Then set loading state
    setIsLoading(true);
    
    try {
      // Ensure we have a thread to submit to
      let threadId = currentThreadId;
      if (!threadId) {
        // Create a new thread if needed
        threadId = await createNewThread();
        if (!threadId) {
          throw new Error('Failed to create thread - threadId is null');
        }
        
        // Re-add the user message after thread creation since createNewThread resets messages
        setMessages([userMessage]);
      }
      
      // Make API call to send message and get response
      const requestPayload = {
        content: content,
        user_id: user?.email,
        user_name: user ? `${user.first_name} ${user.last_name}`.trim() : undefined
      };
      
      const data = await apiClient.post<MessageResponse>(
        API_ENDPOINTS.MESSAGES(threadId), 
        requestPayload
      );
      
      // Add AI response to messages
      const aiMessage: Message = {
        id: data.id || uuidv4(),
        type: 'ai',
        content: data.content || 'I received your message but couldn\'t generate a response.',
        timestamp: data.timestamp || new Date().toISOString(),
        iframe_url: data.iframe_url,
        metadata: data.metadata,
        user_id: data.user_id,
        user_name: data.user_name
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Update thread
      setThreads(prev => prev.map(thread => {
        if (thread.id === threadId) {
          return {
            ...thread,
            messageCount: thread.messageCount + 2, // +2 for user and AI message
            updatedAt: new Date().toISOString(),
            lastMessage: {
              content: aiMessage.content.substring(0, 50) + (aiMessage.content.length > 50 ? '...' : ''),
              sender: 'assistant',
              timestamp: new Date().toISOString()
            }
          };
        }
        return thread;
      }));
    } catch (err) {
      console.error(`Error in submitSuggestion:`, err);
      setError(err instanceof Error ? err : new Error('Failed to submit suggestion'));
      
      // Fallback error message
      const errorMessage = `Error connecting to the backend. Please check your backend server.`;
      
      const aiMessage: Message = {
        id: uuidv4(),
        type: 'ai',
        content: errorMessage,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        threads,
        currentThreadId,
        isLoading,
        error,
        hideToolCalls,
        submit,
        submitWithStream,
        submitSuggestion,
        stop,
        createNewThread,
        switchThread,
        deleteThread,
        uploadFiles,
        setHideToolCalls,
        clearCurrentThread,
        resetThreadFetchFlag
      }}
    >
      {children}
    </ChatContext.Provider>
  );
} 