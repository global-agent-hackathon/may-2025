from backend.services.finance import FinanceService
from backend.agents.base import BaseAgent
from backend.settings import LLMConfig
from backend.models.response.chat import AnalysisResponse
from agno.tools import tool
from agno.agent import Agent
from backend.utils.llm import get_model
import asyncio
from dotenv import load_dotenv
from backend.settings import get_app_settings
from typing import Optional
import json


# Helper to wrap async methods for sync tool interface
def syncify(async_fn):
    def wrapper(*args, **kwargs):
        return asyncio.run(async_fn(*args, **kwargs))

    return wrapper


class FinanceAgent(BaseAgent):
    def __init__(self, finance_service: FinanceService, llm_config: LLMConfig):
        super().__init__(llm_config)
        self.finance_service = finance_service

        # Register finance tools using phidata
        @tool()
        def get_revenue_analysis(
            company_name: str,
            domain: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            granularity: str = "year",
        ):
            result = syncify(self.finance_service.get_revenue_analysis)(
                company_name=company_name,
                domain=domain,
                start_date=start_date,
                end_date=end_date,
                granularity=granularity,
            )
            return json.dumps(result)

        @tool()
        def get_expense_analysis(
            company_name: str,
            domain: Optional[str] = None,
            year: Optional[int] = None,
            category: Optional[str] = None,
        ):
            result = syncify(self.finance_service.get_expense_analysis)(
                company_name=company_name, domain=domain, year=year, category=category
            )
            return json.dumps(result)

        @tool()
        def get_profit_margins(
            company_name: str, domain: Optional[str] = None, year: Optional[int] = None
        ):
            result = syncify(self.finance_service.get_profit_margins)(
                company_name=company_name, domain=domain, year=year
            )
            return json.dumps(result)

        @tool()
        def get_valuation_estimation(
            company_name: str,
            domain: Optional[str] = None,
            as_of_date: Optional[str] = None,
        ):
            result = syncify(self.finance_service.get_valuation_estimation)(
                company_name=company_name, domain=domain, as_of_date=as_of_date
            )
            return json.dumps(result)

        @tool()
        def get_funding_history(company_name: str, domain: Optional[str] = None):
            result = syncify(self.finance_service.get_funding_history)(
                company_name=company_name, domain=domain
            )
            return json.dumps(result)

        self.tools = [
            get_revenue_analysis,
            get_expense_analysis,
            get_profit_margins,
            get_valuation_estimation,
            get_funding_history,
        ]

        self.agent = Agent(
            name="FinanceAgent",
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
            "You are a finance agent. "
            "You are given a user input about a company and you need to analyze the user input and return the finance data. "
            "You have access to the following tools, each providing specific financial insights about a company:\n"
            "- get_revenue_analysis: Returns detailed revenue timeseries, total revenue, and sources for a company. Accepts company name, domain, date range, and granularity (year/quarter/month).\n"
            "- get_expense_analysis: Returns expense breakdown by category, expense timeseries, and total expenses. Accepts company name, domain, year, and category.\n"
            "- get_profit_margins: Returns gross, operating, and net profit margins, including timeseries data. Accepts company name, domain, and year.\n"
            "- get_valuation_estimation: Returns the estimated valuation of a company, valuation timeseries, and sources. Accepts company name, domain, and as-of date.\n"
            "- get_funding_history: Returns funding rounds, cumulative funding timeseries, and total funding. Accepts company name and domain.\n"
            "Use the most relevant tool(s) to answer the user's question, and always cite sources if available."
        )

    def run(self, user_message: str) -> AnalysisResponse:
        result = self.agent.run(user_message)
        return result.content


if __name__ == "__main__":
    load_dotenv()
    app_settings = get_app_settings()
    finance_service = FinanceService()
    finance_agent = FinanceAgent(finance_service, app_settings.llm_config)
    data = finance_agent.run("What is the revenue of DataGenie Inc. in Q1 2023?")
    print(data)
    print(type(data))
