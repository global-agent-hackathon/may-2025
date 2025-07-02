import React from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import { X } from "lucide-react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  section: {
    title: string;
    description: string;
    section_order: number;
    content: string;
  } | null;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, section }) => {
  if (!isOpen || !section) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/20 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      />
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden animate-scale-in">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-lg flex items-center justify-center text-sm font-semibold">
              {section.section_order}
            </div>
            <h3 className="text-xl font-bold text-gray-800">{section.title}</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        <div className="p-6 overflow-y-auto max-h-[calc(80vh-140px)]">
          <div className="prose">
            <ReactMarkdown rehypePlugins={[rehypeRaw]}>
              {section.content}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
