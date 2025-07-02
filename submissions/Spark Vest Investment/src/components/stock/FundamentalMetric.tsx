
import React from 'react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { HelpCircle } from 'lucide-react';

interface FundamentalMetricProps {
  label: string;
  value: string;
  trend?: 'up' | 'down' | 'neutral';
  description?: string;
}

const FundamentalMetric = ({ label, value, trend, description }: FundamentalMetricProps) => {
  return (
    <div className="flex justify-between items-center border-b border-white/10 pb-3 mb-3 group hover:bg-white/5 transition-colors px-2 py-1 rounded-sm">
      <div className="flex items-center gap-1">
        <span className="text-sm text-muted-foreground">{label}</span>
        {description && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <HelpCircle className="h-3 w-3 text-muted-foreground opacity-70 cursor-help" />
              </TooltipTrigger>
              <TooltipContent side="right" className="max-w-[220px]">
                <p className="text-xs">{description}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>
      <span className={`text-sm font-medium ${
        trend === 'up' ? 'text-green-500' : 
        trend === 'down' ? 'text-red-500' : ''
      }`}>{value}</span>
    </div>
  );
};

export default FundamentalMetric;
