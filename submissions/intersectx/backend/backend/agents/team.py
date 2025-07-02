from backend.services.team import TeamService
from backend.agents.base import BaseAgent
from backend.settings import LLMConfig
from backend.models.response.chat import AnalysisResponse
from agno.tools import tool
from agno.agent import Agent
from backend.utils.llm import get_model
import asyncio
from typing import Optional
import json


# Helper to wrap async methods for sync tool interface
def syncify(async_fn):
    def wrapper(*args, **kwargs):
        return asyncio.run(async_fn(*args, **kwargs))

    return wrapper


class TeamAgent(BaseAgent):
    def __init__(self, linkedin_team_service: TeamService, llm_config: LLMConfig):
        super().__init__(llm_config)
        self.linkedin_team_service = linkedin_team_service

        @tool()
        def get_team_overview(company_name: str, domain: Optional[str] = None):
            result = syncify(self.linkedin_team_service.get_team_overview)(
                company_name=company_name, domain=domain
            )
            return json.dumps(result)

        @tool()
        def get_individual_performance(
            company_name: str,
            domain: Optional[str] = None,
            individual_name: Optional[str] = None,
        ):
            result = syncify(self.linkedin_team_service.get_individual_performance)(
                company_name=company_name,
                domain=domain,
                individual_name=individual_name,
            )
            return json.dumps(result)

        @tool()
        def get_org_structure(company_name: str, domain: Optional[str] = None):
            result = syncify(self.linkedin_team_service.get_org_structure)(
                company_name=company_name, domain=domain
            )
            return json.dumps(result)

        @tool()
        def get_team_growth(
            company_name: str,
            domain: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.linkedin_team_service.get_team_growth)(
                company_name=company_name,
                domain=domain,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        self.tools = [
            get_team_overview,
            get_individual_performance,
            get_org_structure,
            get_team_growth,
        ]

        self.agent = Agent(
            name="LinkedInTeamAgent",
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
            "You are a LinkedIn Team agent. "
            "You are given a user input about a company and you need to analyze the user input and return LinkedIn team data. "
            "You have access to the following tools, each providing specific team insights about a company:\n"
            "- get_team_overview: Returns team size, roles breakdown, and locations. Accepts company name and domain.\n"
            "- get_individual_performance: Returns performance metrics for an individual. Accepts company name, domain, and individual name.\n"
            "- get_org_structure: Returns the org chart for a company. Accepts company name and domain.\n"
            "- get_team_growth: Returns team growth timeseries and net growth. Accepts company name, domain, start date, and end date.\n"
            "Use the most relevant tool(s) to answer the user's question, and always cite sources if available."
        )

    def run(self, user_message: str) -> AnalysisResponse:
        result = self.agent.run(user_message)
        return result.content
