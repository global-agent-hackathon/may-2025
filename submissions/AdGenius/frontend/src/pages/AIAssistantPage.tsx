import React from 'react';
import ChatPanel from '../components/ChatPanel';

const AIAssistantPage: React.FC = () => {
  return (
    <div className="w-full h-full p-6">
      <h1 className="text-2xl font-bold mb-6">AI Chat Assistant</h1>
      <div className="w-full h-[calc(100%-60px)]">
        <ChatPanel />
      </div>
    </div>
  );
};

export default AIAssistantPage;