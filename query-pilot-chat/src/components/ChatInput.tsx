
import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Search, SendHorizontal } from "lucide-react";

interface ChatInputProps {
  onSubmit: (message: string, type: "search" | "ai") => void;
}

const ChatInput = ({ onSubmit }: ChatInputProps) => {
  const [message, setMessage] = useState("");

  const handleSubmit = (type: "search" | "ai") => {
    if (message.trim()) {
      onSubmit(message, type);
      setMessage("");
    }
  };

  return (
    <div className="border-t bg-white dark:bg-gray-800 p-6 shadow-lg">
      <div className="max-w-3xl mx-auto flex flex-col gap-4">
        <Input
          placeholder="Type your question..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="flex-1 bg-gray-50 dark:bg-gray-700 border-violet-100 dark:border-gray-600 focus:border-violet-300"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit("ai");
            }
          }}
        />
        <div className="flex gap-3">
          <Button
            onClick={() => handleSubmit("search")}
            variant="secondary"
            className="flex-1 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600"
          >
            <Search className="w-4 h-4 mr-2" />
            Search
          </Button>
          <Button
            onClick={() => handleSubmit("ai")}
            variant="default"
            className="flex-1 bg-lightBlue hover:bg-lightBlue-hover text-white"
          >
            <SendHorizontal className="w-4 h-4 mr-2" />
            Ask AI
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
