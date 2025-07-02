from backend.utils.cache_decorator import cacheable

from datetime import datetime
from typing import Optional
from backend.plot.factory import get_builder
from backend.models.response.risk_analysis import (
    RegulatoryRisksResponse,
    MarketRisksResponse,
    OperationalRisksResponse,
    LegalRisksResponse,
)


class RiskAnalysisService:
    def __init__(self, netlify_agent):
        self.netlify_agent = netlify_agent
        # cache_service will be injected by the dependency injection system

    @cacheable()
    async def get_regulatory_risks(
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
                    "risk": "GDPR Non-compliance",
                    "severity": "High",
                    "description": "Potential non-compliance with EU data privacy laws.",
                    "sources": ["https://gdpr.eu/tecnova"],
                    "confidence": 0.85,
                },
                {
                    "risk": "SOX Reporting Issues",
                    "severity": "Medium",
                    "description": "Possible issues with Sarbanes-Oxley reporting.",
                    "sources": ["https://sox.com/tecnova"],
                    "confidence": 0.7,
                },
            ],
            "summary": "Key regulatory risks include GDPR and SOX compliance.",
            "sources": ["https://gdpr.eu/tecnova", "https://sox.com/tecnova"],
            "last_updated": datetime.now().isoformat(),
        }
        response = RegulatoryRisksResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response

    @cacheable()
    async def get_market_risks(
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
                    "risk": "Market Saturation",
                    "severity": "High",
                    "description": "High competition may limit growth.",
                    "sources": ["https://marketwatch.com/tecnova"],
                    "confidence": 0.8,
                },
                {
                    "risk": "Changing Customer Preferences",
                    "severity": "Medium",
                    "description": "Rapidly evolving customer needs.",
                    "sources": ["https://forrester.com/tecnova"],
                    "confidence": 0.75,
                },
            ],
            "summary": "Market is highly competitive and customer needs are evolving.",
            "sources": [
                "https://marketwatch.com/tecnova",
                "https://forrester.com/tecnova",
            ],
            "last_updated": datetime.now().isoformat(),
        }
        response = MarketRisksResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response

    @cacheable()
    async def get_operational_risks(
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
                    "risk": "Talent Retention",
                    "severity": "Medium",
                    "description": "Difficulty retaining skilled engineers.",
                    "sources": ["https://linkedin.com/company/tecnova"],
                    "confidence": 0.7,
                },
                {
                    "risk": "Supply Chain Disruption",
                    "severity": "Low",
                    "description": "Potential delays in hardware supply.",
                    "sources": ["https://supplychain.com/tecnova"],
                    "confidence": 0.6,
                },
            ],
            "summary": "Operational risks include talent retention and supply chain issues.",
            "sources": [
                "https://linkedin.com/company/tecnova",
                "https://supplychain.com/tecnova",
            ],
            "last_updated": datetime.now().isoformat(),
        }
        response = OperationalRisksResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response

    @cacheable()
    async def get_legal_risks(
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
                    "risk": "Patent Infringement Lawsuit",
                    "severity": "High",
                    "description": "Ongoing lawsuit regarding cloud storage patents.",
                    "sources": ["https://law360.com/tecnova-lawsuit"],
                    "confidence": 0.8,
                    "case_number": "2023-CV-1234",
                    "date_filed": "2023-02-15",
                },
                {
                    "risk": "Contract Dispute",
                    "severity": "Medium",
                    "description": "Dispute with a major supplier.",
                    "sources": ["https://contracts.com/tecnova-dispute"],
                    "confidence": 0.7,
                    "case_number": "2023-CV-5678",
                    "date_filed": "2023-05-10",
                },
            ],
            "summary": "Legal risks include ongoing patent and contract disputes.",
            "sources": [
                "https://law360.com/tecnova-lawsuit",
                "https://contracts.com/tecnova-dispute",
            ],
            "last_updated": datetime.now().isoformat(),
        }
        response = LegalRisksResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response
