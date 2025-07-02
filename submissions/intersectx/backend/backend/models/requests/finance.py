from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ExpenseAnalysisRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    year: Optional[int] = None
    category: Optional[str] = None


class ProfitMarginsRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    year: Optional[int] = None


class ValuationEstimationRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    as_of_date: Optional[date] = None


class FundingHistoryRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None


class RevenueAnalysisRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    granularity: Optional[str] = Field(
        "year", description="Granularity: year, quarter, or month"
    )
