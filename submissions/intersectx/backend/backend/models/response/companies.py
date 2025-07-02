from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CompanyBaseInfo(BaseModel):
    name: str = Field(..., description="Name of the company")
    logo: str = Field(..., description="URL to the company logo image")
    founder: str = Field(..., description="Name of the founder")
    headquarters: str = Field(..., description="Headquarters location")
    founding_date: datetime = Field(..., description="Founding Date of the company")
    members_count: int = Field(..., description="Number of members in the company")


class DocumentInfo(BaseModel):
    id: str
    name: str
    type: str
    uploadDate: str
    analysis: str


class DocumentProcessing(BaseModel):
    summary: str
    keyFindings: list[str]
    documents: list[DocumentInfo]


class TeamMember(BaseModel):
    name: str
    role: str
    background: str
    linkedin: str


class TeamAnalysis(BaseModel):
    founders: list[TeamMember]
    keyTeamMembers: list[TeamMember]


class MarketIntelligence(BaseModel):
    marketSize: float
    growthRate: float
    trends: list[str]
    opportunities: list[str]


class Competitor(BaseModel):
    name: str
    strength: str
    weakness: str


class CompetitiveLandscape(BaseModel):
    competitors: list[Competitor]
    marketPosition: str


class FinancialAnalysis(BaseModel):
    revenue: float
    funding: float
    valuation: float
    metrics: dict[str, str]


class RiskItem(BaseModel):
    category: str
    description: str
    severity: str
    mitigation: str


class RiskAssessment(BaseModel):
    risks: list[RiskItem]


class CompanyAnalysisCompanyInfo(BaseModel):
    name: str = Field(..., description="Name of the company")
    description: str = Field(..., description="Short description of the company")
    industry: str = Field(..., description="Industry sector of the company")
    foundingYear: int = Field(..., description="Year the company was founded")
    headquarters: str = Field(..., description="Headquarters location")
    website: str = Field(..., description="Company website URL")
    logo: str = Field(..., description="URL to the company logo image")


class CompanyAnalysis(BaseModel):
    documentProcessing: DocumentProcessing = Field(
        ..., description="Analysis and summary of company documents"
    )
    teamAnalysis: TeamAnalysis = Field(
        ..., description="Analysis of founders and key team members"
    )
    marketIntelligence: MarketIntelligence = Field(
        ..., description="Market size, growth, trends, and opportunities"
    )
    competitiveLandscape: CompetitiveLandscape = Field(
        ..., description="Competitors and market position analysis"
    )
    financialAnalysis: FinancialAnalysis = Field(
        ..., description="Financial metrics, revenue, funding, and valuation"
    )
    riskAssessment: RiskAssessment = Field(
        ..., description="Identified risks and mitigation strategies"
    )


class CompanyAnalysisFullResponse(BaseModel):
    company: CompanyAnalysisCompanyInfo = Field(
        ..., description="Basic information about the company"
    )
    analysis: CompanyAnalysis = Field(
        ..., description="Detailed analysis of the company"
    )


class GradientColors(BaseModel):
    from_color: str = Field(
        "from-teal-600", alias="from", description="Tailwind CSS 'from' gradient class"
    )
    to: str = Field("to-teal-700", description="Tailwind CSS 'to' gradient class")

    class Config:
        populate_by_name = True


class FeaturedCompany(BaseModel):
    id: str = Field(..., description="Unique identifier for the company")
    name: str = Field(..., description="Name of the company")
    description: str = Field(..., description="Short description of the company")
    logo_url: str = Field(
        ..., alias="logoUrl", description="URL to the company logo image"
    )
    logo_text: str = Field(
        ..., alias="logoText", description="Text to display if no logo is available"
    )
    logo_sub_text: str | None = Field(
        None, alias="logoSubText", description="Optional secondary text for logo"
    )
    logo_icon_class: str | None = Field(
        None,
        alias="logoIconClass",
        description="Optional font awesome class if no logo",
    )
    funding_stage: str = Field(
        ..., alias="fundingStage", description="Company's funding stage"
    )
    tags: list[str] = Field(..., description="Tags related to the company")
    funding_ask: int = Field(
        500000, alias="fundingAsk", description="Amount of funding requested"
    )
    industry: str = Field(..., description="Industry sector of the company")
    valuation: int = Field(5000000, description="Company valuation")
    location: str = Field(..., description="Company location")
    gradient_colors: Optional[GradientColors] = Field(
        GradientColors(), alias="gradientColors", description="Gradient colors for UI"
    )

    class Config:
        populate_by_name = True


class FeaturedCompaniesResponse(BaseModel):
    companies: list[FeaturedCompany] = Field(
        ..., description="List of featured companies"
    )
    total: int = Field(..., description="Total number of companies")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of companies per page")


class CompanySearchResult(BaseModel):
    """Model for simplified company search results"""

    name: str = Field(..., description="Name of the company")
    logo_url: str = Field(..., alias="logoUrl", description="URL to the company logo")

    class Config:
        populate_by_name = True


class TopInvestorResponse(BaseModel):
    first_name: str = Field(..., description="First name of the investor")
    last_name: str = Field(..., description="Last name of the investor")
    linkedin_url: str = Field(..., description="LinkedIn URL of the investor")
    portfolio: int = Field(..., description="Investment Value Portfolio of the VC")
    companies_invested: int = Field(..., description="Number of companies invested in")
    email: str = Field(..., description="Email of the investor")


class TopInvestorsListResponse(BaseModel):
    investors: list[TopInvestorResponse] = Field(
        ..., description="List of top investors"
    )
