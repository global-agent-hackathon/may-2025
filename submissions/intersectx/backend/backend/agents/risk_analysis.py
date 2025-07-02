from backend.services.risk_analysis import RiskAnalysisService
from backend.agents.base import BaseAgent
from backend.settings import LLMConfig
from backend.models.response.chat import AnalysisResponse
from phi.tools import tool
from phi.agent import Agent
from backend.utils.llm import get_model
import asyncio
from typing import Optional
import json


# Helper to wrap async methods for sync tool interface
def syncify(async_fn):
    def wrapper(*args, **kwargs):
        return asyncio.run(async_fn(*args, **kwargs))

    return wrapper


class RiskAnalysisAgent(BaseAgent):
    def __init__(
        self, risk_analysis_service: RiskAnalysisService, llm_config: LLMConfig
    ):
        super().__init__(llm_config)
        self.risk_analysis_service = risk_analysis_service

        @tool()
        def get_regulatory_risks(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(self.risk_analysis_service.get_regulatory_risks)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        @tool()
        def get_market_risks(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(self.risk_analysis_service.get_market_risks)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        @tool()
        def get_operational_risks(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(self.risk_analysis_service.get_operational_risks)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        @tool()
        def get_legal_risks(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(self.risk_analysis_service.get_legal_risks)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        self.tools = [
            get_regulatory_risks,
            get_market_risks,
            get_operational_risks,
            get_legal_risks,
        ]

        self.agent = Agent(
            name="RiskAnalysisAgent",
            model=get_model(llm_config),
            tools=self.tools,
            system_prompt=self.system_prompt(),
            show_tool_calls=True,
            response_model=AnalysisResponse,
        )

    @staticmethod
    def system_prompt():
        return (
            "You are a risk analysis agent. "
            "You are given a user input about a company or industry and you need to analyze the user input and return risk analysis data. "
            "You have access to the following tools, each providing specific risk insights:\n"
            "- get_regulatory_risks: Returns regulatory risks and summary. Accepts company name, domain, industry, and region.\n"
            "- get_market_risks: Returns market risks and summary. Accepts company name, domain, industry, and region.\n"
            "- get_operational_risks: Returns operational risks and summary. Accepts company name, domain, industry, and region.\n"
            "- get_legal_risks: Returns legal risks and summary. Accepts company name, domain, industry, and region.\n"
            "Use the most relevant tool(s) to answer the user's question, and always cite sources if available."
        )

    def run(self, user_message: str) -> AnalysisResponse:
        result = self.agent.run(user_message)
        return result.content
