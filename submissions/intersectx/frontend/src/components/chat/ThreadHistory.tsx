import React from 'react';
import { TrashIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline';
import { useChatContext, type Thread } from '../../providers/ChatProvider';
import { useNavigate } from 'react-router-dom';
import { cn } from '../../lib/utils';

export function ThreadHistory() {
  const { 
    threads, 
    currentThreadId,
    deleteThread
  } = useChatContext();
  const navigate = useNavigate();


  const handleThreadClick = (threadId: string) => {
    // Just navigate to the thread URL, IntersectXChatPage will handle the thread switching
    navigate(`/intersectx-chat/t/${threadId}`);
  };

  const handleDeleteThread = async (threadId: string) => {
    const success = await deleteThread(threadId);
    if (success && currentThreadId === threadId) {
      // If we deleted the current thread and there are other threads available,
      // navigate to the first available thread instead of creating a new one
      if (threads.length > 1) {
        // Find the first thread that's not the one being deleted
        const nextThread = threads.find(t => t.id !== threadId);
        if (nextThread) {
          navigate(`/intersectx-chat/t/${nextThread.id}`);
          return;
        }
      }
      // If no other threads exist, navigate to the main chat page
      // This will create a new thread but only once
      navigate('/intersectx-chat');
    }
  };

  return (
    <aside className="w-full h-full flex flex-col bg-white overflow-hidden">
      <div className="px-4 py-2">
        <h3 className="text-sm font-medium text-[#49739c] mb-1 text-center">Chat History</h3>
      </div>


      <div className="flex-1 overflow-y-auto px-3 py-1 scrollbar-hide">
        {threads.length === 0 ? (
          <div className="text-center text-[#49739c] p-4 border border-dashed border-[#e7edf4] rounded-lg">
            <p className="text-sm">No chat history yet</p>
            <p className="text-xs mt-1">Start a new conversation to see it here</p>
          </div>
        ) : (
          <ul className="space-y-1.5">
            {threads.map((thread) => (
              <ThreadItem
                key={thread.id}
                thread={thread}
                isActive={thread.id === currentThreadId}
                onClick={() => handleThreadClick(thread.id)}
                onDelete={() => handleDeleteThread(thread.id)}
              />
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}

interface ThreadItemProps {
  thread: Thread;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}

function ThreadItem({ thread, isActive, onClick, onDelete }: ThreadItemProps) {
  console.log(thread)
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete "${thread.title}"?`)) {
      onDelete();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      onClick();
    }
  };

  return (
    <li>
      <div
        onClick={onClick}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        className={cn(
          "w-full text-left p-3 rounded-lg flex items-center justify-between group cursor-pointer transition-colors",
          isActive 
            ? "bg-[#e7edf4] text-[#0d141c]" 
            : "text-[#49739c] hover:bg-[#f5f8fc] border border-[#e7edf4]"
        )}
      >
        <div className="truncate flex-1 flex items-center">
          <ChatBubbleLeftIcon className="h-4 w-4 mr-2 flex-shrink-0" />
          <div className="truncate">
            <div className="font-medium truncate text-xs">New Chat - {new Date(thread.createdAt).toLocaleString('en-US', { 
              month: 'short', 
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}</div>
            {thread.lastMessage && (
              <div className="text-xs opacity-70 truncate mt-1">
                {thread.lastMessage?.content.substring(0, 40)}
                {thread.lastMessage?.content.length > 40 ? "..." : ""}
              </div>
            )}
          </div>
        </div>
        <button
          onClick={handleDeleteClick}
          className="h-4 w-4 opacity-0 group-hover:opacity-100 ml-2 flex-shrink-0 text-gray-500 hover:text-red-500"
          aria-label="Delete thread"
        >
          <TrashIcon className="h-4 w-4" />
        </button>
      </div>
    </li>
  );
} 