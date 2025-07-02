import React from 'react';

const HeroSection: React.FC = () => {
  return (
    <div className="text-center py-12 lg:py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl mb-4">
          Discover and Analyze<br className="hidden sm:inline" /> Companies
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto mb-8">
          Get comprehensive insights into companies, their performance, and market trends.
          Make informed decisions with our advanced analysis tools.
        </p>

        {/* Search Bar */}
        <div className="max-w-2xl mx-auto relative">
          <div className="relative">
            <input
              type="text"
              placeholder="Search for a company..."
              className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none shadow-sm"
            />
            {/* Replace with an actual icon or SVG */}
            <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-lg">
              🔍
            </span>
            {/* <button className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1">
              <i className="fas fa-search text-gray-400 hover:text-gray-600"></i>
            </button> */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSection; 