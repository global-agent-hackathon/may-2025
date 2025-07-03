import React from 'react';
import { Plus } from 'lucide-react';

interface NewCampaignButtonProps {
  isCollapsed?: boolean;
  onClick?: () => void;
}

const NewCampaignButton: React.FC<NewCampaignButtonProps> = ({
  isCollapsed = false,
  onClick
}) => {
  return (
    <div className="p-4">
      <button 
        onClick={onClick}
        className={`flex items-center justify-center py-2.5 px-4 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-medium transition-colors ${
          isCollapsed ? 'w-12 px-0' : 'w-full'
        }`}
      >
        <Plus className="h-5 w-5" />
        {!isCollapsed && <span className="ml-2">New Campaign</span>}
      </button>
    </div>
  );
};

export default NewCampaignButton;