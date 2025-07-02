import React from 'react';
import type { Company } from '../../types/Company';
import CompanyCard from './CompanyCard';

interface CompanyGridProps {
  companies: Company[];
  isLoading: boolean;
  onQuickView: (companyId: string) => void;
  onRequestAccess: (companyId: string) => void;
  onAnalyzeWithAI: (companyId: string) => void;
}

const CompanyGrid: React.FC<CompanyGridProps> = ({
  companies,
  isLoading,
  onQuickView,
  onRequestAccess,
  onAnalyzeWithAI,
}) => {
  if (isLoading) {
    // Basic loading state, can be enhanced with skeleton loaders
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 py-8">
        {Array.from({ length: 8 }).map((_, index) => (
          <div key={index} className="bg-white shadow-lg rounded-lg p-4 animate-pulse">
            <div className="h-40 bg-gray-300 rounded mb-4"></div>
            <div className="h-6 bg-gray-300 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2 mb-2"></div>
            <div className="h-4 bg-gray-300 rounded w-1/3 mb-4"></div>
            <div className="flex space-x-2">
              <div className="h-10 bg-gray-300 rounded flex-1"></div>
              <div className="h-10 bg-gray-300 rounded flex-1"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (companies.length === 0) {
    return <p className="text-center text-gray-500 py-8">No companies to display.</p>;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-6 xl:gap-8 py-8">
      {/* Adjusted to 3 columns for desktop as per original prompt, image also shows 3 */}
      {companies.map((company) => (
        <CompanyCard
          key={company.id}
          company={company}
          onQuickView={onQuickView}
          onRequestAccess={onRequestAccess}
          onAnalyzeWithAI={onAnalyzeWithAI}
        />
      ))}
    </div>
  );
};

export default CompanyGrid; 