import React from 'react';
import { BarChart3, MessageSquare } from 'lucide-react';

interface NavigationProps {
  onToggleView: (view: 'chat' | 'metrics') => void;
  currentView: 'chat' | 'metrics';
  isCollapsed?: boolean;
}

const Navigation: React.FC<NavigationProps> = ({
  onToggleView,
  currentView,
  isCollapsed = false
}) => {
  return (
    <nav className="px-3 pb-4">
      <div className="space-y-1">
        <button
          onClick={() => onToggleView('chat')}
          className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
            currentView === 'chat'
              ? 'bg-primary-50 text-primary-700'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
        >
          <MessageSquare className="h-5 w-5" />
          {!isCollapsed && <span className="ml-3">Chat Assistant</span>}
        </button>
        
        <a
          href="https://ads-publisher.feedmob.ai/"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-100"
        >
          <BarChart3 className="h-5 w-5" />
          {!isCollapsed && <span className="ml-3">Performance Metrics</span>}
        </a>
      </div>
    </nav>
  );
};

export default Navigation;