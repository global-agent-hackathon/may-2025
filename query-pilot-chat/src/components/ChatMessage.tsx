import { Bot, User } from "lucide-react";
import { Markdown } from "./ui/markdown";

interface ChatMessageProps {
  message: string; // Expect string directly
  isBot: boolean;
  // Updated to include all possible types from ChatContainer
  type: 'search' | 'ai' | 'dialogue' | 'info' | 'error' | 'status' | 'grammar' | 'vocabulary' | 'culture' | 'explanation' | 'problems' | 'visuals' | 'pronunciation';
  data?: any;
}

const ChatMessage = ({ message, isBot, type, data }: ChatMessageProps) => {
  // Directly use the message prop as it's expected to be a string

  return (
    <div
      className={`flex gap-4 ${
        isBot ? "justify-start" : "justify-end"
      } mb-6 animate-fade-in max-w-3xl mx-auto`}
    >
      {isBot && (
        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
          <Bot className="w-6 h-6 text-gray-600" />
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-xl px-6 py-4 ${
          isBot
            ? "bg-white shadow-sm border border-gray-100"
            : "bg-gray-800 text-white"
        }`}
      >
        <div className={`text-xs ${isBot ? "text-gray-400" : "text-gray-300"} mb-2`}>
          {/* Adjust title based on type */}
          {type === "search" ? "Search Result"
           : type === "dialogue" ? "Practice Dialogue"
           : type === "info" ? "Info"
           : type === "error" ? "Error"
           : type === "status" ? "Status"
           : "AI Response"}
        </div>
        {/* Render the main message string using Markdown */}
        <Markdown>{message || ""}</Markdown> {/* Ensure message is not null/undefined */}

        {/* Optional: Add specific rendering based on data prop if needed */}

      </div>
      {!isBot && (
        <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center">
          <User className="w-6 h-6 text-gray-600" />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;

