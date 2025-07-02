
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Info, Briefcase } from 'lucide-react';
import FundamentalMetric from './FundamentalMetric';
import FundamentalsInfoDialog from './FundamentalsInfoDialog';
import { useQuery } from '@tanstack/react-query';
import { StockAnalysis } from '@/lib/types';

// Descriptions for tooltips
const metricDescriptions = {
  marketCap: "Total value of all outstanding shares",
  peRatio: "Price to Earnings ratio - measures company valuation relative to its earnings",
  pbRatio: "Price to Book ratio - compares market value to book value",
  industryPE: "Average P/E ratio for the industry",
  evToEBITDA: "Enterprise Value to EBITDA - valuation multiple",
  roe: "Return on Equity - measures profitability relative to shareholder equity",
  roa: "Return on Assets - measures profitability relative to total assets",
  roic: "Return on Invested Capital - efficiency at allocating capital",
  operatingMargin: "Operating income divided by revenue",
  netMargin: "Net profit divided by revenue",
  debtToEquity: "Total debt divided by equity - measures financial leverage",
  currentRatio: "Current assets divided by current liabilities - liquidity measure",
  quickRatio: "Current assets minus inventory, divided by current liabilities",
  interestCoverage: "EBIT divided by interest expenses - ability to pay interest",
  eps: "Earnings Per Share - profit allocated to each share",
  bookValue: "Net asset value per share",
  dividendYield: "Annual dividend per share divided by share price",
  faceValue: "Original cost of the stock shown on certificate",
  beta: "Measure of volatility compared to the market",
  avgVolume: "Average daily trading volume",
  yearHigh: "Highest price in the last 52 weeks",
  yearLow: "Lowest price in the last 52 weeks",
}

// Format large numbers with appropriate suffixes
const formatNumber = (num: number): string => {
  if (num >= 1000000000000) {
    return `₹${(num / 1000000000000).toFixed(2)}T`;
  } else if (num >= 1000000000) {
    return `₹${(num / 1000000000).toFixed(2)}B`;
  } else if (num >= 1000000) {
    return `₹${(num / 1000000).toFixed(2)}M`;
  } else if (num >= 1000) {
    return `₹${(num / 1000).toFixed(2)}K`;
  } else {
    return `₹${num.toFixed(2)}`;
  }
};

