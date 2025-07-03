import React, { useState } from 'react';
import { Paperclip, Sparkles, Send, ArrowUp, Video, Calendar, CheckSquare, Target } from 'lucide-react';

interface ManimatorInterfaceProps {}

const ManimatorInterface: React.FC<ManimatorInterfaceProps> = () => {
  const [inputValue, setInputValue] = useState<string>('');
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setInputValue(e.target.value);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const handleAttachment = (): void => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'video/*,image/*,.pdf,.doc,.docx';
    fileInput.click();
  };

  const handleEnhance = (): void => {
    console.log('Enhancing prompt...');
  };

  const handleSend = (): void => {
    if (inputValue.trim()) {
      setTimeout(() => {
        console.log('Sending:', inputValue);
      }, 1000);
    }
  };

  const quickActions = [
    {
      label: 'Remotion video',
      icon: Video,
      onClick: () => console.log('Remotion video clicked')
    },
    {
      label: 'Kanban board',
      icon: CheckSquare,
      onClick: () => console.log('Kanban board clicked')
    },
    {
      label: 'Task manager',
      icon: Calendar,
      onClick: () => console.log('Task manager clicked')
    },
    {
      label: 'Habit tracker',
      icon: Target,
      onClick: () => console.log('Habit tracker clicked')
    }
  ];

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-white">
      <header className="flex items-center justify-between p-6">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
            <div className="text-black font-bold text-xl">M</div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="px-4 py-2 text-sm text-gray-300 hover:text-white border border-gray-600 rounded-lg hover:border-gray-500 transition-all duration-200">
            Sign In
          </button>
          <button className="px-4 py-2 text-sm bg-white text-black rounded-lg hover:bg-gray-100 transition-all duration-200">
            Sign Up
          </button>
        </div>
      </header>

      <main className="flex flex-col items-center justify-center px-6 py-20">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-light text-center mb-16 tracking-wide">
          Imagine with <span className="font-normal">M</span>animator
        </h1>

        <div className="w-full max-w-2xl mb-16">
          <div className="relative bg-[#2a2a2a] border border-gray-700 rounded-2xl p-4 hover:border-gray-600 transition-all duration-200">
            <div className="flex items-center gap-4">
              <button
                onClick={handleAttachment}
                className="p-2 text-gray-400 hover:text-white transition-colors duration-200"
                aria-label="Attach file"
              >
                <Paperclip className="w-5 h-5" />
              </button>

              <div className="flex-1">
                <input
                  type="text"
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyPress={handleKeyPress}
                  className="w-full bg-transparent text-white placeholder-gray-500 outline-none text-lg"
                  placeholder="A cool video about...."
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleEnhance}
                  className="p-2 text-gray-400 hover:text-yellow-400 transition-colors duration-200"
                  aria-label="Enhance prompt"
                >
                  <Sparkles className="w-5 h-5" />
                </button>

                <button
                  onClick={handleSend}
                  className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-300 hover:text-white transition-all duration-200"
                  aria-label="Send message"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4">
          {quickActions.map((action, index) => {
            const IconComponent = action.icon;
            return (
              <button
                key={index}
                onClick={action.onClick}
                className="group flex items-center gap-2 px-4 py-2 text-sm text-gray-400 hover:text-white border border-gray-700 rounded-lg hover:border-gray-600 transition-all duration-200 hover:bg-gray-800/50"
              >
                <IconComponent className="w-4 h-4" />
                <span>{action.label}</span>
                <ArrowUp className="w-3 h-3 rotate-45 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
              </button>
            );
          })}
        </div>
      </main>
    </div>
  );
};

export default ManimatorInterface;