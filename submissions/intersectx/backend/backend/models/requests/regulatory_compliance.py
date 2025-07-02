from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class ComplianceOverviewRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None


class ViolationHistoryRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ComplianceRiskRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None


class RegionalComplianceRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    regions: Optional[List[str]] = None
