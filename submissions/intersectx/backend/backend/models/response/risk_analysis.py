from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from backend.models.response.base import CitationResponse
from backend.plot.types import ChartData


# --- Regulatory Risks ---
class RegulatoryRiskItem(BaseModel):
    risk: str
    severity: str
    description: Optional[str] = None
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None


class RegulatoryRisksResponse(CitationResponse):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[RegulatoryRiskItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

    def get_plot_data(self) -> ChartData:
        data = [
            {"risk": r.risk, "severity": r.severity, "confidence": r.confidence or 0}
            for r in self.risks
        ]
        return ChartData(
            data=data,
            title=f"Regulatory Risks for {self.company_name}",
            x="risk",
            y="confidence",
            kind="bar",
        )


# --- Market Risks ---
class MarketRiskItem(BaseModel):
    risk: str
    severity: str
    description: Optional[str] = None
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None


class MarketRisksResponse(CitationResponse):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[MarketRiskItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

    def get_plot_data(self) -> ChartData:
        data = [
            {"risk": r.risk, "severity": r.severity, "confidence": r.confidence or 0}
            for r in self.risks
        ]
        return ChartData(
            data=data,
            title=f"Market Risks for {self.company_name}",
            x="risk",
            y="confidence",
            kind="bar",
        )


# --- Operational Risks ---
class OperationalRiskItem(BaseModel):
    risk: str
    severity: str
    description: Optional[str] = None
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None


class OperationalRisksResponse(CitationResponse):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[OperationalRiskItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

    def get_plot_data(self) -> ChartData:
        data = [
            {"risk": r.risk, "severity": r.severity, "confidence": r.confidence or 0}
            for r in self.risks
        ]
        return ChartData(
            data=data,
            title=f"Operational Risks for {self.company_name}",
            x="risk",
            y="confidence",
            kind="bar",
        )


# --- Legal Risks ---
class LegalRiskItem(BaseModel):
    risk: str
    severity: str
    description: Optional[str] = None
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None
    case_number: Optional[str] = None
    date_filed: Optional[date] = None


class LegalRisksResponse(CitationResponse):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[LegalRiskItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

    def get_plot_data(self) -> ChartData:
        data = [
            {"risk": r.risk, "severity": r.severity, "confidence": r.confidence or 0}
            for r in self.risks
        ]
        return ChartData(
            data=data,
            title=f"Legal Risks for {self.company_name}",
            x="risk",
            y="confidence",
            kind="bar",
        )
