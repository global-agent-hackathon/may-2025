import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatContext } from '../../providers/ChatProvider';
import { ThreadHistory } from './ThreadHistory';
import { ChatInput } from './ChatInput';
import { MessageBubble } from './MessageBubble';
import { ChartRenderer } from './ChartRenderer';
import { cn } from '../../lib/utils';
import { Switch } from '../ui/Switch';
import { Label } from '../ui/Label';
import { PaperClipIcon } from '@heroicons/react/24/outline';

// Use simple icon implementations that won't overlap
function CollapseIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
      <path d="M9 3v18"/>
      <path d="m16 15-3-3 3-3"/>
    </svg>
  );
}

function ExpandIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
      <path d="M9 3v18"/>
      <path d="m14 9 3 3-3 3"/>
    </svg>
  );
}

// Custom Plus icon from SVGrepo - https://www.svgrepo.com/svg/347816/plus
function CustomPlusIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.49 2 2 6.49 2 12C2 17.51 6.49 22 12 22C17.51 22 22 17.51 22 12C22 6.49 17.51 2 12 2ZM16 12.75H12.75V16C12.75 16.41 12.41 16.75 12 16.75C11.59 16.75 11.25 16.41 11.25 16V12.75H8C7.59 12.75 7.25 12.41 7.25 12C7.25 11.59 7.59 11.25 8 11.25H11.25V8C11.25 7.59 11.59 7.25 12 7.25C12.41 7.25 12.75 7.59 12.75 8V11.25H16C16.41 11.25 16.75 11.59 16.75 12C16.75 12.41 16.41 12.75 16 12.75Z" fill="currentColor"/>
    </svg>
  );
}

