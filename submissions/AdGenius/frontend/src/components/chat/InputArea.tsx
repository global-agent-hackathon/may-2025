import React from "react";
import { Image, Mic, Send, StopCircle } from "lucide-react";

interface InputAreaProps {
  newMessage: string;
  setNewMessage: (message: string) => void;
  handleSendMessage: () => void;
  isRecording: boolean;
  toggleRecording: () => void;
  isDisabled: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({
  newMessage,
  setNewMessage,
  handleSendMessage,
  isRecording,
  toggleRecording,
  isDisabled,
}) => {
  return (
    <div className="p-4 md:p-6 bg-white border-t border-gray-200/50 sticky bottom-0 z-10 shadow-md">
      <div className="flex items-end space-x-3">
        <div className="flex-1 bg-white rounded-xl border border-gray-200 focus-within:border-primary-200 focus-within:ring-2 focus-within:ring-primary-100 focus-within:hover:border-primary-200 overflow-hidden">
          <textarea
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            className="w-full px-4 py-3 focus:outline-none resize-none text-[15px]"
            rows={2}
            disabled={isDisabled}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
          />
          <div className="flex items-center justify-between px-4 py-2 border-t border-gray-100">
            <div className="flex items-center space-x-1">
              <button 
                className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100/80 transition-colors"
                disabled={isDisabled}
              >
                <Image className="h-5 w-5" />
              </button>
              <button
                onClick={toggleRecording}
                disabled={isDisabled}
                className={`p-2 rounded-lg transition-colors ${
                  isRecording
                    ? "text-red-500 hover:text-red-600 bg-red-50 hover:bg-red-100/80"
                    : "text-gray-500 hover:text-gray-700 hover:bg-gray-100/80"
                } ${isDisabled ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                {isRecording ? (
                  <StopCircle className="h-5 w-5" />
                ) : (
                  <Mic className="h-5 w-5" />
                )}
              </button>
            </div>
            <button
              onClick={handleSendMessage}
              disabled={isDisabled || (newMessage.trim() === "" && !isRecording)}
              className={`p-2 rounded-lg transition-colors ${
                newMessage.trim() === "" && !isRecording || isDisabled
                  ? "text-gray-400 cursor-not-allowed"
                  : "text-primary-600 hover:text-primary-700 hover:bg-primary-50"
              } ${isDisabled ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InputArea;