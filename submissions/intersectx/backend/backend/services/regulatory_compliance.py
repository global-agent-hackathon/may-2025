from backend.utils.cache_decorator import cacheable

from datetime import datetime
from typing import Optional, List
from backend.plot.factory import get_builder
from backend.models.response.regulatory_compliance import (
    ComplianceOverviewResponse,
    ViolationHistoryResponse,
    ComplianceRiskResponse,
    RegionalComplianceResponse,
)


class RegulatoryComplianceService:
    def __init__(self, netlify_agent):
        self.netlify_agent = netlify_agent
        # cache_service will be injected by the dependency injection system

    @cacheable()
    async def get_compliance_overview(
        self,
        company_name: str,
        domain: Optional[str] = None,
        industry: Optional[str] = None,
        region: Optional[str] = None,
    ):
        data = {
            "company_name": company_name,
            "industry": industry or "Cloud Computing",
            "region": region or "Global",
            "regulations": [
                {
                    "regulation": "GDPR",
                    "description": "EU data privacy regulation.",
                    "applicable": True,
                    "sources": ["https://gdpr.eu/"],
                },
                {
                    "regulation": "SOX",
                    "description": "Sarbanes-Oxley Act.",
                    "applicable": True,
                    "sources": ["https://sox.com/"],
                },
                {
                    "regulation": "HIPAA",
                    "description": "US health data regulation.",
                    "applicable": False,
                    "sources": ["https://hhs.gov/hipaa/"],
                },
            ],
            "summary": "Key regulations include GDPR and SOX.",
            "sources": ["https://gdpr.eu/", "https://sox.com/"],
            "last_updated": datetime.now().isoformat(),
        }
        response = ComplianceOverviewResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response

    @cacheable()
    async def get_violation_history(
        self,
        company_name: str,
        domain: Optional[str] = None,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        data = {
            "company_name": company_name,
            "industry": industry or "Cloud Computing",
            "region": region or "Global",
            "violations": [
                {
                    "violation": "Data Breach",
                    "regulation": "GDPR",
                    "date": "2022-05-10",
                    "severity": "High",
                    "description": "Unauthorized access to user data.",
                    "sources": ["https://databreaches.net/tecnova"],
                    "resolved": True,
                },
                {
                    "violation": "Late SOX Filing",
                    "regulation": "SOX",
                    "date": "2023-01-15",
                    "severity": "Medium",
                    "description": "Delayed financial reporting.",
                    "sources": ["https://sox.com/tecnova-filing"],
                    "resolved": False,
                },
            ],
            "summary": "Two major violations in the last two years.",
            "sources": [
                "https://databreaches.net/tecnova",
                "https://sox.com/tecnova-filing",
            ],
            "last_updated": datetime.now().isoformat(),
        }
        response = ViolationHistoryResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response

    @cacheable()
    async def get_compliance_risk(
        self,
        company_name: str,
        domain: Optional[str] = None,
        industry: Optional[str] = None,
        region: Optional[str] = None,
    ):
        data = {
            "company_name": company_name,
            "industry": industry or "Cloud Computing",
            "region": region or "Global",
            "risks": [
                {
                    "risk": "GDPR Fines",
                    "severity": "High",
                    "description": "Potential fines for non-compliance.",
                    "sources": ["https://gdpr.eu/fines/"],
                    "confidence": 0.8,
                },
                {
                    "risk": "SOX Audit Failure",
                    "severity": "Medium",
                    "description": "Risk of failing SOX audit.",
                    "sources": ["https://sox.com/audit/"],
                    "confidence": 0.7,
                },
            ],
            "summary": "GDPR fines and SOX audit are the main compliance risks.",
            "sources": ["https://gdpr.eu/fines/", "https://sox.com/audit/"],
            "last_updated": datetime.now().isoformat(),
        }
        response = ComplianceRiskResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response

    @cacheable()
    async def get_regional_compliance(
        self,
        company_name: str,
        domain: Optional[str] = None,
        industry: Optional[str] = None,
        regions: Optional[List[str]] = None,
    ):
        data = {
            "company_name": company_name,
            "industry": industry or "Cloud Computing",
            "regional_compliance": [
                {
                    "region": "EU",
                    "regulations": [
                        {
                            "regulation": "GDPR",
                            "description": "EU data privacy regulation.",
                            "applicable": True,
                            "sources": ["https://gdpr.eu/"],
                        }
                    ],
                    "compliance_score": 0.85,
                    "sources": ["https://gdpr.eu/"],
                },
                {
                    "region": "US",
                    "regulations": [
                        {
                            "regulation": "SOX",
                            "description": "Sarbanes-Oxley Act.",
                            "applicable": True,
                            "sources": ["https://sox.com/"],
                        },
                        {
                            "regulation": "HIPAA",
                            "description": "US health data regulation.",
                            "applicable": False,
                            "sources": ["https://hhs.gov/hipaa/"],
                        },
                    ],
                    "compliance_score": 0.78,
                    "sources": ["https://sox.com/", "https://hhs.gov/hipaa/"],
                },
            ],
            "summary": "EU compliance is higher than US compliance.",
            "sources": [
                "https://gdpr.eu/",
                "https://sox.com/",
                "https://hhs.gov/hipaa/",
            ],
            "last_updated": datetime.now().isoformat(),
        }
        response = RegionalComplianceResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response