export function ChatContainer() {
  const { 
    messages, 
    isLoading, 
    submit, 
    stop, 
    hideToolCalls, 
    setHideToolCalls,
    uploadFiles,
    currentThreadId
  } = useChatContext();
  
  // Track if user has scrolled up (for auto-scroll feature)
  
  const navigate = useNavigate();
  // Default sidebar state is open on larger screens, closed on mobile
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth >= 768);
  // State for tracking when a new thread is being created
  const [isCreatingThread, setIsCreatingThread] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Track if we should auto-scroll
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  
  // Handle window resize for responsive sidebar
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768 && sidebarOpen) {
        setSidebarOpen(false);
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [sidebarOpen]);
  
  // Detect if user has scrolled up (to disable auto-scroll)
  useEffect(() => {
    const handleScroll = () => {
      if (!messagesContainerRef.current) return;
      
      const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
      const isScrolledToBottom = scrollHeight - scrollTop - clientHeight < 50;
      setShouldAutoScroll(isScrolledToBottom);
    };
    
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);
  
  const scrollToBottom = () => {
    if (shouldAutoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Scroll to bottom when messages change or when loading state changes
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, shouldAutoScroll]);
  
  // Initial scroll to bottom when component mounts
  useEffect(() => {
    scrollToBottom();
  }, []);

  const handleSendMessage = (content: string) => {
    // Don't do anything if content is empty
    if (!content.trim()) return;
    
    // Update URL if this is the first message in a new thread
    if (currentThreadId && window.location.pathname === '/intersectx-chat') {
      navigate(`/intersectx-chat/t/${currentThreadId}`, { replace: true });
    }
    
    // Set auto-scroll to true to ensure we scroll to latest messages
    setShouldAutoScroll(true);
    
    // Submit the message to the API
    submit(content);
    
    // Force scroll to bottom after a slight delay to allow UI to update
    setTimeout(() => {
      scrollToBottom();
      // Scroll again after another delay to ensure it catches any late updates
      setTimeout(scrollToBottom, 500);
    }, 100);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    
    try {
      // Convert FileList to File array
      const files = Array.from(e.target.files);
      
      // Upload the files
      await uploadFiles(files);
      
      // Clear the input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  const handleCreateNewThread = async () => {
    try {
      // Disable multiple rapid clicks
      if (isCreatingThread) return;
      setIsCreatingThread(true);
      
      // Simply navigate to the base chat URL
      // The IntersectXChatPage component will handle the thread creation and navigation
      navigate('/intersectx-chat', { replace: true });
    } catch (error) {
      console.error('Error navigating to new thread:', error);
      // Handle error gracefully
    } finally {
      setIsCreatingThread(false);
    }
  };
  
  return (
    <div className="flex h-[calc(100vh-4rem)] w-full overflow-hidden fixed inset-0 top-16">
      {/* Sidebar for thread history */}
      <div
        className={cn(
          "h-full bg-white border-r border-gray-200 flex flex-col transition-all duration-300",
          sidebarOpen 
            ? "w-full md:w-80 translate-x-0" 
            : "w-0 -translate-x-full md:translate-x-0"
        )}
      >
        {/* Sidebar header with close button */}
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <button
            onClick={toggleSidebar}
            className="text-purple hover:text-purple-dark flex items-center justify-center overflow-hidden"
            aria-label="Close sidebar"
          >
            <span className="block"><CollapseIcon /></span>
          </button>
          
          {/* New Chat button (plus icon) - only shown in sidebar header */}
          <button
            onClick={handleCreateNewThread}
            className="text-purple hover:text-purple-dark flex items-center justify-center transition-colors overflow-hidden"
            aria-label="New chat"
            disabled={isCreatingThread}
          >
            <CustomPlusIcon />
          </button>
        </div>
        <ThreadHistory />
      </div>
      
      {/* Main chat area */}
      <div className="flex-1 flex flex-col overflow-hidden relative h-full w-full">
        {/* Header with toggle button for sidebar */}
        <div className="sticky top-0 z-10 border-b border-[#e7edf4] p-3 flex items-center">
          {!sidebarOpen && (
            <button
              onClick={toggleSidebar}
              className="p-1.5 rounded-md hover:bg-purple-light/10 text-purple flex items-center justify-center transition-colors"
              aria-label="Open sidebar"
            >
              <span className="block"><ExpandIcon /></span>
            </button>
          )}
        </div>
        {/* Messages container with scrolling */}
        <div 
          ref={messagesContainerRef} 
          className="flex-1 overflow-y-auto p-4 md:px-6 lg:px-8 pb-6 scrollbar-hide"
        >
          {messages.length > 0 ? (
            <div className="flex flex-col space-y-4 min-h-full">
              {/* Show all messages */}
              {/* Message bubbles and charts */}
              {/* Add debugging information for visibility */}
              
              {/* Messages are filtered to hide tool calls if enabled */}
              
              {messages.filter(m => !hideToolCalls || m.type !== 'tool').map((message, index) => (
                <React.Fragment key={message.id || index}>
                  <MessageBubble
                    message={message}
                    isLoading={isLoading && index === messages.length - 1 && !message.content}
                  />
                  
                  {/* Render charts as separate components if they exist */}
                  {message.type === 'ai' && message.iframe_url && message.iframe_url.length > 0 && (
                    <div className="w-[80%]">
                      <ChartRenderer iframeUrls={message.iframe_url} />
                    </div>
                  )}
                </React.Fragment>
              ))}
              
              {/* Always show loading indicator when isLoading is true */}
              {isLoading && (
                <div className="flex w-full mb-4 justify-start">
                  <div className="max-w-[80%] rounded-lg p-3 bg-white shadow-sm border border-gray-200">
                    <div className="flex items-center space-x-2">
                      <span className="text-purple-dark text-sm">IntersectX Chat is thinking</span>
                      <div className="flex space-x-1">
                        <div className="animate-pulse h-1.5 w-1.5 rounded-full bg-purple-light"></div>
                        <div className="animate-pulse delay-100 h-1.5 w-1.5 rounded-full bg-purple-light"></div>
                        <div className="animate-pulse delay-200 h-1.5 w-1.5 rounded-full bg-purple-light"></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} className="h-4" />
            </div>
          ) : isLoading ? (
            <div className="flex items-center justify-center min-h-[calc(100vh-16rem)]">
              <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-purple mb-3"></div>
                <span className="text-sm text-purple-dark">Loading conversation...</span>
              </div>
            </div>
          ) : (
            <div className="min-h-[calc(100vh-16rem)] flex flex-col items-center justify-center">
              <h2 className="font-medium text-primary mb-4">IntersectX Chat</h2>
              <p className="text-primary max-w-md text-center mb-6">
                Explore market trends and company analysis for valuable strategic insights.
              </p>
              <div className="flex items-center justify-center">
                <div className="flex flex-col gap-4 w-full max-w-md px-4">
                  <button
                    className="p-3 border border-gray-200 rounded-xl bg-white hover:bg-purple-light/5 hover:border-purple-light transition-colors text-center shadow-sm"
                    onClick={() => {
                      handleSendMessage("Tell me about Apple's revenue");
                    }}
                  >
                    <span className="font-medium block text-primary">Revenue Analysis 📊</span>
                  </button>
                  <button
                    className="p-3 border border-gray-200 rounded-xl bg-white hover:bg-purple-light/5 hover:border-purple-light transition-colors text-center shadow-sm"
                    onClick={() => {
                      handleSendMessage("Competitive analysis of Apple and Microsoft");
                    }}
                  >
                    <span className="font-medium block text-primary">Competitive Analysis 🆚 </span>
                  </button>
                  <button
                    className="p-3 border border-gray-200 rounded-xl bg-white hover:bg-purple-light/5 hover:border-purple-light transition-colors text-center shadow-sm"
                    onClick={() => {
                      handleSendMessage("Tell me about Apple's executive team");
                    }}
                  >
                    <span className="font-medium block text-primary">Team Analysis 👥</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Fixed footer with chat input */}
        <div className="p-4 md:px-6 lg:px-8 border-t border-gray-200 mt-auto bg-white">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200">
            <ChatInput 
              onSend={handleSendMessage} 
              isLoading={isLoading}
              onCancel={stop}
              placeholder="Ask anything..."
            />
          </div>
          <div className="text-xs text-center text-secondary mt-1.5">*IntersectX Chat can make mistakes. Verify important information.</div>
          
          {/* Control options */}
          <div className="flex items-center justify-between px-2 py-2 mt-2">
            <div className="flex items-center space-x-2">
              <Switch
                id="hide-tool-calls"
                checked={hideToolCalls}
                onCheckedChange={setHideToolCalls}
              />
              <Label htmlFor="hide-tool-calls" className="text-sm text-secondary">
                Hide Tool Calls
              </Label>
            </div>
            
            {/* File upload button */}
            <div>
              <input 
                type="file" 
                className="hidden" 
                ref={fileInputRef}
                onChange={handleFileUpload}
                multiple
                accept=".pdf,.doc,.docx"
              />
              <button 
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-1 text-sm text-secondary hover:text-purple p-1 rounded hover:bg-purple-light/10 transition-colors"
              >
                <PaperClipIcon className="h-5 w-5" />
                <span>Upload Files</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}