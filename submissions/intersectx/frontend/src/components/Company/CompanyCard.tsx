import React from 'react';
import { Link } from 'react-router-dom';
import type { Company } from '../../types/Company';
import ConnectionStatusBadge from './ConnectionStatusBadge';
import { formatCurrency } from '../../lib/utils';

interface CompanyCardProps {
  company: Company;
  onQuickView: (companyId: string) => void;
  onRequestAccess: (companyId: string) => void;
  onAnalyzeWithAI: (companyId: string) => void;
}

const CompanyCard: React.FC<CompanyCardProps> = ({ 
  company,
  onQuickView,
  onRequestAccess,
  onAnalyzeWithAI 
}) => {
  const { 
    id,
    logoUrl,
    name,
    industry,
    location,
    // foundedYear, // Not shown in the compact card image directly
    shortDescription, // Using this instead of tagline for main card text based on image
    metrics,
    tags,
    connectionStatus,
    stage 
  } = company;

  const handleRequestAccess = () => {
    onRequestAccess(id);
  };

  const handleQuickView = () => {
    onQuickView(id);
  };

  const handleAnalyzeWithAI = () => {
    onAnalyzeWithAI(id);
  };

  return (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden transform transition-all hover:scale-105 duration-300 ease-in-out">
      <div className="relative">
        <img className="w-full h-40 object-cover" src={logoUrl || 'https://via.placeholder.com/400x200?text=Company+Logo'} alt={`${name} logo`} />
        {stage && (
          <span className="absolute top-0 right-0 bg-purple-600 text-white text-xs font-semibold px-3 py-1 m-2 rounded-full shadow-md">
            {stage}
          </span>
        )}
        <div className="absolute top-2 left-2">
          <ConnectionStatusBadge status={connectionStatus} />
        </div>
      </div>

      <div className="p-4">
        <h3 className="text-xl font-bold text-gray-800 mb-1">{name}</h3>
        <p className="text-sm text-gray-600 mb-2 truncate" title={shortDescription}>{shortDescription}</p>
        
        {tags && tags.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-1">
            {tags.map((tag) => (
              <span key={tag} className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-xs font-medium">
                {tag}
              </span>
            ))}
          </div>
        )}

        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-700 mb-3">
          {metrics.fundingAsk && <div><span className="font-semibold">Funding Ask:</span> {formatCurrency(metrics.fundingAsk)}</div>}
          {metrics.valuation && <div><span className="font-semibold">Valuation:</span> {formatCurrency(metrics.valuation)}</div>}
          {industry && <div><span className="font-semibold">Industry:</span> {industry}</div>}
          {location && <div><span className="font-semibold">Location:</span> {location}</div>}
          {/* Optional: Add more metrics from the detailed design if space allows or for QuickView */}
          {/* {metrics.series && <div><span className="font-semibold">Series:</span> {metrics.series}</div>} */}
          {/* {metrics.employees && <div><span className="font-semibold">Employees:</span> {metrics.employees}</div>} */}
          {/* {metrics.arr && <div><span className="font-semibold">ARR:</span> {formatCurrency(metrics.arr)}</div>} */}
          {/* {metrics.keyFocus && <div><span className="font-semibold">Focus:</span> {metrics.keyFocus}</div>} */}
        </div>

        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 mb-2">
          <button 
            onClick={handleQuickView} 
            className="w-full sm:w-auto flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md text-sm transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-gray-400"
          >
            Quick View
          </button>
          
          {connectionStatus === 'connected' && company.isChatReady ? (
            <button 
              onClick={handleAnalyzeWithAI} 
              className="w-full sm:w-auto flex-1 bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded-md text-sm transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-400"
            >
              Analyze with AI
            </button>
          ) : connectionStatus !== 'connected' && connectionStatus !== 'pending' ? (
            <button 
              onClick={handleRequestAccess} 
              className="w-full sm:w-auto flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-md text-sm transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              {connectionStatus === 'private' || connectionStatus === 'public' ? 'Request Access' : 'Request Sent'}
            </button>
          ) : (
            <button 
              className="w-full sm:w-auto flex-1 bg-yellow-500 text-white font-semibold py-2 px-4 rounded-md text-sm cursor-not-allowed opacity-75"
              disabled
            >
              Pending Approval
            </button>
          )}
        </div>
        
        <Link 
          to={`/companies/${encodeURIComponent(name)}/analysis`} 
          className="block w-full text-center bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-md text-sm transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
          Detailed Analysis
        </Link>
      </div>
    </div>
  );
};

export default CompanyCard; 