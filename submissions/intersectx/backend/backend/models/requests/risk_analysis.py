from pydantic import BaseModel, Field
from typing import Optional


class RegulatoryRisksRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None


class MarketRisksRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None


class OperationalRisksRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None


class LegalRisksRequest(BaseModel):
    company_name: str = Field(...)
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
