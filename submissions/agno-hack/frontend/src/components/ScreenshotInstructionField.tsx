import React from 'react';
import { Trash2 } from 'lucide-react';
import { ScreenshotInstruction } from '../types/TestConfig';

interface ScreenshotInstructionFieldProps {
  instruction: ScreenshotInstruction;
  index: number;
  onChange: (index: number, field: keyof ScreenshotInstruction, value: string) => void;
  onRemove: (index: number) => void;
}

const ScreenshotInstructionField: React.FC<ScreenshotInstructionFieldProps> = ({
  instruction,
  index,
  onChange,
  onRemove
}) => {
  return (
    <div className="p-4 border border-gray-200 rounded-lg bg-white mb-4 animate-fadeIn">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-medium text-gray-700">Screenshot #{index + 1}</h3>
        <button
          type="button"
          onClick={() => onRemove(index)}
          className="text-gray-400 hover:text-red-500 transition-colors"
          aria-label="Remove screenshot instruction"
        >
          <Trash2 size={18} />
        </button>
      </div>
      <div className="space-y-3">
        <div>
          <label htmlFor={`step-description-${index}`} className="block text-sm font-medium text-gray-700 mb-1">
            Step Description
          </label>
          <textarea
            id={`step-description-${index}`}
            value={instruction.step_description}
            onChange={(e) => onChange(index, 'step_description', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            rows={2}
            placeholder="Describe when to take the screenshot"
            required
          />
        </div>
        <div>
          <label htmlFor={`filename-${index}`} className="block text-sm font-medium text-gray-700 mb-1">
            Filename
          </label>
          <input
            type="text"
            id={`filename-${index}`}
            value={instruction.filename}
            onChange={(e) => onChange(index, 'filename', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            placeholder="TC_Example_Screenshot.png"
            required
          />
        </div>
      </div>
    </div>
  );
};

export default ScreenshotInstructionField;