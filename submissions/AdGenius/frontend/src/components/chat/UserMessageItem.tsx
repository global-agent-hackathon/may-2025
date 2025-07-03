import React from "react";
import { ChatMessage } from "../../types/index";

interface UserMessageItemProps {
  message: ChatMessage;
}

const UserMessageItem: React.FC<UserMessageItemProps> = ({ message }) => {
  return (
    <div className="max-w-[85%] p-4 rounded-2xl shadow-sm bg-primary-600 text-white rounded-br-sm">
      <div className="text-[15px]">
        <div className="whitespace-pre-line leading-normal">{message.content}</div>
      </div>
      {message.image && (
        <img
          src={message.image}
          alt="Ad creative"
          className="mt-3 rounded-xl w-full h-auto max-h-64 object-cover"
        />
      )}
      <div className="flex items-center justify-between text-xs mt-2 text-primary-200">
        <div>
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
};

export default UserMessageItem;