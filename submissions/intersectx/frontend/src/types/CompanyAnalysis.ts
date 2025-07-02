export interface Revenue {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  revenue_timeseries: {
    currency: string;
    period_start: string;
    period_end: string;
    value: number;
    sources: string[];
    confidence: number;
  }[];
  total_revenue: number;
  last_updated: string | null;
  plot_url: string | null;
  summary?: string;
}

export interface Expense {
  category: string;
  value: number;
  currency: string;
  sources: string[];
  confidence: number;
}

export interface Expenses {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  expenses: Expense[];
  total_expense: number;
  last_updated: string;
  plot_url: string | null;
  summary?: string;
}

export interface Margin {
  margin_type: string;
  value: number;
  currency: string;
  sources: string[];
  confidence: number;
}

export interface Margins {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  margins: Margin[];
  last_updated: string;
  plot_url: string | null;
  summary?: string;
}

export interface Valuation {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  last_valuation: number;
  valuation_timeseries: {
    date: string;
    value: number;
    currency: string;
    sources: string[];
    confidence: number | null;
  }[];
  last_updated: string;
  plot_url: string | null;
  summary?: string;
}

export interface FundingRound {
  round_type: string;
  value: number;
  currency: string;
  date: string;
  lead_investors: string[] | null;
  sources: string[];
  confidence: number;
}

export interface Funding {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  funding_rounds: FundingRound[];
  total_funding: number;
  last_updated: string;
  plot_url: string | null;
  summary?: string;
}

export interface Finance {
  revenue?: Revenue;
  expenses?: Expenses;
  margins?: Margins;
  valuation?: Valuation;
  funding?: Funding;
}

export interface RoleBreakdown {
  role: string;
  count: number;
  percentage: number;
  sources: number[];
  confidence: number;
}

export interface TeamOverview {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  company_description: string;
  total_employees: number;
  roles_breakdown: RoleBreakdown[];
  locations: string[];
  key_hiring_areas: string[];
  growth_rate: number;
  sources: string[];
  last_updated: string;
  plot_url: string | null;
}

export interface IndividualPerformance {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  individual_name: string;
  title: string | null;
  image_url: string | null;
  tenure_years: number | null;
  performance_metrics: {
    metric: string;
    value: number;
    sources: number[];
    confidence: number;
  }[];
  previous_companies: {
    name: string;
    title: string;
    duration: string;
    dates: string;
  }[] | null;
  key_strengths: string[];
  development_areas: string[];
  education: {
    institution: string;
    degree: string;
    field_of_study: string;
    dates: string;
  }[] | null;
  sources: string[];
  last_updated: string;
  plot_url: string | null;
}

export interface OrgStructure {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  org_chart: {
    name: string;
    title: string;
    department: string;
    linkedin_url: string;
    reports_to: string | null;
    direct_reports: string[];
    sources: number[];
  }[];
  ceo: string;
  departments: {
    name: string;
    head: string;
    employee_count: number;
    sub_departments: string[] | null;
  }[];
  leadership_team: {
    name: string;
    title: string;
    linkedin_url: string;
    department: string;
  }[];
  sources: string[];
  last_updated: string;
  plot_url: string | null;
}

export interface TeamGrowth {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  team_growth_timeseries: {
    period_start: string;
    period_end: string;
    hires: number;
    attrition: number;
    net_growth: number;
    growth_rate: number;
    sources: number[];
    confidence: number | null;
  }[];
  total_hires: number;
  total_attrition: number;
  net_growth: number;
  growth_rate_annualized: number;
  key_hiring_areas: string[];
  attrition_by_department: {
    department: string;
    attrition_count: number;
    attrition_rate: number;
  }[];
  hiring_trends: {
    trend: string;
    description: string;
    supporting_data: any | null;
  }[];
  sources: string[];
  last_updated: string;
  plot_url: string | null;
}

export interface LinkedInTeam {
  team_overview?: TeamOverview;
  individual_performance?: IndividualPerformance;
  org_structure?: OrgStructure;
  team_growth?: TeamGrowth;
}

export interface MarketTrends {
  citations?: any[];
  iframe_url?: string;
  market_size: {
    percentage: number;
    industry: string;
    sources: any | null;
    confidence: any | null;
  }[];
  summary: string;
  last_updated: string;
  plot_url: string | null;
}

