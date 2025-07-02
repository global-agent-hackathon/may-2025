import React from "react";
import { Sparkles, Zap } from "lucide-react";
import CustomDropdown from "./CustomDropdown";
import SuggestionPill from "./SuggestionPill";

interface InputFormProps {
  description: string;
  setDescription: (description: string) => void;
  selectedLevel: string;
  setSelectedLevel: (level: string) => void;
  handleSendMessage: (
    e: React.FormEvent<HTMLFormElement> | React.MouseEvent<HTMLButtonElement>
  ) => void;
  isProcessing: boolean;
}

const InputForm: React.FC<InputFormProps> = ({
  description,
  setDescription,
  selectedLevel,
  setSelectedLevel,
  handleSendMessage,
  isProcessing,
}) => {
  const levelOptions = [
    {
      value: "Beginner",
      label: "Beginner",
      icon: "🌱",
      color: "text-emerald-600",
    },
    {
      value: "Intermediate",
      label: "Intermediate",
      icon: "🚀",
      color: "text-blue-600",
    },
    {
      value: "Advanced",
      label: "Advanced",
      icon: "⚡",
      color: "text-purple-600",
    },
  ];

  const suggestions = [
    {
      text: "Complete React.js Masterclass",
      color:
        "bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 border border-blue-200",
    },
    {
      text: "Python for Data Science",
      color:
        "bg-gradient-to-r from-green-100 to-green-200 text-green-800 border border-green-200",
    },
    {
      text: "Modern JavaScript ES6+",
      color:
        "bg-gradient-to-r from-yellow-100 to-yellow-200 text-yellow-800 border border-yellow-200",
    },
    {
      text: "Machine Learning Fundamentals",
      color:
        "bg-gradient-to-r from-purple-100 to-purple-200 text-purple-800 border border-purple-200",
    },
    {
      text: "Node.js Backend Development",
      color:
        "bg-gradient-to-r from-emerald-100 to-emerald-200 text-emerald-800 border border-emerald-200",
    },
    {
      text: "Database Design & SQL",
      color:
        "bg-gradient-to-r from-orange-100 to-orange-200 text-orange-800 border border-orange-200",
    },
  ];

  if (isProcessing) {
    return (
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-2xl mb-8 border border-blue-100 animate-fade-in">
        <div className="flex items-center gap-3 mb-3">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <p className="text-sm font-medium text-blue-700">
            Creating your course
          </p>
        </div>
        <p className="text-lg text-gray-800 font-medium mb-2">
          "{description}"
        </p>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Level:</span>
          <span
            className={`text-sm font-semibold px-2 py-1 rounded-md ${
              selectedLevel === "Beginner"
                ? "bg-emerald-100 text-emerald-700"
                : selectedLevel === "Intermediate"
                ? "bg-blue-100 text-blue-700"
                : "bg-purple-100 text-purple-700"
            }`}
          >
            {selectedLevel}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      <div className="text-center mb-8 animate-fade-in">
        <div className="flex items-center justify-center gap-2 mb-3">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Ready to create a course?
          </h1>
        </div>
        <p className="text-gray-600 text-lg">
          Describe your dream course and watch our AI bring it to life
        </p>
      </div>

      <form
        onSubmit={handleSendMessage}
        className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-6"
      >
        <div className="space-y-2">
          <label
            htmlFor="course-description"
            className="text-sm font-medium text-gray-700"
          >
            Course Description
          </label>
          <textarea
            id="course-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the course you want to create... (e.g., 'A comprehensive guide to modern web development with practical projects')"
            className="w-full p-4 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 resize-none text-gray-700 placeholder-gray-400"
            rows={3}
          />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="w-full sm:w-1/2 space-y-2">
            {" "}
            <p className="sr-only">Difficulty Level</p>{" "}
            <CustomDropdown
              value={selectedLevel}
              onChange={setSelectedLevel}
              options={levelOptions}
            />
          </div>
          <button
            type="submit"
            disabled={!description.trim()}
            className=" bg-blue-600 text-white py-2 px-3 rounded-xl disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 font-semibold text-base flex items-center justify-center gap-2 hover:bg-blue-700 active:scale-[0.98] hover:shadow"
          >
            <Zap className="w-4 h-4" />
            Generate Course
          </button>
        </div>
      </form>

      <div className="space-y-3 animate-fade-in-up">
        <p className="text-sm font-medium text-gray-600 text-center">
          Or try one of these popular courses:
        </p>
        <div className="flex flex-wrap gap-2 justify-center">
          {suggestions.map((suggestion, index) => (
            <SuggestionPill
              key={index}
              text={suggestion.text}
              color={suggestion.color}
              onClick={() => setDescription(suggestion.text)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default InputForm;
