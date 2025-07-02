from backend.services.customer_sentiment import CustomerSentimentService
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


class CustomerSentimentAgent(BaseAgent):
    def __init__(
        self,
        customer_sentiment_service: CustomerSentimentService,
        llm_config: LLMConfig,
    ):
        super().__init__(llm_config)
        self.customer_sentiment_service = customer_sentiment_service

        @tool()
        def get_sentiment_summary(
            company_name: str,
            domain: Optional[str] = None,
            product: Optional[str] = None,
            region: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.customer_sentiment_service.get_sentiment_summary)(
                company_name=company_name,
                domain=domain,
                product=product,
                region=region,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        @tool()
        def get_customer_feedback(
            company_name: str,
            domain: Optional[str] = None,
            product: Optional[str] = None,
            region: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.customer_sentiment_service.get_customer_feedback)(
                company_name=company_name,
                domain=domain,
                product=product,
                region=region,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        @tool()
        def get_brand_reputation(
            company_name: str,
            domain: Optional[str] = None,
            region: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.customer_sentiment_service.get_brand_reputation)(
                company_name=company_name,
                domain=domain,
                region=region,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        @tool()
        def get_sentiment_comparison(
            company_name: str,
            competitors: List[str],
            domain: Optional[str] = None,
            product: Optional[str] = None,
            region: Optional[str] = None,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
        ):
            result = syncify(self.customer_sentiment_service.get_sentiment_comparison)(
                company_name=company_name,
                competitors=competitors,
                domain=domain,
                product=product,
                region=region,
                start_date=start_date,
                end_date=end_date,
            )
            return json.dumps(result)

        self.tools = [
            get_sentiment_summary,
            get_customer_feedback,
            get_brand_reputation,
            get_sentiment_comparison,
        ]

        self.agent = Agent(
            name="CustomerSentimentAgent",
            model=get_model(llm_config),
            tools=self.tools,
            system_prompt=self.system_prompt(),
            show_tool_calls=True,
            response_model=AnalysisResponse,
        )

    @staticmethod
    def system_prompt():
        return (
            "You are a customer sentiment agent. "
            "You are given a user input about a company or product and you need to analyze the user input and return customer sentiment data. "
            "You have access to the following tools, each providing specific sentiment insights:\n"
            "- get_sentiment_summary: Returns sentiment score, breakdown, and timeseries. Accepts company name, domain, product, region, start date, and end date.\n"
            "- get_customer_feedback: Returns customer feedback items and summary. Accepts company name, domain, product, region, start date, and end date.\n"
            "- get_brand_reputation: Returns brand reputation score and timeseries. Accepts company name, domain, region, start date, and end date.\n"
            "- get_sentiment_comparison: Compares sentiment between a target company and its competitors. Accepts company name, list of competitors, domain, product, region, start date, and end date.\n"
            "Use the most relevant tool(s) to answer the user's question, and always cite sources if available."
        )

    def run(self, user_message: str) -> AnalysisResponse:
        result = self.agent.run(user_message)
        return result.content
