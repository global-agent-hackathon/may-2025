import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
// import Badge from '../ui/Badge'; // Temporarily removed due to creation issues

// Match this interface with the one in Home.tsx or a shared types file
interface Company {
  id: string | number;
  name: string;
  description?: string;
  logoUrl?: string; // URL to company logo
  logoText?: string;

  logoIconClass?: string; // e.g., 'fas fa-leaf' for Font Awesome
  fundingStage: string; // e.g., 'Seed Stage', 'Series A'
  tags?: string[];
  fundingAsk?: string | number;
  industry?: string;
  valuation?: string | number;
  location?: string;

}

interface CompanyCardProps {
  company: Company;
}

// Temporary simplified badge styling function (until Badge.tsx is fixed)
const getBadgeStyles = (color: 'green' | 'yellow' | 'purple' | 'blue' | 'red' | 'gray') => {
  const baseStyle = "px-2 py-1 rounded-full text-xs font-medium";
  const colorStyles = {
    green: 'bg-green-100 text-green-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    purple: 'bg-purple-100 text-purple-800',
    blue: 'bg-blue-100 text-blue-800',
    red: 'bg-red-100 text-red-800',
    gray: 'bg-gray-100 text-gray-800',
  };
  return `${baseStyle} ${colorStyles[color]}`;
};

const CompanyCard: React.FC<CompanyCardProps> = ({ company }) => {
  const [isHovered, setIsHovered] = useState(false);
  const navigate = useNavigate();
  
  const { 
    name,
    logoUrl,
    logoIconClass,
    fundingStage,
    tags,
    industry,
    fundingAsk,
    valuation
  } = company;

  let fundingStageColor: 'green' | 'yellow' | 'purple' = 'green';
  if (fundingStage?.toLowerCase().includes('series a')) {
    fundingStageColor = 'yellow';
  } else if (fundingStage?.toLowerCase().includes('growth')) {
    fundingStageColor = 'purple';
  }

  const handleCardClick = () => {
    navigate(`/companies/${encodeURIComponent(name.toLowerCase())}/analysis`);
  };

  return (
    <div
      className="relative transition-all duration-300 shadow-lg hover:shadow-xl rounded-2xl overflow-hidden cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleCardClick}
      style={{
        transform: isHovered ? 'scale(1.02) translateY(-4px)' : 'translateY(0)',
      }}
    >
      {/* Image Container with Overlay */}
      <div className="relative w-full h-52 overflow-hidden">
        {/* Background Image */}
        {logoUrl ? (
          <>
            <img 
              src={logoUrl} 
              alt={`${name} background`} 
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-black/40 to-black/70"></div>
          </>
        ) : (
          <div className="w-full h-full bg-gradient-to-b from-purple-light/30 to-purple-dark/70"></div>
        )}
        
        {/* Logo in bottom left corner */}
        <div className="absolute bottom-4 left-4 flex items-center z-10">
          <div className="bg-white rounded-full p-1 shadow-md h-10 w-10 flex items-center justify-center mr-3">
            {logoUrl ? (
              <img 
                src={logoUrl} 
                alt={`${name} logo`} 
                className="h-8 w-8 object-contain rounded-full"
              />
            ) : (
              logoIconClass ? (
                <i className={`${logoIconClass} text-purple-dark opacity-90`}></i>
              ) : (
                <div className="font-bold text-xs text-purple-dark">{name.substring(0, 2)}</div>
              )
            )}
          </div>
          <h3 className="font-medium text-white text-lg truncate max-w-[70%]">{name}</h3>
        </div>
        
        {/* Funding Stage Badge */}
        {fundingStage && (
          <div className="absolute top-4 right-4 z-10">
            <span className={`${getBadgeStyles(fundingStageColor)} shadow-md`}>{fundingStage}</span>
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-5 flex flex-col flex-grow bg-white">
        {/* Signal Type - Like Acquisition Prediction */}
        <div className="mb-3">
          <div className="inline-flex items-center bg-purple-light/20 text-purple-dark px-3 py-1.5 rounded-full text-sm font-medium">
            <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none">
              <path d="m 4,16 c 0.63,0 1.22,0.16 1.74,0.42 0.01,-0.02 0.02,-0.04 0.03,-0.05 l 4.25,-4.25 C 10.02,12.08 10,12.04 10,12 c 0,-0.02 0.01,-0.03 0.01,-0.04 L 5.76,7.71 C 5.73,7.68 5.72,7.65 5.7,7.61 5.18,7.85 4.61,8 4,8 1.79,8 0,6.21 0,4 0,1.79 1.79,0 4,0 6.21,0 8,1.79 8,4 8,4.88 7.71,5.69 7.23,6.35 l 4.51,4.51 c 0.04,0.04 0.06,0.1 0.1,0.15 H 16 c 0.05,0 0.09,0.02 0.13,0.03 C 16.57,9.29 18.13,8 20,8 c 2.21,0 4,1.79 4,4 0,2.21 -1.79,4 -4,4 -1.87,0 -3.43,-1.29 -3.87,-3.03 C 16.09,12.98 16.05,13 16,13 h -4.03 l -4.7,4.7 C 7.73,18.35 8,19.14 8,20 8,22.21 6.21,24 4,24 1.79,24 0,22.21 0,20 0,17.79 1.79,16 4,16 Z" fill="currentColor"/>
            </svg>
            <span>Investment Opportunity</span>
          </div>
        </div>
        
        {/* Tags */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {tags && tags.length > 0 ? tags.slice(0, 3).map(tag => (
            <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">{tag}</span>
          )) : (
            industry && <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">{industry}</span>
          )}
        </div>

        {/* Funding Ask and Valuation Section */}
        {(fundingAsk || valuation) && (
          <div className="mt-auto pt-3 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-x-4 text-xs text-gray-600">
              {fundingAsk && (
                <div>
                  <p className="font-medium text-gray-700">Funding Ask</p>
                  <p className="text-purple font-semibold">
                    {typeof fundingAsk === 'number' ? `$${fundingAsk.toLocaleString()}` : fundingAsk}
                  </p>
                </div>
              )}
              {valuation && (
                <div>
                  <p className="font-medium text-gray-700">Valuation</p>
                  <p className="text-purple font-semibold">
                    {typeof valuation === 'number' ? `$${valuation.toLocaleString()}` : valuation}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompanyCard; 