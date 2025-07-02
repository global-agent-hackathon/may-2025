from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from backend.plot.types import ChartData
from backend.models.response.base import CitationResponse


# --- Partner List ---
class PartnerItem(BaseModel):
    name: str
    domain: Optional[str] = None
    partnership_type: Optional[str] = None
    since: Optional[date] = None
    sources: Optional[List[str]] = None


class PartnerListResponse(CitationResponse):
    company_name: str
    partners: List[PartnerItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
    plot_url: Optional[str] = None

    def get_plot_data(self) -> ChartData:
        type_counts = {}
        for p in self.partners:
            t = p.partnership_type or "Unknown"
            type_counts[t] = type_counts.get(t, 0) + 1
        data = [{"partnership_type": k, "count": v} for k, v in type_counts.items()]
        return ChartData(
            data=data,
            title=f"Partners by Type for {self.company_name}",
            x="partnership_type",
            y="count",
            kind="pie",
        )


# --- Strategic Alliances ---
class AllianceImpactItem(BaseModel):
    partner: str
    impact_area: str
    impact_score: float
    description: Optional[str] = None
    sources: Optional[List[str]] = None


class StrategicAlliancesResponse(CitationResponse):
    company_name: str
    alliances: List[AllianceImpactItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
    plot_url: Optional[str] = None

    def get_plot_data(self) -> ChartData:
        data = [
            {"partner": a.partner, "impact_score": a.impact_score}
            for a in self.alliances
        ]
        return ChartData(
            data=data,
            title=f"Strategic Alliance Impact Scores for {self.company_name}",
            x="partner",
            y="impact_score",
            kind="bar",
        )


# --- Network Strength ---
class NetworkMetricItem(BaseModel):
    metric: str
    value: float
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None


class NetworkStrengthResponse(CitationResponse):
    company_name: str
    network_metrics: List[NetworkMetricItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
    plot_url: Optional[str] = None

    def get_plot_data(self) -> ChartData:
        data = [{"metric": m.metric, "value": m.value} for m in self.network_metrics]
        return ChartData(
            data=data,
            title=f"Network Metrics for {self.company_name}",
            x="metric",
            y="value",
            kind="bar",
        )


# --- Partnership Trends ---
class PartnershipTrendTimeSeriesPoint(BaseModel):
    period_start: date
    period_end: date
    new_partnerships: int
    ended_partnerships: int
    net_growth: int
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None


class PartnershipTrendsResponse(CitationResponse):
    company_name: str
    partnership_trends_timeseries: List[PartnershipTrendTimeSeriesPoint]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
    plot_url: Optional[str] = None

    def get_plot_data(self) -> ChartData:
        data = [
            {"period_start": t.period_start.isoformat(), "net_growth": t.net_growth}
            for t in self.partnership_trends_timeseries
        ]
        return ChartData(
            data=data,
            title=f"Partnership Net Growth Over Time for {self.company_name}",
            x="period_start",
            y="net_growth",
            kind="line",
        )
