
import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  BarChart4,
  Building, 
  Calculator
} from 'lucide-react';

interface FundamentalsInfoDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const FundamentalsInfoDialog = ({ open, onOpenChange }: FundamentalsInfoDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[625px] max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <BarChart4 className="h-5 w-5" />
            Understanding Stock Fundamentals
          </DialogTitle>
          <DialogDescription>
            A guide to the key financial metrics that help evaluate a company's performance and valuation.
          </DialogDescription>
        </DialogHeader>
        
        <ScrollArea className="pr-4 max-h-[calc(80vh-180px)]">
          <div className="space-y-6 py-4">
            {/* Valuation Metrics Section */}
            <div>
              <h3 className="font-semibold text-primary flex items-center gap-2 mb-3">
                <DollarSign className="h-4 w-4" />
                Valuation Metrics
              </h3>
              <p className="text-sm mb-4">
                These metrics help determine if a stock is undervalued or overvalued relative to its earnings, assets, or industry peers.
              </p>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium">Market Cap</h4>
                  <p className="text-sm text-muted-foreground">
                    Total market value of a company's outstanding shares. Calculated by multiplying the stock price by the total number of shares.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">P/E Ratio (Price to Earnings)</h4>
                  <p className="text-sm text-muted-foreground">
                    Compares a company's share price to its earnings per share. A higher P/E suggests investors expect higher growth in the future.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">P/B Ratio (Price to Book)</h4>
                  <p className="text-sm text-muted-foreground">
                    Compares a company's market value to its book value. A lower P/B ratio could indicate an undervalued stock.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">EV/EBITDA</h4>
                  <p className="text-sm text-muted-foreground">
                    Enterprise Value to Earnings Before Interest, Taxes, Depreciation, and Amortization. A lower ratio might suggest the company is undervalued.
                  </p>
                </div>
              </div>
            </div>
            
            {/* Performance Metrics Section */}
            <div>
              <h3 className="font-semibold text-primary flex items-center gap-2 mb-3">
                <TrendingUp className="h-4 w-4" />
                Performance Metrics
              </h3>
              <p className="text-sm mb-4">
                These metrics measure how efficiently a company is using its resources to generate profits.
              </p>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium">ROE (Return on Equity)</h4>
                  <p className="text-sm text-muted-foreground">
                    Measures how efficiently a company is using its equity to generate profits. Higher percentages indicate better performance.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">ROA (Return on Assets)</h4>
                  <p className="text-sm text-muted-foreground">
                    Shows how efficiently a company is using its assets to generate earnings. Higher values indicate better asset utilization.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Operating Margin</h4>
                  <p className="text-sm text-muted-foreground">
                    The percentage of revenue that remains after deducting operating expenses. Higher margins suggest better operational efficiency.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Net Margin</h4>
                  <p className="text-sm text-muted-foreground">
                    The percentage of revenue that translates into profit. A higher net margin indicates better profitability.
                  </p>
                </div>
              </div>
            </div>
            
            {/* Financial Health Section */}
            <div>
              <h3 className="font-semibold text-primary flex items-center gap-2 mb-3">
                <Building className="h-4 w-4" />
                Financial Health
              </h3>
              <p className="text-sm mb-4">
                These metrics evaluate a company's stability and ability to meet its financial obligations.
              </p>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium">Debt to Equity</h4>
                  <p className="text-sm text-muted-foreground">
                    Measures a company's financial leverage. A lower ratio indicates a company has less debt relative to its equity.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Current Ratio</h4>
                  <p className="text-sm text-muted-foreground">
                    Measures a company's ability to pay short-term obligations. A ratio above 1 indicates good short-term financial strength.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Quick Ratio</h4>
                  <p className="text-sm text-muted-foreground">
                    Similar to current ratio but excludes inventory. Provides a more stringent test of short-term liquidity.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Interest Coverage</h4>
                  <p className="text-sm text-muted-foreground">
                    Indicates how easily a company can pay interest on its outstanding debt. Higher values suggest better ability to meet interest payments.
                  </p>
                </div>
              </div>
            </div>
            
            {/* Per Share Data Section */}
            <div>
              <h3 className="font-semibold text-primary flex items-center gap-2 mb-3">
                <Calculator className="h-4 w-4" />
                Per Share Data
              </h3>
              <p className="text-sm mb-4">
                These metrics help investors understand what they're getting for each share they own.
              </p>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium">EPS (Earnings Per Share)</h4>
                  <p className="text-sm text-muted-foreground">
                    The portion of a company's profit allocated to each outstanding share. Higher EPS indicates better profitability.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Book Value</h4>
                  <p className="text-sm text-muted-foreground">
                    The net asset value of a company per share. Represents the minimum value of a company's equity.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Dividend Yield</h4>
                  <p className="text-sm text-muted-foreground">
                    The annual dividend payment divided by the share price. Higher yields indicate better income for shareholders.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">52-Week High & Low</h4>
                  <p className="text-sm text-muted-foreground">
                    The highest and lowest price at which the stock has traded in the past year. Helps gauge the stock's volatility and price range.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </ScrollArea>
        
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Close</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default FundamentalsInfoDialog;
