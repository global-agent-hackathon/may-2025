from backend.utils.cache_decorator import cacheable

from datetime import datetime
from typing import Optional
from backend.plot.factory import get_builder
from backend.models.response.partnership_network import (
    PartnerListResponse,
    StrategicAlliancesResponse,
    NetworkStrengthResponse,
    PartnershipTrendsResponse,
)


class PartnershipNetworkService:
    def __init__(self, netlify_agent):
        self.netlify_agent = netlify_agent
        # cache_service will be injected by the dependency injection system

    @cacheable()
    async def get_partner_list(
        self,
        company_name: str,
        domain: Optional[str] = None,
        industry: Optional[str] = None,
        region: Optional[str] = None,
    ):
        data = {
            "company_name": company_name,
            "partners": [
                {
                    "name": "CloudX",
                    "domain": "cloudx.com",
                    "partnership_type": "Technology",
                    "since": "2021-03-01",
                    "sources": ["https://cloudx.com/partners"],
                },
                {
                    "name": "DataBridge",
                    "domain": "databridge.com",
                    "partnership_type": "Channel",
                    "since": "2022-07-15",
                    "sources": ["https://databridge.com/partners"],
                },
            ],
            "summary": "TechNova has two major partners in technology and channel.",
            "sources": [
                "https://cloudx.com/partners",
                "https://databridge.com/partners",
            ],
            "last_updated": datetime.now().isoformat(),
        }
        response = PartnerListResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response

    @cacheable()
    async def get_strategic_alliances(
        self,
        company_name: str,
        domain: Optional[str] = None,
        industry: Optional[str] = None,
        region: Optional[str] = None,
    ):
        data = {
            "company_name": company_name,
            "alliances": [
                {
                    "partner": "CloudX",
                    "impact_area": "Product Integration",
                    "impact_score": 0.9,
                    "description": "Joint cloud product offering.",
                    "sources": ["https://cloudx.com/alliances"],
                },
                {
                    "partner": "DataBridge",
                    "impact_area": "Market Expansion",
                    "impact_score": 0.8,
                    "description": "Expanded reach in EMEA.",
                    "sources": ["https://databridge.com/alliances"],
                },
            ],
            "summary": "Alliances have led to product integration and market expansion.",
            "sources": [
                "https://cloudx.com/alliances",
                "https://databridge.com/alliances",
            ],
            "last_updated": datetime.now().isoformat(),
        }
        response = StrategicAlliancesResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response

    @cacheable()
    async def get_network_strength(
        self,
        company_name: str,
        domain: Optional[str] = None,
        industry: Optional[str] = None,
        region: Optional[str] = None,
    ):
        data = {
            "company_name": company_name,
            "network_metrics": [
                {
                    "metric": "Partner Count",
                    "value": 12,
                    "sources": ["https://tecnova.com/network"],
                    "confidence": 0.9,
                },
                {
                    "metric": "Industry Connections",
                    "value": 35,
                    "sources": ["https://tecnova.com/network"],
                    "confidence": 0.85,
                },
            ],
            "summary": "TechNova has a strong network in the cloud industry.",
            "sources": ["https://tecnova.com/network"],
            "last_updated": datetime.now().isoformat(),
        }
        response = NetworkStrengthResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response

    @cacheable()
    async def get_partnership_trends(
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
            "partnership_trends_timeseries": [
                {
                    "period_start": "2022-01-01",
                    "period_end": "2022-12-31",
                    "new_partnerships": 3,
                    "ended_partnerships": 1,
                    "net_growth": 2,
                    "sources": ["https://tecnova.com/partners"],
                    "confidence": 0.8,
                },
                {
                    "period_start": "2023-01-01",
                    "period_end": "2023-12-31",
                    "new_partnerships": 4,
                    "ended_partnerships": 0,
                    "net_growth": 4,
                    "sources": ["https://tecnova.com/partners"],
                    "confidence": 0.85,
                },
            ],
            "summary": "Partnerships are growing year over year.",
            "sources": ["https://tecnova.com/partners"],
            "last_updated": datetime.now().isoformat(),
        }
        response = PartnershipTrendsResponse(**data)
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None
        return response
