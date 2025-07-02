from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from backend.plot.types import ChartData
from backend.models.response.base import CitationResponse


# --- Compliance Overview ---
class RegulationItem(BaseModel):
    regulation: str
    description: Optional[str] = None
    applicable: bool
    sources: Optional[List[str]] = None


class ComplianceOverviewResponse(CitationResponse):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    regulations: List[RegulationItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

    def get_plot_data(self) -> ChartData:
        applicable = sum(1 for r in self.regulations if r.applicable)
        non_applicable = len(self.regulations) - applicable
        data = [
            {"status": "Applicable", "count": applicable},
            {"status": "Not Applicable", "count": non_applicable},
        ]
        return ChartData(
            data=data,
            title=f"Regulation Applicability for {self.company_name}",
            x="status",
            y="count",
            kind="pie",
        )


# --- Violation History ---
class ViolationItem(BaseModel):
    violation: str
    regulation: str
    date: date
    severity: str
    description: Optional[str] = None
    sources: Optional[List[str]] = None
    resolved: Optional[bool] = None


class ViolationHistoryResponse(CitationResponse):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    violations: List[ViolationItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

    def get_plot_data(self) -> ChartData:
        severity_counts = {}
        for v in self.violations:
            s = v.severity or "Unknown"
            severity_counts[s] = severity_counts.get(s, 0) + 1
        data = [{"severity": k, "count": v} for k, v in severity_counts.items()]
        return ChartData(
            data=data,
            title=f"Violations by Severity for {self.company_name}",
            x="severity",
            y="count",
            kind="bar",
        )


# --- Compliance Risk ---
class ComplianceRiskItem(BaseModel):
    risk: str
    severity: str
    description: Optional[str] = None
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None


class ComplianceRiskResponse(CitationResponse):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[ComplianceRiskItem]
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
            title=f"Compliance Risks for {self.company_name}",
            x="risk",
            y="confidence",
            kind="bar",
        )


# --- Regional Compliance ---
class RegionalComplianceItem(BaseModel):
    region: str
    regulations: List[RegulationItem]
    compliance_score: Optional[float] = None
    sources: Optional[List[str]] = None


class RegionalComplianceResponse(CitationResponse):
    company_name: str
    industry: Optional[str] = None
    regional_compliance: List[RegionalComplianceItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

    def get_plot_data(self) -> ChartData:
        data = [
            {"region": r.region, "compliance_score": r.compliance_score or 0}
            for r in self.regional_compliance
        ]
        return ChartData(
            data=data,
            title=f"Regional Compliance Scores for {self.company_name}",
            x="region",
            y="compliance_score",
            kind="bar",
        )
