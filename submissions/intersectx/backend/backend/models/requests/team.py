from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class TeamOverviewRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None


class IndividualPerformanceRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    individual_name: str = Field(...)


class OrgStructureRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None


class TeamGrowthRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
