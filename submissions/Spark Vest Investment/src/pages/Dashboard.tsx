import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { ArrowUpRight, ArrowDownRight, Search, AlertTriangle } from 'lucide-react';
import StockFundamentals from '@/components/stock/StockFundamentals';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useQuery } from '@tanstack/react-query';
import { BasicStockInfo, StockData } from '@/lib/types';
import { useToast } from '@/components/ui/use-toast';

// Available stock options for search
const stockOptions = [
  { id: 'MSFT', name: 'Microsoft Corporation' },
  { id: 'AAPL', name: 'Apple Inc.' },
  { id: 'GOOGL', name: 'Alphabet Inc.' },
  { id: 'AMZN', name: 'Amazon.com Inc.' },
  { id: 'META', name: 'Meta Platforms Inc.' },
  { id: 'NVDA', name: 'NVIDIA Corporation' },
  { id: 'TSLA', name: 'Tesla Inc.' },
  { id: 'PYPL', name: 'PayPal Holdings Inc.' },
  { id: 'NFLX', name: 'Netflix Inc.' },
];

const stock_url = import.meta.env.VITE_PUBLIC_SERVER_URL;

// Fetch basic stock info
const fetchStockInfo = async (symbol: string): Promise<BasicStockInfo> => {
  const response = await fetch(`${stock_url}stock/${symbol.toLowerCase()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch stock info');
  }
  return response.json();
};

// Generate mock stock price data based on current price and previous close
const generateMockPriceData = (stockInfo: BasicStockInfo, timeframe: string): StockData[] => {
  const currentPrice = stockInfo.currentPrice;
  const previousClose = stockInfo.previousClose;
  const priceDiff = currentPrice - previousClose;
  const volatility = Math.abs(priceDiff) * 0.3; // Use price difference to determine volatility
  
  const now = new Date();
  let dataPoints: StockData[] = [];
  
  // Generate hourly data for the last day
  for (let i = 0; i < 8; i++) {
    const date = new Date(now);
    date.setHours(9 + i);
    date.setMinutes(0);
    date.setSeconds(0);
    
    // Price trends upwards or downwards based on the actual daily change
    const progress = i / 7; // 0 to 1 as the day progresses
    const randomFactor = (Math.random() - 0.5) * volatility;
    const price = previousClose + (priceDiff * progress) + randomFactor;
    
    dataPoints.push({
      date: date.toISOString(),
      price: Number(price.toFixed(2)),
      volume: Math.floor(100000 + Math.random() * 900000)
    });
  }
  return dataPoints;
};

const Dashboard = () => {
  const [selectedStock, setSelectedStock] = useState('MSFT');
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredStocks, setFilteredStocks] = useState(stockOptions);
  const [showResults, setShowResults] = useState(false);
  const [customTicker, setCustomTicker] = useState('');
  const { toast } = useToast();
  
  // Query for stock information
  const { 
    data: stockInfo, 
    isLoading: isStockInfoLoading, 
    error: stockInfoError,
    refetch: refetchStockInfo
  } = useQuery({
    queryKey: ['stockInfo', selectedStock],
    queryFn: () => fetchStockInfo(selectedStock),
    staleTime: 60000, // 1 minute
    refetchOnWindowFocus: false,
  });
  
  // Generate chart data based on stock info - using 'daily' as fixed timeframe
  const chartData = stockInfo ? generateMockPriceData(stockInfo, 'daily') : [];
  
  // Handle errors
  useEffect(() => {
    if (stockInfoError) {
      toast({
        title: "Error loading stock data",
        description: "Could not fetch the stock information. Please try again later.",
        variant: "destructive",
      });
    }
  }, [stockInfoError, toast]);
  
  // Handle search input changes
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    setCustomTicker(query);
    
    if (query.trim() === '') {
      setFilteredStocks(stockOptions);
    } else {
      const filtered = stockOptions.filter(
        stock => stock.name.toLowerCase().includes(query.toLowerCase()) || 
                stock.id.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredStocks(filtered);
    }
    
    setShowResults(query.trim() !== '');
  };
  
  // Handle stock selection
  const handleSelectStock = (stockId: string) => {
    setSelectedStock(stockId);
    setSearchQuery(stockOptions.find(s => s.id === stockId)?.name || stockId);
    setShowResults(false);
    refetchStockInfo();
  };

  // Handle custom stock search
  const handleSearch = () => {
    // If the search query matches one of our predefined options, use that
    const matchedStock = stockOptions.find(
      s => s.id.toLowerCase() === searchQuery.toLowerCase() || 
           s.name.toLowerCase() === searchQuery.toLowerCase()
    );
    
    if (matchedStock) {
      handleSelectStock(matchedStock.id);
    } else if (customTicker.trim() !== '') {
      // Otherwise use the custom ticker (could be any valid stock symbol)
      const ticker = customTicker.trim().toUpperCase();
      setSelectedStock(ticker);
      refetchStockInfo();
      setShowResults(false);
    }
  };

  // Handle pressing Enter in the search box
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Calculate price change for display
  const calculateChange = () => {
    if (!stockInfo) return { change: '0.00', percentChange: '0.00', isPositive: true };
    
    const currentPrice = stockInfo.currentPrice;
    const previousClose = stockInfo.previousClose;
    const change = currentPrice - previousClose;
    const percentChange = (change / previousClose) * 100;
    
    return {
      change: change.toFixed(2),
      percentChange: percentChange.toFixed(2),
      isPositive: change >= 0
    };
  };

  const priceChange = calculateChange();
  
  if (isStockInfoLoading) {
    return (
      <div className="py-8 space-y-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Dashboard</h1>
        </div>
        <div className="flex items-center justify-center h-[400px]">
          <div className="text-center flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
            <p className="text-muted-foreground">Loading dashboard data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (stockInfoError) {
    return (
      <div className="py-8 space-y-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Dashboard</h1>
        </div>
        <div className="flex items-center justify-center h-[400px]">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">Failed to load dashboard</h2>
            <p className="text-muted-foreground mb-4">There was an error loading the stock data.</p>
            <Button onClick={() => refetchStockInfo()}>Try Again</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-8 space-y-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
      </div>

      {/* Search Bar */}
      <div className="w-full relative">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search stocks..."
              value={searchQuery}
              onChange={handleSearchChange}
              onKeyPress={handleKeyPress}
              className="pl-9 w-full"
            />
            {showResults && filteredStocks.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 p-2 bg-card border rounded-md shadow-lg z-10 max-h-60 overflow-y-auto">
                {filteredStocks.map(stock => (
                  <div 
                    key={stock.id}
                    className="p-2 hover:bg-accent rounded-md cursor-pointer"
                    onClick={() => handleSelectStock(stock.id)}
                  >
                    <div className="font-medium">{stock.name}</div>
                    <div className="text-xs text-muted-foreground">{stock.id}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <Button onClick={handleSearch}>
            Search
          </Button>
        </div>
      </div>
            
      {/* Stock Summary Section */}
      
      <Card className="glass-panel">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>{stockInfo?.name} Performance</CardTitle>
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-medium ${priceChange.isPositive ? 'text-green-500' : 'text-red-500'}`}>
              {priceChange.isPositive ? '+' : ''}{priceChange.change} ({priceChange.isPositive ? '+' : ''}{priceChange.percentChange}%)
            </span>
            {priceChange.isPositive ? 
              <ArrowUpRight className="h-4 w-4 text-green-500" /> : 
              <ArrowDownRight className="h-4 w-4 text-red-500" />
            }
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="date" 
                  stroke="#888888" 
                  tickFormatter={(date) => new Date(date).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })} 
                />
                <YAxis 
                  stroke="#888888" 
                  domain={['auto', 'auto']}
                  tickFormatter={(value) => `$${value}`}
                />
                <Tooltip 
                  formatter={(value, name) => [
                    `$${value}`, name === 'price' ? 'Price' : 'Volume'
                  ]}
                  labelFormatter={(label) => new Date(label).toLocaleString(undefined, { 
                    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
                  })}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 6 }}
                  name="Price"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Stock Fundamentals Section */}
      <StockFundamentals stockSymbol={selectedStock} />
    </div>
  );
};

export default Dashboard;
