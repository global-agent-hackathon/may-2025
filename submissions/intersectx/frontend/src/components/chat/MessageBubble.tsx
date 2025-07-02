// React is used implicitly in JSX
import { cn } from '../../lib/utils';
import type { Message } from '../../providers/ChatProvider';
import { AttachmentList } from './AttachmentList';
import { CodeBracketIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageBubbleProps {
  message: Message;
  isLoading?: boolean;
}

export function MessageBubble({ message, isLoading = false }: MessageBubbleProps) {
  const isUser = message.type === 'human';
  const isAI = message.type === 'ai';
  const isTool = message.type === 'tool';
  
  const hasAttachments = message.metadata?.attachments && message.metadata.attachments.length > 0;

  return (
    <>
      <div
        className={cn(
          'flex w-full mb-4',
          isUser ? 'justify-end' : 'justify-start'
        )}
      >
      {/* AI or User Message */}
      <div
        className={cn(
          'max-w-[80%] p-3.5 shadow-sm',
          isUser ? 'bg-purple text-white rounded-2xl rounded-tr-sm' : 'bg-white border border-gray-200 text-primary rounded-2xl rounded-tl-sm',
          isTool && 'bg-purple-light/10 text-purple-dark border-gray-200 text-sm font-mono rounded-xl',
        )}
      >
        {isLoading ? (
          <div className="flex space-x-2">
            <div className="h-2.5 w-2.5 animate-pulse rounded-full bg-purple-light opacity-80"></div>
            <div className="h-2.5 w-2.5 animate-pulse rounded-full bg-purple-light opacity-80" style={{ animationDelay: '0.2s' }}></div>
            <div className="h-2.5 w-2.5 animate-pulse rounded-full bg-purple-light opacity-80" style={{ animationDelay: '0.4s' }}></div>
          </div>
        ) : (
          <>
            {/* Tool Icon for Tool Messages */}
            {isTool && (
              <div className="flex items-center mb-1">
                <CodeBracketIcon className="h-4 w-4 mr-1 text-purple-dark" />
                <span className="text-xs font-medium text-purple-dark">Tool Call</span>
              </div>
            )}
            
            {/* Message Content */}
            {isAI ? (
              <div className="markdown-content break-words [&_p]:my-1.5 [&_ul]:mt-2 [&_ol]:mt-2 [&_li]:my-1 [&_h1]:mt-3 [&_h1]:mb-2 [&_h2]:mt-2 [&_h2]:mb-1.5 [&_h3]:mt-2 [&_h3]:mb-1">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    a: ({ node, ...props }) => (
                      <a 
                        {...props} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-purple hover:text-purple-dark hover:underline transition-colors"
                      />
                    ),
                    strong: ({ node, ...props }) => (
                      <strong {...props} className="font-bold" />
                    ),
                    ul: ({ node, ...props }) => (
                      <ul {...props} className="list-disc ml-6 my-2" />
                    ),
                    ol: ({ node, ...props }) => (
                      <ol {...props} className="list-decimal ml-6 my-2" />
                    ),
                    li: ({ node, ...props }) => (
                      <li {...props} className="my-1" />
                    ),
                    h1: ({ node, ...props }) => (
                      <h1 {...props} className="text-xl font-bold my-3" />
                    ),
                    h2: ({ node, ...props }) => (
                      <h2 {...props} className="text-lg font-bold my-2" />
                    ),
                    h3: ({ node, ...props }) => (
                      <h3 {...props} className="text-base font-bold my-2" />
                    ),
                    code: ({ node, ...props }) => (
                      <code {...props} className="bg-purple-light/10 px-1.5 py-0.5 rounded font-mono text-sm text-primary" />
                    ),
                    blockquote: ({ node, ...props }) => (
                      <blockquote {...props} className="border-l-4 border-purple-light pl-3 italic my-2" />
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            ) : (
              <div className="whitespace-pre-wrap break-words">{message.content}</div>
            )}
            
            {/* Charts are rendered outside the message bubble as separate components */}

            {/* Attachments */}
            {hasAttachments && !isUser && (
              <AttachmentList attachments={message.metadata!.attachments!} />
            )}
            
            {/* Timestamp */}
            {message.timestamp && !isLoading && (
              <div className="text-xs mt-2 opacity-60 flex items-center">
                <svg className="inline-block mr-1 h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            )}
          </>
        )}
      </div>
    </div>
      
      {/* Charts are now rendered in ChatContainer */}
    </>
  );
} 