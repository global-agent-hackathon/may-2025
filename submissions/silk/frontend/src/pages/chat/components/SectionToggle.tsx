import React from "react";
import { ChevronDown, ChevronUp, BookOpen } from "lucide-react";

interface SectionToggleProps {
  section: { section_order: number; title: string; description: string };
  isOpen: boolean;
  onToggle: () => void;
  onOpenModal: () => void;
}

const SectionToggle: React.FC<SectionToggleProps> = ({
  section,
  isOpen,
  onToggle,
  onOpenModal,
}) => (
  <div className="bg-white border border-gray-100 rounded-xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden">
    <button
      onClick={onToggle}
      className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors duration-200"
    >
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-lg flex items-center justify-center text-sm font-semibold">
          {section.section_order}
        </div>
        <h4 className="font-semibold text-gray-800">{section.title}</h4>
      </div>
      {isOpen ? (
        <ChevronUp className="w-5 h-5 text-gray-400" />
      ) : (
        <ChevronDown className="w-5 h-5 text-gray-400" />
      )}
    </button>

    {isOpen && (
      <div className="px-4 pb-4 border-t border-gray-50 bg-gray-50/50 animate-fade-in">
        <p className="text-gray-600 text-sm mb-3 mt-3 leading-relaxed">
          {section.description}
        </p>
        <button
          onClick={onOpenModal}
          className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors duration-200"
        >
          <BookOpen className="w-4 h-4" />
          View Full Content
        </button>
      </div>
    )}
  </div>
);

export default SectionToggle;
