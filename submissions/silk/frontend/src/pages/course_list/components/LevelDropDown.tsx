import { useState } from "react";

interface LevelDropdownProps {
  selectedLevel: string;
  setSelectedLevel: (level: string) => void;
  levels: string[];
}

export default function LevelDropdown({
  selectedLevel,
  setSelectedLevel,
  levels,
}: LevelDropdownProps) {
  const [open, setOpen] = useState(false);

  const handleSelect = (level: string) => {
    setSelectedLevel(level);
    setOpen(false);
  };

  return (
    <div className="relative w-full sm:w-auto">
      <button
        onClick={() => setOpen(!open)}
        className="w-full sm:w-48 flex justify-between items-center py-2 px-4 border border-slate-300 rounded-lg bg-white text-slate-700"
      >
        <span>{selectedLevel || "All Levels"}</span>
        <svg
          className={`w-4 h-4 transform transition-transform duration-200 ${
            open ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {open && (
        <div className="absolute z-10 mt-2 w-full sm:w-48 bg-white border border-slate-200 rounded-lg shadow-lg">
          <div
            onClick={() => handleSelect("")}
            className="px-4 py-2 cursor-pointer hover:bg-indigo-50"
          >
            All Levels
          </div>
          {levels.map((level) => (
            <div
              key={level}
              onClick={() => handleSelect(level)}
              className={`px-4 py-2 cursor-pointer hover:bg-indigo-50 ${
                selectedLevel === level ? "bg-indigo-100 font-medium" : ""
              }`}
            >
              {level}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
