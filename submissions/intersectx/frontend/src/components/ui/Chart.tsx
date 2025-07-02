import React from 'react';

type ChartType = 'line' | 'bar' | 'pie' | 'donut' | 'area';

interface ChartProps {
  type: ChartType;
  title: string;
  description?: string;
  data: any;
  className?: string;
}

export const Chart: React.FC<ChartProps> = ({ type, title, description, data, className }) => {
  // This is a placeholder component that would be replaced with an actual chart library like Chart.js or Recharts
  return (
    <div className={`bg-white rounded-lg p-4 ${className}`}>
      <div className="mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {description && <p className="text-sm text-gray-500">{description}</p>}
      </div>
      
      <div className="h-52 bg-gray-100 rounded-md flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-500 mb-2">{type.charAt(0).toUpperCase() + type.slice(1)} Chart</div>
          <p className="text-sm text-gray-400">
            Chart visualization would be rendered here with {JSON.stringify(data).slice(0, 40)}...
          </p>
        </div>
      </div>
    </div>
  );
};

export default Chart; 