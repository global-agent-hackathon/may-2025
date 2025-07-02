export type ConnectionStatus = 'private' | 'connected' | 'pending' | 'public';

export interface Company {
  id: string;
  logoUrl: string;
  name: string;
  industry: string;
  location: string;
  foundedYear: number;
  tagline: string;
  shortDescription: string; // Added based on image card content
  metrics: {
    series?: string;
    employees?: number;
    arr?: string | number;
    keyFocus?: string;
    fundingAsk?: string | number; // From image
    valuation?: string | number; // From image
  };
  tags?: string[]; // From image (e.g., AI, Logistics, SaaS)
  connectionStatus: ConnectionStatus;
  description?: string;
  teamInfo?: string;
  fundingInfo?: string;
  documentCount?: number;
  isChatReady?: boolean;
  stage?: string; // From image (e.g., Seed Stage, Series A)
}

export interface FilterOption {
  id: string;
  name: string;
  type: 'industry' | 'stage';
}

export interface FilterType extends FilterOption {} 