export interface Competitor {
  company_name: string;
  industry: string;
  market_share: number;
  revenue: number;
  growth_rate: number;
  strengths: string[];
  weaknesses: string[];
  differentiating_factors: string[];
  sources: string[];
  confidence: number;
}

export interface CompetitiveAnalysis {
  citations?: any[];
  iframe_url?: string;
  top_competitors: Competitor[];
  summary: string;
  last_updated: string;
  plot_url: string | null;
}

export interface GrowthProjections {
  citations?: any[];
  iframe_url?: string;
  projections_timeseries: {
    period_start: string;
    period_end: string;
    projected_value: number;
    metric: string;
    sources: any | null;
    confidence: any | null;
  }[];
  summary: string;
  sources: string[];
  last_updated: string;
  plot_url: string | null;
}

export interface RegionalTrends {
  citations?: any[];
  iframe_url?: string;
  regional_trends: {
    industry: string;
    region: string;
    period_start: string;
    period_end: string;
    value: number;
    metric: string;
    sources: string[];
    confidence: number;
  }[];
  summary: string;
  last_updated: string;
  plot_url: string;
  sources: string[];
}

export interface MarketAnalysis {
  market_trends?: MarketTrends;
  competitive_analysis?: CompetitiveAnalysis;
  growth_projections?: GrowthProjections;
  regional_trends?: RegionalTrends;
}

export interface SentimentSummary {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  product: string;
  region: string;
  sentiment_score: number;
  sentiment_breakdown: {
    positive: number;
    negative: number;
    neutral: number;
  };
  sentiment_timeseries: {
    period_start: string;
    period_end: string;
    positive: number;
    negative: number;
    neutral: number;
    sentiment_score: number;
    sources: string[];
    confidence: number;
  }[];
  summary: string;
  sources: string[];
  last_updated: string;
}

export interface CustomerFeedback {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  product: string;
  region: string;
  feedback_items: {
    date: string;
    customer: string;
    feedback: string;
    sentiment: string;
    sources: string[];
    confidence: number;
  }[];
  summary: string;
  sources: string[];
  last_updated: string;
}

export interface BrandReputation {
  citations?: any[];
  iframe_url?: string;
  company_name: string;
  region: string;
  reputation_score: number;
  reputation_timeseries: {
    period_start: string;
    period_end: string;
    reputation_score: number;
    sources: string[];
    confidence: number;
  }[];
  summary: string;
  sources: string[];
  last_updated: string;
}

export interface CustomerSentiment {
  sentiment_summary?: SentimentSummary;
  customer_feedback?: CustomerFeedback;
  brand_reputation?: BrandReputation;
}

export interface PartnerList {
  partners: {
    name: string;
    partnership_type: string;
    partnership_strength: number;
    start_date: string;
    description: string;
  }[];
  total_partners: number;
  sources: string[];
  last_updated: string;
  iframe_url?: string;
}

export interface PartnershipNetwork {
  partner_list?: PartnerList;
}

export interface ComplianceOverview {
  company_name: string;
  compliance_score: number;
  key_regulations: string[];
  last_audit_date: string;
  summary: string;
  sources: string[];
  last_updated: string;
  iframe_url?: string;
}

export interface RegulatoryCompliance {
  compliance_overview?: ComplianceOverview;
}

export interface RegulatoryRisks {
  company_name: string;
  regulatory_risk_score: number;
  risks: {
    risk_type: string;
    risk_level: string;
    description: string;
    mitigation_strategy: string;
    potential_impact: number;
  }[];
  summary: string;
  sources: string[];
  last_updated: string;
  iframe_url?: string;
}

export interface MarketRisks {
  company_name: string;
  market_risk_score: number;
  risks: {
    risk_type: string;
    risk_level: string;
    description: string;
    mitigation_strategy: string;
    potential_impact: number;
  }[];
  summary: string;
  sources: string[];
  last_updated: string;
  iframe_url?: string;
}

export interface RiskAnalysis {
  regulatory_risks?: RegulatoryRisks;
  market_risks?: MarketRisks;
}

export interface CompanyAnalysisData {
  company_name: string;
  finance?: Finance;
  linkedin_team?: LinkedInTeam;
  market_analysis?: MarketAnalysis;
  customer_sentiment?: CustomerSentiment;
  partnership_network?: PartnershipNetwork;
  regulatory_compliance?: RegulatoryCompliance;
  risk_analysis?: RiskAnalysis;
} 