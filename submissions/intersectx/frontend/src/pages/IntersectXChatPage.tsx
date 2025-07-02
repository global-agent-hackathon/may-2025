import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ChatContainer } from '../components/chat/ChatContainer';
import { useChatContext } from '../providers/ChatProvider';
import { v4 as uuidv4 } from 'uuid';

export default function IntersectXChatPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { threadId } = useParams<{ threadId: string }>();
  const { switchThread, currentThreadId, messages, clearCurrentThread, createNewThread, resetThreadFetchFlag } = useChatContext();
  const [threadLoaded, setThreadLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [redirectInProgress, setRedirectInProgress] = useState(false);
  
  // Refs to prevent redundant API calls
  const isLoadingRef = useRef(false);
  const lastLoadedThreadIdRef = useRef<string | null>(null);
  const initialLoadCompletedRef = useRef(false);
  const threadCreationTimeRef = useRef<number>(0);
  // Debounce time in milliseconds to prevent multiple thread creations
  const THREAD_CREATION_DEBOUNCE_MS = 2000;

  // Function to create a new thread and navigate to it
  const createAndNavigateToNewThread = async () => {
    // Check if we're already redirecting
    if (redirectInProgress) return;
    
    // Implement debouncing to prevent multiple rapid thread creations
    const now = Date.now();
    const lastCreationTime = threadCreationTimeRef.current;
    if (now - lastCreationTime < THREAD_CREATION_DEBOUNCE_MS) {
      console.log(`Debouncing thread creation, last created ${now - lastCreationTime}ms ago`);
      return;
    }
    
    // Update the last creation time
    threadCreationTimeRef.current = now;
    setRedirectInProgress(true);
    
    try {
      console.log('Starting thread creation process...');
      
      // Reset refs to ensure we load the new thread
      lastLoadedThreadIdRef.current = null;
      initialLoadCompletedRef.current = false;
      setThreadLoaded(false);
      
      // Reset thread fetch flag to ensure we have the latest threads
      // This is important when threads have been deleted
      resetThreadFetchFlag();
      
      // Create a new thread via the API
      const newThreadId = await createNewThread();
      if (newThreadId) {
        console.log('Created new thread with ID:', newThreadId);
        navigate(`/intersectx-chat/t/${newThreadId}`, { replace: true });
      } else {
        // Fallback to UUID if API thread creation fails
        const fallbackThreadId = uuidv4();
        console.log('Falling back to UUID thread:', fallbackThreadId);
        navigate(`/intersectx-chat/t/${fallbackThreadId}`, { replace: true });
      }
    } catch (error) {
      console.error('Error during thread creation:', error);
      // Fallback to UUID if there's an error
      const fallbackThreadId = uuidv4();
      navigate(`/intersectx-chat/t/${fallbackThreadId}`, { replace: true });
    } finally {
      setRedirectInProgress(false);
    }
  };
  
  // Redirect to a new thread if accessing /intersectx-chat directly
  // Use a ref to track if we've already handled this path to prevent multiple redirects
  const hasHandledPathRef = useRef<string | null>(null);
  
  useEffect(() => {
    // Only proceed if we're on the base chat URL and not already redirecting
    if (location.pathname === '/intersectx-chat' && !redirectInProgress) {
      // Check if we've already handled this exact path in this session
      if (hasHandledPathRef.current === location.pathname + location.search) {
        console.log('Already handled this path, skipping redirect');
        return;
      }
      
      // Mark this path as handled
      hasHandledPathRef.current = location.pathname + location.search;
      console.log('Handling new path:', location.pathname);
      
      // Create and navigate to a new thread
      createAndNavigateToNewThread();
    }
  }, [location.pathname, location.search, redirectInProgress]);

  // Log info for debugging
  console.log('IntersectXChatPage - Render. URL threadId:', threadId, 'Context currentThreadId:', currentThreadId, 'Messages:', messages.length, 'Loaded:', threadLoaded, 'Loading:', loading);

  // Effect to handle thread ID changes and clear thread when needed
  useEffect(() => {
    // Only reset states if the threadId changes to a different value than what we've already loaded
    if (threadId !== lastLoadedThreadIdRef.current) {
      console.log('IntersectXChatPage - URL threadId changed to:', threadId, '. Resetting local load states.');
      setThreadLoaded(false);
      setLoadError(null);
    }

    // If threadId from URL is now undefined (e.g., navigated to /intersectx-chat/)
    // and there was a currentThreadId in the context, clear the context's thread.
    if (!threadId && currentThreadId) {
      console.log('IntersectXChatPage - URL threadId is undefined, and context has a currentThreadId. Clearing current thread from context.');
      clearCurrentThread();
      lastLoadedThreadIdRef.current = null;
      initialLoadCompletedRef.current = false;
    }
  }, [threadId, clearCurrentThread, currentThreadId]);

  // Effect to load thread data - optimized to prevent redundant API calls
  useEffect(() => {
    const loadThread = async () => {
      // Guard against no threadId or already loading
      if (!threadId || isLoadingRef.current) {
        console.log('IntersectXChatPage - loadThread: No threadId or already loading. Aborting load.');
        setLoading(false);
        return;
      }

      // Skip if this thread is already loaded
      if (threadId === lastLoadedThreadIdRef.current && threadLoaded) {
        console.log('IntersectXChatPage - loadThread: Thread already loaded. Skipping load.');
        setLoading(false);
        return;
      }

      console.log('IntersectXChatPage - loadThread: Loading thread:', threadId);
      isLoadingRef.current = true;
      setLoading(true);
      
      try {
        // switchThread will handle its own internal logic for whether to fetch
        await switchThread(threadId);
        console.log('IntersectXChatPage - loadThread: switchThread call completed for', threadId);
        setThreadLoaded(true);
        lastLoadedThreadIdRef.current = threadId;
        initialLoadCompletedRef.current = true;
      } catch (error) {
        console.error('IntersectXChatPage - loadThread: Error during switchThread call for', threadId, error);
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';
        setLoadError(errorMsg);
        setThreadLoaded(false);
      } finally {
        setLoading(false);
        isLoadingRef.current = false;
        console.log('IntersectXChatPage - loadThread: Finished loading attempt for thread:', threadId);
      }
    };

    // Only load if we have a threadId and either:
    // 1. This is our first load (initialLoadCompletedRef is false), or
    // 2. The threadId has changed from what we last loaded
    if (threadId && (!initialLoadCompletedRef.current || threadId !== lastLoadedThreadIdRef.current)) {
      console.log('IntersectXChatPage - useEffect: Loading thread', threadId);
      loadThread();
    } else if (threadId) {
      console.log('IntersectXChatPage - useEffect: Already loaded thread', threadId);
      setLoading(false);
    } else {
      console.log('IntersectXChatPage - useEffect: No threadId in URL. Not calling loadThread.');
      setLoading(false);
    }
  // Only depend on threadId changes to prevent excessive re-renders
  // switchThread should be stable if provided by context
  }, [threadId, switchThread]);

  return (
    <div className="min-h-screen bg-off-white font-chat">
      {/* Mercury-inspired subtle gradient background with Space Grotesk font */}
      <div className="fixed inset-0 bg-gradient-to-br from-off-white to-white opacity-50 z-0"></div>
      {/* Debug info - hidden in production */}
      <div style={{ position: 'fixed', top: '4rem', right: '1rem', background: 'rgba(0,0,0,0.05)', padding: '0.5rem', borderRadius: '0.25rem', fontSize: '0.7rem', zIndex: 1000, maxWidth: '300px', display: 'none' }}>
        Thread ID: {threadId || 'none'}<br/>
        Current Thread ID: {currentThreadId || 'none'}<br/>
        Messages: {messages.length}<br/>
        Thread Loaded: {threadLoaded ? 'Yes' : 'No'}<br/>
        Loading: {loading ? 'Yes' : 'No'}<br/>
        Error: {loadError || 'None'}
      </div>
      
      {/* Show error message if thread loading failed */}
      {loadError && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-10 bg-white border-l-4 border-error rounded-lg p-3 shadow-md text-error text-sm">
          Error loading thread: {loadError}
        </div>
      )}
      
      {/* Show loading indicator if thread is loading */}
      {loading && messages.length === 0 && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple"></div>
        </div>
      )}
      
      <ChatContainer />
    </div>
  );
} 