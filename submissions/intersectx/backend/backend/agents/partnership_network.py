from backend.services.partnership_network import PartnershipNetworkService
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


class PartnershipNetworkAgent(BaseAgent):
    def __init__(
        self,
        partnership_network_service: PartnershipNetworkService,
        llm_config: LLMConfig,
    ):
        super().__init__(llm_config)
        self.partnership_network_service = partnership_network_service

        @tool()
        def get_partner_list(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(self.partnership_network_service.get_partner_list)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        @tool()
        def get_strategic_alliances(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(self.partnership_network_service.get_strategic_alliances)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        @tool()
        def get_network_strength(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(self.partnership_network_service.get_network_strength)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        @tool()
        def get_partnership_trends(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.partnership_network_service.get_partnership_trends)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        self.tools = [
            get_partner_list,
            get_strategic_alliances,
            get_network_strength,
            get_partnership_trends,
        ]

        self.agent = Agent(
            name="PartnershipNetworkAgent",
            model=get_model(llm_config),
            tools=self.tools,
            system_prompt=self.system_prompt(),
            show_tool_calls=True,
            response_model=AnalysisResponse,
        )

    @staticmethod
    def system_prompt():
        return (
            "You are a partnership network agent. "
            "You are given a user input about a company or industry and you need to analyze the user input and return partnership network data. "
            "You have access to the following tools, each providing specific partnership insights:\n"
            "- get_partner_list: Returns partner list and summary. Accepts company name, domain, industry, and region.\n"
            "- get_strategic_alliances: Returns strategic alliances and summary. Accepts company name, domain, industry, and region.\n"
            "- get_network_strength: Returns network metrics and summary. Accepts company name, domain, industry, and region.\n"
            "- get_partnership_trends: Returns partnership trends timeseries and summary. Accepts company name, domain, industry, region, start date, and end date.\n"
            "Use the most relevant tool(s) to answer the user's question, and always cite sources if available."
        )

    def run(self, user_message: str) -> AnalysisResponse:
        result = self.agent.run(user_message)
        return result.content
