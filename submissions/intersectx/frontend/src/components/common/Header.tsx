import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              {/* Replace with an actual icon or SVG */}
              <span className="text-white text-sm font-bold">VI</span>
            </div>
            <span className="text-xl font-semibold text-gray-900">Intersectx</span>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-8">
            <a href="#" className="text-blue-600 font-medium border-b-2 border-blue-600 pb-4">Home</a>
            <a href="#" className="text-gray-600 hover:text-gray-900 pb-4">IntersectxChat</a>
            <a href="#" className="text-gray-600 hover:text-gray-900 pb-4">Research</a>
          </nav>

          {/* User Profile */}
          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white font-medium text-sm">TU</span> {/* Placeholder for Test User */}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 