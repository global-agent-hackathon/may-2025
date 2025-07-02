from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PartnerListRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None


class StrategicAlliancesRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None


class NetworkStrengthRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None


class PartnershipTrendsRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
