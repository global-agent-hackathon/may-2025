import React from "react";

interface SuggestionPillProps {
  text: string;
  color: string;
  onClick: () => void;
}

const SuggestionPill: React.FC<SuggestionPillProps> = ({
  text,
  color,
  onClick,
}) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 hover:scale-105 active:scale-95 ${color} hover:shadow-md`}
  >
    {text}
  </button>
);

export default SuggestionPill;
