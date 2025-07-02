import React, { useState } from 'react';

interface InvestorCardProps {
  investor: {
    first_name: string;
    last_name: string;
    linkedin_url: string;
    portfolio: number;
    companies_invested: number;
    email?: string;
  };
  onReachOut?: () => void;
  isConnected?: boolean;
}

const InvestorCard: React.FC<InvestorCardProps> = ({ investor, onReachOut, isConnected }) => {
  const [isHovered, setIsHovered] = useState(false);
  const initials = `${investor.first_name.charAt(0)}${investor.last_name.charAt(0)}`;

  return (
    <div
      className="relative transition-all duration-300 ease-out"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        transform: isHovered ? 'scale(1.03) translateY(-8px)' : 'translateY(0)',
      }}
    >
      {/* No shadow elements for cleaner design */}

      {/* Main Card */}
      <div className="relative bg-white rounded-xl overflow-hidden shadow-lg hover:shadow-xl border border-gray-100 flex flex-col h-full transform transition-all duration-300">
        {/* Avatar Area */}
        <div className="relative h-44 bg-white flex items-center justify-center p-4">
          <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center text-3xl font-bold text-indigo-600 border-2 border-indigo-200">
            {initials}
          </div>
          {/* LinkedIn Icon/Link */}
          <a
            href={investor.linkedin_url}
            target="_blank"
            rel="noopener noreferrer"
            className="absolute top-3 right-3 z-10 bg-blue-50 hover:bg-blue-100 rounded-full p-2 shadow-sm border border-blue-100 transition-colors"
            title="View LinkedIn Profile"
          >
            <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.76 0-5 2.24-5 5v14c0 2.76 2.24 5 5 5h14c2.76 0 5-2.24 5-5v-14c0-2.76-2.24-5-5-5zm-11 19h-3v-9h3v9zm-1.5-10.28c-.97 0-1.75-.79-1.75-1.75s.78-1.75 1.75-1.75 1.75.79 1.75 1.75-.78 1.75-1.75 1.75zm15.5 10.28h-3v-4.5c0-1.08-.02-2.47-1.5-2.47-1.5 0-1.73 1.17-1.73 2.39v4.58h-3v-9h2.88v1.23h.04c.4-.75 1.38-1.54 2.84-1.54 3.04 0 3.6 2 3.6 4.59v4.72z"/></svg>
          </a>
        </div>
        <div className="p-4 flex flex-col flex-grow bg-gray-50 border-t border-gray-100">
          <h3 className="font-semibold text-lg text-gray-900 mb-1 truncate">{investor.first_name} {investor.last_name}</h3>
          <div className="grid grid-cols-2 gap-x-2 gap-y-1 mb-4 text-xs">
            <div>
              <span className="text-gray-500">Portfolio:</span>
              <div className="font-medium text-gray-800">${investor.portfolio.toLocaleString()}</div>
            </div>
            <div>
              <span className="text-gray-500">Companies Invested:</span>
              <div className="font-medium text-gray-800">{investor.companies_invested}</div>
            </div>
          </div>
          <div className="flex gap-2 mt-auto pt-3 border-t border-gray-200">
            {isConnected ? (
              <span className="flex-1 px-3 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-lg flex items-center justify-center shadow-sm border border-green-200">
                <svg className="w-4 h-4 mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20"><path d="M16.707 5.293a1 1 0 00-1.414 0L8 12.586 4.707 9.293a1 1 0 00-1.414 1.414l4 4a1 1 0 001.414 0l8-8a1 1 0 000-1.414z" /></svg>
                Connected
              </span>
            ) : (
              <button 
                className="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center shadow-sm"
                onClick={onReachOut}
              >
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20"><path d="M2.003 9.25C2.003 5.798 4.8 3 8.25 3c2.1 0 3.95 1.09 5.01 2.75h1.24c2.45 0 4.44 1.99 4.44 4.44 0 2.45-1.99 4.44-4.44 4.44h-1.24c-1.06 1.66-2.91 2.75-5.01 2.75-3.45 0-6.25-2.8-6.25-6.25zm6.25 4.25c2.35 0 4.25-1.9 4.25-4.25s-1.9-4.25-4.25-4.25-4.25 1.9-4.25 4.25 1.9 4.25 4.25 4.25z"/></svg>
                Reach Out for Investment
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestorCard; 