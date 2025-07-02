from backend.services.regulatory_compliance import RegulatoryComplianceService
from backend.agents.base import BaseAgent
from backend.settings import LLMConfig
from backend.models.response.chat import AnalysisResponse
from phi.tools import tool
from phi.agent import Agent
from backend.utils.llm import get_model
import asyncio
from typing import Optional, List
import json


# Helper to wrap async methods for sync tool interface
def syncify(async_fn):
    def wrapper(*args, **kwargs):
        return asyncio.run(async_fn(*args, **kwargs))

    return wrapper


class RegulatoryComplianceAgent(BaseAgent):
    def __init__(
        self,
        regulatory_compliance_service: RegulatoryComplianceService,
        llm_config: LLMConfig,
    ):
        super().__init__(llm_config)
        self.regulatory_compliance_service = regulatory_compliance_service

        @tool()
        def get_compliance_overview(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(
                self.regulatory_compliance_service.get_compliance_overview
            )(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        @tool()
        def get_violation_history(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.regulatory_compliance_service.get_violation_history)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        @tool()
        def get_compliance_risk(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            region: Optional[str] = None,
        ):
            result = syncify(self.regulatory_compliance_service.get_compliance_risk)(
                company_name=company_name,
                domain=domain,
                industry=industry,
                region=region,
            )
            return json.dumps(result)

        @tool()
        def get_regional_compliance(
            company_name: str,
            domain: Optional[str] = None,
            industry: Optional[str] = None,
            regions: Optional[List[str]] = None,
        ):
            result = syncify(
                self.regulatory_compliance_service.get_regional_compliance
            )(
                company_name=company_name,
                domain=domain,
                industry=industry,
                regions=regions,
            )
            return json.dumps(result)

        self.tools = [
            get_compliance_overview,
            get_violation_history,
            get_compliance_risk,
            get_regional_compliance,
        ]

        self.agent = Agent(
            name="RegulatoryComplianceAgent",
            model=get_model(llm_config),
            tools=self.tools,
            system_prompt=self.system_prompt(),
            show_tool_calls=True,
            response_model=AnalysisResponse,
        )

    @staticmethod
    def system_prompt():
        return (
            "You are a regulatory compliance agent. "
            "You are given a user input about a company or industry and you need to analyze the user input and return regulatory compliance data. "
            "You have access to the following tools, each providing specific compliance insights:\n"
            "- get_compliance_overview: Returns compliance overview and regulations. Accepts company name, domain, industry, and region.\n"
            "- get_violation_history: Returns compliance violations and summary. Accepts company name, domain, industry, region, start date, and end date.\n"
            "- get_compliance_risk: Returns compliance risks and summary. Accepts company name, domain, industry, and region.\n"
            "- get_regional_compliance: Returns regional compliance details. Accepts company name, domain, industry, and regions.\n"
            "Use the most relevant tool(s) to answer the user's question, and always cite sources if available."
        )

    def run(self, user_message: str) -> AnalysisResponse:
        result = self.agent.run(user_message)
        return result.content
