import React from 'react';

interface MobileSignOutProps {
  onSignOut?: () => void;
}

const MobileSignOut: React.FC<MobileSignOutProps> = ({ onSignOut }) => {
  return (
    <div className="border-t border-gray-200 p-4 md:hidden">
      <button
        onClick={onSignOut}
        className="w-full text-sm text-red-600 font-medium"
      >
        Sign Out
      </button>
    </div>
  );
};

export default MobileSignOut;