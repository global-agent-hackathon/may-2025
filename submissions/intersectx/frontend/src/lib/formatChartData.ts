/**
 * Utility functions for formatting data for the company analysis charts
 */

/**
 * Format revenue timeseries data for charts
 */
export const formatRevenueData = (revenueData: any) => {
  if (!revenueData || !revenueData.revenue_timeseries) {
    return [];
  }

  return revenueData.revenue_timeseries.map((item: any) => ({
    date: item.period_start,
    value: item.value / 1000000, // Convert to millions
    label: `${new Date(item.period_start).toLocaleDateString()} - ${new Date(item.period_end).toLocaleDateString()}`
  }));
};

/**
 * Format expense data for charts
 */
export const formatExpensesData = (expensesData: any) => {
  if (!expensesData || !expensesData.expenses) {
    return [];
  }

  return expensesData.expenses.map((item: any) => ({
    name: item.category,
    value: item.value / 1000000 // Convert to millions
  }));
};

/**
 * Format funding data for charts
 */
export const formatFundingData = (fundingData: any) => {
  if (!fundingData || !fundingData.funding_rounds) {
    return [];
  }

  return fundingData.funding_rounds.map((item: any) => ({
    date: item.date,
    value: item.value / 1000000, // Convert to millions
    name: item.round_type,
    label: `${item.round_type} - ${new Date(item.date).toLocaleDateString()}`
  }));
};

/**
 * Format margin data for charts
 */
export const formatMarginsData = (marginsData: any) => {
  if (!marginsData || !marginsData.margins) {
    return [];
  }

  return marginsData.margins.map((item: any) => ({
    name: item.margin_type,
    value: item.value * 100 // Convert to percentage
  }));
};

/**
 * Format team data for charts
 */
export const formatTeamData = (teamData: any) => {
  if (!teamData || !teamData.roles_breakdown) {
    return [];
  }

  return teamData.roles_breakdown.map((item: any) => ({
    name: item.role,
    value: item.count,
    percentage: item.percentage
  }));
};

/**
 * Format team growth data for charts
 */
export const formatTeamGrowthData = (teamGrowthData: any) => {
  if (!teamGrowthData || !teamGrowthData.team_growth_timeseries) {
    return [];
  }

  return teamGrowthData.team_growth_timeseries.map((item: any) => ({
    date: item.period_start,
    hires: item.hires,
    attrition: item.attrition,
    netGrowth: item.net_growth,
    growthRate: item.growth_rate * 100 // Convert to percentage
  }));
};

/**
 * Format market share data for charts
 */
export const formatMarketShareData = (marketData: any) => {
  if (!marketData || !marketData.market_size) {
    return [];
  }

  return marketData.market_size.map((item: any) => ({
    name: item.industry,
    value: item.percentage
  }));
};

/**
 * Format competitive analysis data for charts
 */
export const formatCompetitiveData = (competitiveData: any) => {
  if (!competitiveData || !competitiveData.top_competitors) {
    return [];
  }

  return competitiveData.top_competitors.map((item: any) => ({
    name: item.company_name,
    marketShare: item.market_share,
    revenue: item.revenue / 1000000, // Convert to millions
    growthRate: item.growth_rate * 100 // Convert to percentage
  }));
};

/**
 * Format growth projections data for charts
 */
export const formatGrowthProjectionsData = (growthData: any) => {
  if (!growthData || !growthData.projections_timeseries) {
    return [];
  }

  return growthData.projections_timeseries.map((item: any) => ({
    date: item.period_start,
    value: item.projected_value / 1000000, // Convert to millions
    metric: item.metric
  }));
};

/**
 * Format sentiment data for charts
 */
export const formatSentimentData = (sentimentData: any) => {
  if (!sentimentData || !sentimentData.sentiment_timeseries) {
    return [];
  }

  return sentimentData.sentiment_timeseries.map((item: any) => ({
    date: item.period_start,
    score: item.sentiment_score,
    positive: item.positive,
    negative: item.negative,
    neutral: item.neutral
  }));
};

/**
 * Format currency for display
 */
export const formatCurrency = (value: number) => {
  if (!value && value !== 0) return 'N/A';
  
  if (value >= 1000000000) {
    return `$${(value / 1000000000).toFixed(1)}B`;
  } else if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(1)}M`;
  } else if (value >= 1000) {
    return `$${(value / 1000).toFixed(1)}K`;
  } else {
    return `$${value.toFixed(0)}`;
  }
};

/**
 * Format percentage for display
 */
export const formatPercentage = (value: number) => {
  if (!value && value !== 0) return 'N/A';
  return `${value.toFixed(1)}%`;
}; 