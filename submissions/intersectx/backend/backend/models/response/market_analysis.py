from pydantic import BaseModel
from typing import Optional, List
from pydantic import Field
from backend.models.response.base import CitationResponse
from backend.plot.types import ChartData


# --- Market Trends ---
class MarketSize(BaseModel):
    percentage: float = Field(
        ..., description="The market size in the primary currency"
    )
    industry: str = Field(..., description="The industry the market size belongs to")
    sources: Optional[list[str]] = Field(
        None, description="List of sources or references for this revenue data point"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class MarketTrendsResponse(CitationResponse):
    market_size: List[MarketSize] = Field(
        ...,
        description="List of market size data points showing market size over different periods",
    )
    summary: str = Field(..., description="Summary of the market trend")
    last_updated: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp indicating when this analysis was last updated",
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {"industry": m.industry, "percentage": m.percentage}
            for m in self.market_size
        ]
        return ChartData(
            data=data,
            title="Market Size by Industry",
            x="industry",
            y="percentage",
            kind="pie",
        )


# --- Competitive Analysis ---
class CompetitorProfile(BaseModel):
    company_name: str = Field(..., description="The name of the company")
    industry: Optional[str] = Field(None, description="The industry of the company")
    market_share: Optional[float] = Field(
        None, description="The market share of the company"
    )
    revenue: Optional[float] = Field(None, description="The revenue of the company")
    growth_rate: Optional[float] = Field(
        None, description="The growth rate of the company"
    )
    strengths: Optional[list[str]] = Field(
        None, description="The strengths of the company"
    )
    weaknesses: Optional[list[str]] = Field(
        None, description="The weaknesses of the company"
    )
    differentiating_factors: Optional[list[str]] = Field(
        None, description="The differentiating factors of the company"
    )
    sources: Optional[list[str]] = Field(
        None, description="List of sources or references for this revenue data point"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class CompetitiveAnalysisResponse(CitationResponse):
    top_competitors: list[CompetitorProfile] = Field(
        ...,
        description="List of top competitors for the company",
    )
    summary: Optional[str] = Field(
        None,
        description="Summary of the competitive analysis",
    )
    last_updated: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp indicating when this analysis was last updated",
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {"company_name": c.company_name, "market_share": c.market_share or 0}
            for c in self.top_competitors
        ]
        return ChartData(
            data=data,
            title="Competitor Market Share",
            x="company_name",
            y="market_share",
            kind="bar",
        )


# --- Growth Projections ---
class GrowthProjectionTimeSeriesPoint(BaseModel):
    period_start: str = Field(..., description="The start date of the period")
    period_end: str = Field(..., description="The end date of the period")
    projected_value: float = Field(
        ..., description="The projected value for the period"
    )
    metric: str = Field(..., description="The metric being projected")
    sources: Optional[list[str]] = Field(
        None, description="List of sources or references for this revenue data point"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class GrowthProjectionsResponse(CitationResponse):
    projections_timeseries: List[GrowthProjectionTimeSeriesPoint] = Field(
        ..., description="List of projected values for the company"
    )
    summary: Optional[str] = Field(
        None, description="Summary of the growth projections"
    )
    sources: Optional[list[str]] = Field(
        None, description="List of sources or references for this revenue data point"
    )
    last_updated: Optional[str] = None

    def get_plot_data(self) -> ChartData:
        data = [
            {"period_start": p.period_start, "projected_value": p.projected_value}
            for p in self.projections_timeseries
        ]
        return ChartData(
            data=data,
            title="Growth Projections Over Time",
            x="period_start",
            y="projected_value",
            kind="area",
        )


# --- Regional Trends ---
class RegionalTrendPoint(BaseModel):
    industry: str = Field(..., description="The industry the trend belongs to")
    region: str = Field(..., description="The region the trend belongs to")
    period_start: str = Field(..., description="The start date of the period")
    period_end: str = Field(..., description="The end date of the period")
    value: float = Field(..., description="The value of the trend")
    metric: str = Field(..., description="The metric being projected")
    sources: Optional[list[str]] = Field(
        None, description="List of sources or references for this revenue data point"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class RegionalTrendsResponse(CitationResponse):
    regional_trends: list[RegionalTrendPoint] = Field(
        ..., description="List of regional trends"
    )
    summary: Optional[str] = Field(None, description="Summary of the regional trends")
    last_updated: Optional[str] = Field(None, description="Last updated timestamp")

    def get_plot_data(self) -> ChartData:
        data = [
            {"region": r.region, "period_start": r.period_start, "value": r.value}
            for r in self.regional_trends
        ]
        return ChartData(
            data=data,
            title="Regional Trends Over Time",
            x="period_start",
            y="value",
            kind="bar",
        )
