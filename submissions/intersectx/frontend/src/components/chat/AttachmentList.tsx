import { DocumentTextIcon, DocumentIcon } from '@heroicons/react/24/outline';
import type { Attachment } from '../../providers/ChatProvider';

interface AttachmentListProps {
  attachments: Attachment[];
}

export function AttachmentList({ attachments }: AttachmentListProps) {
  if (!attachments || attachments.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 space-y-2">
      <h4 className="text-xs font-medium text-gray-500">Attachments</h4>
      <div className="space-y-2">
        {attachments.map((attachment) => (
          <AttachmentItem key={attachment.id} attachment={attachment} />
        ))}
      </div>
    </div>
  );
}

interface AttachmentItemProps {
  attachment: Attachment;
}

function AttachmentItem({ attachment }: AttachmentItemProps) {
  const isPDF = attachment.type.includes('pdf');
  const isDoc = attachment.type.includes('word') || attachment.name.endsWith('.doc') || attachment.name.endsWith('.docx');
  
  return (
    <a 
      href={attachment.url} 
      target="_blank" 
      rel="noopener noreferrer"
      className="flex items-center p-2 rounded-lg border border-gray-200 bg-gray-50 hover:bg-gray-100 transition-colors"
    >
      {isPDF ? (
        <DocumentTextIcon className="h-5 w-5 text-red-500 mr-2" />
      ) : isDoc ? (
        <DocumentTextIcon className="h-5 w-5 text-blue-500 mr-2" />
      ) : (
        <DocumentIcon className="h-5 w-5 text-gray-500 mr-2" />
      )}
      
      <div className="flex flex-col min-w-0">
        <div className="text-sm font-medium text-gray-900 truncate">
          {attachment.name}
        </div>
        <div className="text-xs text-gray-500">
          {formatFileSize(attachment.size)}
        </div>
      </div>
    </a>
  );
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return bytes + ' B';
  } else if (bytes < 1024 * 1024) {
    return (bytes / 1024).toFixed(1) + ' KB';
  } else {
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
} 