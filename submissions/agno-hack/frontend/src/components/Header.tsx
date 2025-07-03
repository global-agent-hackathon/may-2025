import React from 'react';
import { Compass } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-primary-800 shadow-lg py-4 px-6 md:px-8">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Compass className="h-6 w-6 text-white" />
          <h1 className="text-xl font-semibold text-white">WebTest AI</h1>
        </div>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <a href="#" className="text-sm font-medium text-primary-100 hover:text-white transition-colors">
                Documentation
              </a>
            </li>
            <li>
              <a href="#" className="text-sm font-medium text-primary-100 hover:text-white transition-colors">
                Examples
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;