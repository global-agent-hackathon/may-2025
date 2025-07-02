from pydantic import BaseModel, Field
from typing import Optional

from backend.models.response.finance import (
    RevenueAnalysisResponse,
    ExpenseAnalysisResponse,
    ProfitMarginsResponse,
    ValuationEstimationResponse,
    FundingHistoryResponse,
)
from backend.models.response.team import (
    TeamOverviewResponse,
    IndividualPerformanceResponse,
    OrgStructureResponse,
    TeamGrowthResponse,
)
from backend.models.response.market_analysis import (
    MarketTrendsResponse,
    CompetitiveAnalysisResponse,
    GrowthProjectionsResponse,
    RegionalTrendsResponse,
)
from backend.models.response.partnership_network import (
    PartnerListResponse,
    StrategicAlliancesResponse,
    NetworkStrengthResponse,
    PartnershipTrendsResponse,
)
from backend.models.response.regulatory_compliance import (
    ComplianceOverviewResponse,
    ViolationHistoryResponse,
    ComplianceRiskResponse,
    RegionalComplianceResponse,
)
from backend.models.response.customer_sentiment import (
    SentimentSummaryResponse,
    CustomerFeedbackResponse,
    BrandReputationResponse,
    SentimentComparisonResponse,
)
from backend.models.response.risk_analysis import (
    RegulatoryRisksResponse,
    MarketRisksResponse,
    OperationalRisksResponse,
    LegalRisksResponse,
)


class FinanceResponse(BaseModel):
    revenue: Optional[RevenueAnalysisResponse] = Field(
        None, description="Revenue analysis and timeseries data."
    )
    expenses: Optional[ExpenseAnalysisResponse] = Field(
        None, description="Expense analysis and category breakdowns."
    )
    margins: Optional[ProfitMarginsResponse] = Field(
        None, description="Profit margin analysis and breakdowns."
    )
    valuation: Optional[ValuationEstimationResponse] = Field(
        None, description="Company valuation estimates and timeseries."
    )
    funding: Optional[FundingHistoryResponse] = Field(
        None, description="Funding history and details of funding rounds."
    )


class LinkedInTeamResponse(BaseModel):
    team_overview: Optional[TeamOverviewResponse] = Field(
        None, description="Overview of the team, including size, roles, and locations."
    )
    individual_performance: Optional[IndividualPerformanceResponse] = Field(
        None, description="Performance metrics and background for key individuals."
    )
    org_structure: Optional[OrgStructureResponse] = Field(
        None, description="Organizational structure and leadership team."
    )
    team_growth: Optional[TeamGrowthResponse] = Field(
        None, description="Team growth, hiring, and attrition trends."
    )


class MarketAnalysisResponse(BaseModel):
    market_trends: Optional[MarketTrendsResponse] = Field(
        None, description="Trends and size of the relevant market."
    )
    competitive_analysis: Optional[CompetitiveAnalysisResponse] = Field(
        None, description="Analysis of competitors and market positioning."
    )
    growth_projections: Optional[GrowthProjectionsResponse] = Field(
        None, description="Growth projections and forecasts."
    )
    regional_trends: Optional[RegionalTrendsResponse] = Field(
        None, description="Regional trends and performance breakdowns."
    )


class PartnershipNetworkResponse(BaseModel):
    partner_list: Optional[PartnerListResponse] = Field(
        None, description="List of partners and partnership details."
    )
    strategic_alliances: Optional[StrategicAlliancesResponse] = Field(
        None, description="Strategic alliances and their impact."
    )
    network_strength: Optional[NetworkStrengthResponse] = Field(
        None, description="Strength and metrics of the partnership network."
    )
    partnership_trends: Optional[PartnershipTrendsResponse] = Field(
        None, description="Trends in partnerships over time."
    )


class RegulatoryComplianceResponse(BaseModel):
    compliance_overview: Optional[ComplianceOverviewResponse] = Field(
        None, description="Overview of compliance with key regulations."
    )
    violation_history: Optional[ViolationHistoryResponse] = Field(
        None, description="History of regulatory violations."
    )
    compliance_risk: Optional[ComplianceRiskResponse] = Field(
        None, description="Assessment of compliance risks."
    )
    regional_compliance: Optional[RegionalComplianceResponse] = Field(
        None, description="Compliance status by region."
    )


class CustomerSentimentResponse(BaseModel):
    sentiment_summary: Optional[SentimentSummaryResponse] = Field(
        None, description="Summary of customer sentiment and scores."
    )
    customer_feedback: Optional[CustomerFeedbackResponse] = Field(
        None, description="Customer feedback and qualitative insights."
    )
    brand_reputation: Optional[BrandReputationResponse] = Field(
        None, description="Brand reputation scores and trends."
    )
    sentiment_comparison: Optional[SentimentComparisonResponse] = Field(
        None, description="Comparison of sentiment with competitors."
    )


class RiskAnalysisResponse(BaseModel):
    regulatory_risks: Optional[RegulatoryRisksResponse] = Field(
        None, description="Risks related to regulatory compliance."
    )
    market_risks: Optional[MarketRisksResponse] = Field(
        None, description="Risks related to market conditions."
    )
    operational_risks: Optional[OperationalRisksResponse] = Field(
        None, description="Risks related to operations and supply chain."
    )
    legal_risks: Optional[LegalRisksResponse] = Field(
        None, description="Risks related to legal and intellectual property issues."
    )


class ResearchResponse(BaseModel):
    company_name: str = Field(..., description="The full name of the company.")
    finance: Optional[FinanceResponse] = Field(
        None,
        description="Detailed financial data for the company (revenue, expenses, margins, valuation, funding).",
    )
    linkedin_team: Optional[LinkedInTeamResponse] = Field(
        None,
        description="Team composition, org structure, leadership, and hiring trends.",
    )
    market_analysis: Optional[MarketAnalysisResponse] = Field(
        None,
        description="Market trends, projections, competitors, and regional growth analysis.",
    )


class ResearchResponseWithSummary(ResearchResponse):
    summary: str = Field(
        ...,
        description="A summary of the company's financial, organizational, and market-level information.",
    )
