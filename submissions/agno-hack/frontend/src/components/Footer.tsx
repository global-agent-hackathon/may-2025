import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-primary-100 py-6 px-6 md:px-8 mt-auto">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-gray-500 mb-4 md:mb-0">
            © {new Date().getFullYear()} WebTest AI. All rights reserved.
          </p>
          <div className="flex space-x-6">
            <a href="#" className="text-sm text-primary-600 hover:text-primary-800 transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="text-sm text-primary-600 hover:text-primary-800 transition-colors">
              Terms of Service
            </a>
            <a href="#" className="text-sm text-primary-600 hover:text-primary-800 transition-colors">
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer