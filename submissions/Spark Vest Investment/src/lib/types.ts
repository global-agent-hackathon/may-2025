
export type AssistantType = 'general' | 'financial';
export type Message = { query: string; response: string };

// Stock API Types
export interface BasicStockInfo {
  symbol: string;
  name: string;
  currentPrice: number;
  previousClose: number;
  sector: string;
}

export interface StockAnalysis {
  symbol: string;
  company_name: string;
  current_price: number;
  market_cap: number;
  financial_ratios: {
    pe_ratio: number;
    pb_ratio: number;
    ev_ebitda: number;
    roe: number;
    roa: number;
    operating_margin: number;
    net_margin: number;
  };
  financial_health: {
    debt_to_equity: number;
    current_ratio: number;
    quick_ratio: number;
    interest_coverage: number;
  };
  per_share_metrics: {
    eps: number;
    book_value: number;
    dividend_yield: number;
    fifty_two_week_low: number;
    fifty_two_week_high: number;
  };
}

export interface StockData {
  date: string;
  price: number;
  volume: number;
}
