import { useState, useEffect } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Star, Plus, Loader2 } from 'lucide-react';
import { useWatchlist } from '@/contexts/WatchlistContext';
import { useToast } from '@/components/ui/use-toast';
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { supabase } from '@/integrations/supabase/client';
import type { Database } from '@/types/supabase';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import TradingViewWidget from './TradingViewWidget';

interface StockData {
  symbol: string;
  name: string;
  currentPrice: number;
  previousClose: number;
  sector: string;
}

type CustomStock = Database['public']['Tables']['custom_stocks']['Row'];

const stock_url = import.meta.env.VITE_PUBLIC_SERVER_URL;

export default function MarketPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showStarredOnly, setShowStarredOnly] = useState(false);
  const [marketData, setMarketData] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStock, setSelectedStock] = useState<StockData | null>(null);
  const [showAddStock, setShowAddStock] = useState(false);
  const [newStockSymbol, setNewStockSymbol] = useState('');
  const [addingStock, setAddingStock] = useState(false);
  const { watchlist, addToWatchlist, removeFromWatchlist } = useWatchlist();
  const { toast } = useToast();

  // Filter stocks based on search query and starred filter
  const filteredStocks = marketData.filter(stock => {
    const matchesSearch = 
      stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      stock.name.toLowerCase().includes(searchQuery.toLowerCase());
    
    const isStarred = watchlist.some((item) => item.symbol === stock.symbol);
    
    return matchesSearch && (!showStarredOnly || isStarred);
  });
  
  const fetchCustomStocks = async (userId: string) => {
    try {
      const { data: customStocks, error } = await supabase
        .from('custom_stocks')
        .select('*')
        .eq('user_id', userId)
        .returns<CustomStock[]>();
      
      if (error) throw error;

      // Fetch data for each custom stock
      const customStockData = await Promise.all(
        (customStocks || []).map(async (stock: CustomStock) => {
          try {
            const response = await fetch(`${stock_url}stock/${stock.symbol}`);
            if (!response.ok) return null;
            return response.json();
          } catch {
            return null;
          }
        })
      );

      // Filter out any failed requests and add to market data
      const validStockData = customStockData.filter((data): data is StockData => data !== null);
      return validStockData;
    } catch (error) {
      console.error('Error fetching custom stocks:', error);
      return [];
    }
  };

  useEffect(() => {
    const fetchAllStockData = async () => {
      try {
        // Get current user
        const { data: { user }, error: userError } = await supabase.auth.getUser();
        if (userError) throw userError;

        if (!user) {
          throw new Error('No authenticated user found');
        }

        // Fetch default stocks
        const response = await fetch(`${stock_url}top-stocks`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const defaultStocks = await response.json();

        // Fetch custom stocks
        const customStocks = await fetchCustomStocks(user.id);

        // Combine both sets of stocks, avoiding duplicates
        const allStocks = [...defaultStocks];
        customStocks.forEach(customStock => {
          if (!allStocks.some(stock => stock.symbol === customStock.symbol)) {
            allStocks.push(customStock);
          }
        });

        setMarketData(allStocks);
        setError(null);
      } catch (error) {
        setError('Failed to fetch market data. Please try again later.');
        console.error('Failed to fetch market data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAllStockData();
    const interval = setInterval(fetchAllStockData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleWatchlistToggle = async (stock: StockData, isInWatchlist: boolean, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      if (isInWatchlist) {
        const watchlistItem = watchlist.find((item) => item.symbol === stock.symbol);
        if (watchlistItem) {
          await removeFromWatchlist(watchlistItem.id);
          toast({
            title: "Success",
            description: `${stock.symbol} removed from watchlist`,
          });
        }
      } else {
        await addToWatchlist(stock.symbol);
        toast({
          title: "Success",
          description: `${stock.symbol} added to watchlist`,
        });
      }
    } catch (error) {
      console.error('Watchlist operation failed:', error);
      toast({
        title: "Error",
        description: "Failed to update watchlist",
        variant: "destructive",
      });
    }
  };

  const handleAddStock = async () => {
    if (!newStockSymbol.trim()) {
      toast({
        title: "Error",
        description: "Please enter a stock symbol",
        variant: "destructive",
      });
      return;
    }

    setAddingStock(true);
    try {
      // Get current user
      const { data: { user }, error: userError } = await supabase.auth.getUser();
      if (userError) throw userError;

      if (!user) {
        throw new Error('No authenticated user found');
      }

      // Fetch stock data to validate
      const response = await fetch(`${stock_url}stock/${newStockSymbol.toUpperCase()}`);
      if (!response.ok) {
        throw new Error(`Stock not found or invalid symbol`);
      }
      const stockData = await response.json();
      
      // Check if stock already exists
      if (marketData.some(stock => stock.symbol === stockData.symbol)) {
        toast({
          title: "Info",
          description: "This stock is already in your list",
        });
        return;
      }

      // Save to custom_stocks table
      const { error: insertError } = await supabase
        .from('custom_stocks')
        .insert({ 
          symbol: stockData.symbol,
          user_id: user.id
        });

      if (insertError) throw insertError;

      // Update local state
      setMarketData(prev => [...prev, stockData]);
      setNewStockSymbol('');
      setShowAddStock(false);
      toast({
        title: "Success",
        description: `${stockData.symbol} has been added to your list`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add stock",
        variant: "destructive",
      });
    } finally {
      setAddingStock(false);
    }
  };

  return (
    <>
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Market</h1>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search stocks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="starred-filter"
                checked={showStarredOnly}
                onCheckedChange={setShowStarredOnly}
              />
              <Label htmlFor="starred-filter">Show Starred Only</Label>
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setShowAddStock(true)}
              title="Add Custom Stock"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {loading && marketData.length === 0 ? (
          <div className="py-8 text-center">Loading market data...</div>
        ) : error ? (
          <div className="py-8 text-center text-red-500">{error}</div>
        ) : marketData.length === 0 ? (
          <div className="text-center py-4">No stocks data available</div>
        ) : filteredStocks.length === 0 ? (
          <div className="text-center py-4">
            {showStarredOnly 
              ? "No starred stocks found" 
              : "No stocks match your search criteria"}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredStocks.map((stock) => {
              const priceChange = stock.currentPrice - stock.previousClose;
              const percentageChange = ((priceChange / stock.previousClose) * 100).toFixed(2);
              const isInWatchlist = watchlist.some((item) => item.symbol === stock.symbol);

              return (
                <Card 
                  key={stock.symbol} 
                  className="glass-panel hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => setSelectedStock(stock)}
                >
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold">{stock.symbol}</h3>
                        <p className="text-sm text-muted-foreground">{stock.name}</p>
                        <p className="text-xs text-muted-foreground">{stock.sector}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="flex-none"
                        onClick={(e) => handleWatchlistToggle(stock, isInWatchlist, e)}
                      >
                        <Star className={`h-5 w-5 ${isInWatchlist ? "fill-yellow-500 text-yellow-500" : ""}`} />
                      </Button>
                    </div>
                    <div className="mt-4">
                      <p className="text-2xl font-bold tabular-nums">${stock.currentPrice.toFixed(2)}</p>
                      <p className={`text-lg tabular-nums ${priceChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {priceChange >= 0 ? '+' : ''}
                        {percentageChange}%
                      </p>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        <Dialog open={!!selectedStock} onOpenChange={() => setSelectedStock(null)}>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>
                {selectedStock?.symbol} - {selectedStock?.name}
              </DialogTitle>
            </DialogHeader>
            {selectedStock && (
              <div className="mt-4">
                <TradingViewWidget symbol={selectedStock.symbol} />
              </div>
            )}
          </DialogContent>
        </Dialog>

        <Dialog open={showAddStock} onOpenChange={setShowAddStock}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Custom Stock</DialogTitle>
              <DialogDescription>
                Enter a stock symbol to add it to your list
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <Input
                placeholder="Enter stock symbol (e.g., AAPL)"
                value={newStockSymbol}
                onChange={(e) => setNewStockSymbol(e.target.value.toUpperCase())}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !addingStock) {
                    handleAddStock();
                  }
                }}
              />
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setShowAddStock(false)}
                disabled={addingStock}
              >
                Cancel
              </Button>
              <Button
                onClick={handleAddStock}
                disabled={addingStock || !newStockSymbol.trim()}
              >
                {addingStock ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Adding...
                  </>
                ) : (
                  'Add Stock'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </>
  );
}