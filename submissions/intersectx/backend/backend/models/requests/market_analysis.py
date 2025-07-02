from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class MarketTrendsRequest(BaseModel):
    company_name: str = Field(...)
    industry: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CompetitiveAnalysisRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    companies_to_compare: Optional[list[str]] = None


class GrowthProjectionsRequest(BaseModel):
    company_name: str = Field(...)
    industry: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class RegionalTrendsRequest(BaseModel):
    company_name: str = Field(...)
    industry: Optional[str] = None
    regions_of_interest: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
