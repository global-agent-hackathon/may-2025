from backend.services.market_analysis import MarketAnalysisService
from backend.agents.base import BaseAgent
from backend.settings import LLMConfig
from backend.models.response.chat import AnalysisResponse
from agno.tools import tool
from agno.agent import Agent
from backend.utils.llm import get_model
import asyncio
from typing import Optional, List
import json


# Helper to wrap async methods for sync tool interface
def syncify(async_fn):
    def wrapper(*args, **kwargs):
        return asyncio.run(async_fn(*args, **kwargs))

    return wrapper


class MarketAnalysisAgent(BaseAgent):
    def __init__(
        self, market_analysis_service: MarketAnalysisService, llm_config: LLMConfig
    ):
        super().__init__(llm_config)
        self.market_analysis_service = market_analysis_service

        @tool()
        def get_market_trends(
            industry: str,
            region: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.market_analysis_service.get_market_trends)(
                industry=industry,
                region=region,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        @tool()
        def get_competitive_analysis(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(self.market_analysis_service.get_competitive_analysis)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        @tool()
        def get_growth_projections(
            industry: str,
            region: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.market_analysis_service.get_growth_projections)(
                industry=industry,
                region=region,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        @tool()
        def get_regional_trends(
            industry: str,
            regions: Optional[List[str]] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.market_analysis_service.get_regional_trends)(
                industry=industry,
                regions=regions,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        self.tools = [
            get_market_trends,
            get_competitive_analysis,
            get_growth_projections,
            get_regional_trends,
        ]

        self.agent = Agent(
            name="MarketAnalysisAgent",
            model=get_model(llm_config),
            tools=self.tools,
            instructions=self.system_prompt(),
            show_tool_calls=True,
            response_model=AnalysisResponse,
            use_json_mode=True,
        )

    @staticmethod
    def system_prompt():
        return (
            "You are a market analysis agent. "
            "You are given a user input about a company or industry and you need to analyze the user input and return market analysis data. "
            "You have access to the following tools, each providing specific market insights:\n"
            "- get_market_trends: Returns market trends timeseries and summary. Accepts industry, region, start date, and end date.\n"
            "- get_competitive_analysis: Returns competitor profiles and summary. Accepts company name, domain, industry, and region.\n"
            "- get_growth_projections: Returns growth projections timeseries and summary. Accepts industry, region, start date, and end date.\n"
            "- get_regional_trends: Returns regional market trends. Accepts industry, regions, start date, and end date.\n"
            "Use the most relevant tool(s) to answer the user's question, and always cite sources if available."
        )

    def run(self, user_message: str) -> AnalysisResponse:
        result = self.agent.run(user_message)
        return result.content
