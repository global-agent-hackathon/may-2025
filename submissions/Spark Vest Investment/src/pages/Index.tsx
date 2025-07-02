import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { TrendingUp, ExternalLink } from 'lucide-react';
import { format} from 'date-fns';
import { useQuery } from '@tanstack/react-query';
import { ScrollArea } from "@/components/ui/scroll-area";

// Types for our price data
interface PriceData {
  date: string;
  price: number;
}

interface CryptoOption {
  id: string;
  name: string;
  symbol: string;
}

interface NewsItem {
  title: string;
  url: string;
}

const cryptoOptions: CryptoOption[] = [
  { id: 'bitcoin', name: 'Bitcoin', symbol: 'BTC' },
  { id: 'ethereum', name: 'Ethereum', symbol: 'ETH' },
  { id: 'binancecoin', name: 'BNB', symbol: 'BNB' },
  { id: 'ripple', name: 'XRP', symbol: 'XRP' },
];

// Function to fetch price data from CoinGecko
const fetchPriceData = async (cryptoId: string): Promise<PriceData[]> => {
  const endDate = new Date();
  const startDate = new Date(endDate.getTime() - (30 * 24 * 60 * 60 * 1000));
  const response = await fetch(
    `https://api.coingecko.com/api/v3/coins/${cryptoId}/market_chart/range?vs_currency=usd&from=${Math.floor(startDate.getTime() / 1000)}&to=${Math.floor(endDate.getTime() / 1000)}`,
    {
      headers: {
        'Accept': 'application/json',
      }
    }
  );
  
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  const data = await response.json();
  return data.prices.map(([timestamp, price]: [number, number]) => ({
    date: format(new Date(timestamp), 'MM/dd'),
    price: parseFloat(price.toFixed(2))
  }));
};

const stock_url = import.meta.env.VITE_PUBLIC_SERVER_URL;

const Index = () => {
  const [selectedCrypto, setSelectedCrypto] = useState<string>(cryptoOptions[0].id);
  const [newsData, setNewsData] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNewsData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${stock_url}stock-news`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const formattedNews = data.map(([title, url]: [string, string]) => ({
          title,
          url
        }));
        setNewsData(formattedNews);
        setError(null);
      } catch (error) {
        setError('Failed to fetch news data. Please try again later.');
        console.error('Failed to fetch news data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNewsData();
    const interval = setInterval(fetchNewsData, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const { data: priceData, isLoading: isPriceLoading } = useQuery({
    queryKey: ['cryptoPrice', selectedCrypto],
    queryFn: () => fetchPriceData(selectedCrypto),
    refetchInterval: 300000, // Refetch every 5 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="mb-12 text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-gradient animate-fade-in">
          Your Gateway to Smart Investing
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Track real-time crypto prices, analyze market trends, and make informed investment decisions.
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/register">
            <Button size="lg" className="hover-effect">
              Start Trading
              <TrendingUp className="ml-2 h-5 w-5" />
            </Button>
          </Link>
          <Link to="/about">
            <Button size="lg" variant="outline" className="hover-effect">
              Learn More
            </Button>
          </Link>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-2 gap-8 mb-12">
        {/* Price Chart Card */}
        <Card className="glass-panel p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Price Chart (30 Days)</h2>
            <Select
              value={selectedCrypto}
              onValueChange={setSelectedCrypto}
            >
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {cryptoOptions.map((crypto) => (
                  <SelectItem key={crypto.id} value={crypto.id}>
                    {crypto.symbol}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="h-[300px]">
            {isPriceLoading ? (
              <div className="h-full flex items-center justify-center">
                <p className="text-muted-foreground">Loading chart data...</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={priceData}>
                  <XAxis 
                    dataKey="date" 
                    stroke="#666"
                    tickLine={false}
                    axisLine={false}
                    fontSize={12}
                  />
                  <YAxis 
                    stroke="#666"
                    tickLine={false}
                    axisLine={false}
                    fontSize={12}
                    tickFormatter={(value) => `$${value.toLocaleString()}`}
                  />
                  <Tooltip 
                    contentStyle={{ background: '#1a1f2c', border: 'none' }}
                    formatter={(value: number) => [`$${value.toLocaleString()}`, 'Price']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="price" 
                    stroke="#9b87f5" 
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        {/* Market Updates Card */}
        <Card className="glass-panel p-6">
          <h3 className="text-2xl font-semibold mb-6">Latest Market News</h3>
          {loading ? (
            <div className="text-center py-4">Loading news...</div>
          ) : error ? (
            <div className="text-center text-red-500 py-4">{error}</div>
          ) : (
            <ScrollArea className="h-[300px] md:h-[300px] w-full">
              <div className="space-y-4 px-1">
                {newsData.map((news, index) => (
                  <div key={index} className="border-b border-border pb-4 last:border-0">
                    <a 
                      href={news.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="group flex items-start gap-2 hover:text-primary transition-colors"
                    >
                      <ExternalLink className="h-4 w-4 mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                      <h4 className="font-medium text-sm md:text-base">{news.title}</h4>
                    </a>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Index;