const stock_url = import.meta.env.VITE_PUBLIC_SERVER_URL;
// Fetch stock fundamentals data
const fetchStockAnalysis = async (symbol: string): Promise<StockAnalysis> => {
  const response = await fetch(`${stock_url}stock-analysis/${symbol.toLowerCase()}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch stock analysis');
  }
  return response.json();
};

interface StockFundamentalsProps {
  stockSymbol?: string;
}

const StockFundamentals: React.FC<StockFundamentalsProps> = ({ stockSymbol = 'MSFT' }) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  
  // Remove the .NS extension if it exists
  const tickerSymbol = stockSymbol.split('.')[0];
  
  const { data: stockAnalysis, isLoading, error } = useQuery({
    queryKey: ['stockAnalysis', tickerSymbol],
    queryFn: () => fetchStockAnalysis(tickerSymbol),
    refetchOnWindowFocus: false,
    staleTime: 300000, // 5 minutes
  });

  if (isLoading) {
    return (
      <Card className="glass-panel">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Briefcase className="h-5 w-5" />
            Loading Fundamentals...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] flex items-center justify-center">
            <div className="animate-pulse space-y-4 w-full">
              {[1, 2, 3, 4, 5, 6].map((item) => (
                <div key={item} className="h-4 bg-gray-300/20 rounded w-full"></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="glass-panel">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-500">
            <Briefcase className="h-5 w-5" />
            Error Loading Fundamentals
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p>Failed to load stock fundamentals. Please try again later.</p>
            <Button 
              variant="outline" 
              className="mt-4"
              onClick={() => window.location.reload()}
            >
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stockAnalysis) {
    return null;
  }

  // Determine trends for certain metrics (you would ideally get this from historical data)
  const trends = {
    peRatio: stockAnalysis.financial_ratios.pe_ratio > 30 ? 'up' : 'down',
    roe: stockAnalysis.financial_ratios.roe > 25 ? 'up' : 'down',
    debtToEquity: stockAnalysis.financial_health.debt_to_equity < 1 ? 'down' : 'up',
    operatingMargin: stockAnalysis.financial_ratios.operating_margin > 30 ? 'up' : 'down',
    netMargin: stockAnalysis.financial_ratios.net_margin > 20 ? 'up' : 'down',
  };

  return (
    <Card className="glass-panel">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Briefcase className="h-5 w-5" />
            Fundamentals
          </CardTitle>
          <div className="text-sm text-muted-foreground">
            {stockAnalysis.symbol}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column */}
          <div>
            <h3 className="text-sm font-medium mb-3 text-primary">Valuation Metrics</h3>
            <div className="space-y-1">
              <FundamentalMetric 
                label="Market Cap" 
                value={formatNumber(stockAnalysis.market_cap)} 
                description={metricDescriptions.marketCap}
              />
              <FundamentalMetric 
                label="P/E Ratio (TTM)" 
                value={stockAnalysis.financial_ratios.pe_ratio.toFixed(2)} 
                trend={trends.peRatio as any}
                description={metricDescriptions.peRatio}
              />
              <FundamentalMetric 
                label="P/B Ratio" 
                value={stockAnalysis.financial_ratios.pb_ratio.toFixed(2)} 
                description={metricDescriptions.pbRatio}
              />
              <FundamentalMetric 
                label="EV/EBITDA" 
                value={stockAnalysis.financial_ratios.ev_ebitda.toFixed(2)} 
                description={metricDescriptions.evToEBITDA}
              />
            </div>
            
            <h3 className="text-sm font-medium mt-6 mb-3 text-primary">Performance Metrics</h3>
            <div className="space-y-1">
              <FundamentalMetric 
                label="ROE" 
                value={`${stockAnalysis.financial_ratios.roe.toFixed(2)}%`} 
                trend={trends.roe as any}
                description={metricDescriptions.roe}
              />
              <FundamentalMetric 
                label="ROA" 
                value={`${stockAnalysis.financial_ratios.roa.toFixed(2)}%`} 
                description={metricDescriptions.roa}
              />
              <FundamentalMetric 
                label="Operating Margin" 
                value={`${stockAnalysis.financial_ratios.operating_margin.toFixed(2)}%`} 
                trend={trends.operatingMargin as any}
                description={metricDescriptions.operatingMargin}
              />
              <FundamentalMetric 
                label="Net Margin" 
                value={`${stockAnalysis.financial_ratios.net_margin.toFixed(2)}%`} 
                trend={trends.netMargin as any}
                description={metricDescriptions.netMargin}
              />
            </div>
          </div>
          
          {/* Right Column */}
          <div>
            <h3 className="text-sm font-medium mb-3 text-primary">Financial Health</h3>
            <div className="space-y-1">
              <FundamentalMetric 
                label="Debt to Equity" 
                value={stockAnalysis.financial_health.debt_to_equity.toFixed(2)} 
                trend={trends.debtToEquity as any}
                description={metricDescriptions.debtToEquity}
              />
              <FundamentalMetric 
                label="Current Ratio" 
                value={stockAnalysis.financial_health.current_ratio.toFixed(2)} 
                description={metricDescriptions.currentRatio}
              />
              <FundamentalMetric 
                label="Quick Ratio" 
                value={stockAnalysis.financial_health.quick_ratio.toFixed(2)} 
                description={metricDescriptions.quickRatio}
              />
              <FundamentalMetric 
                label="Interest Coverage" 
                value={`${stockAnalysis.financial_health.interest_coverage.toFixed(2)}x`} 
                description={metricDescriptions.interestCoverage}
              />
            </div>
            
            <h3 className="text-sm font-medium mt-6 mb-3 text-primary">Per Share Data</h3>
            <div className="space-y-1">
              <FundamentalMetric 
                label="EPS (TTM)" 
                value={`$${stockAnalysis.per_share_metrics.eps.toFixed(2)}`} 
                description={metricDescriptions.eps}
              />
              <FundamentalMetric 
                label="Book Value" 
                value={`$${stockAnalysis.per_share_metrics.book_value.toFixed(2)}`} 
                description={metricDescriptions.bookValue}
              />
              <FundamentalMetric 
                label="Dividend Yield" 
                value={`${stockAnalysis.per_share_metrics.dividend_yield.toFixed(2)}%`} 
                description={metricDescriptions.dividendYield}
              />
              <FundamentalMetric 
                label="52-Week High" 
                value={`$${stockAnalysis.per_share_metrics.fifty_two_week_high.toFixed(2)}`} 
                description={metricDescriptions.yearHigh}
              />
              <FundamentalMetric 
                label="52-Week Low" 
                value={`$${stockAnalysis.per_share_metrics.fifty_two_week_low.toFixed(2)}`} 
                description={metricDescriptions.yearLow}
              />
            </div>
          </div>
        </div>
        
        <div className="mt-6 flex items-center justify-center">
          <Button 
            variant="ghost" 
            size="sm" 
            className="text-sm flex items-center"
            onClick={() => setDialogOpen(true)}
          >
            <span>Understand Fundamentals</span>
            <Info className="ml-1 h-4 w-4" />
          </Button>
        </div>

        {/* Fundamentals Info Dialog */}
        <FundamentalsInfoDialog 
          open={dialogOpen} 
          onOpenChange={setDialogOpen} 
        />
      </CardContent>
    </Card>
  );
};

export default StockFundamentals;
