from datetime import datetime, date
from typing import Optional, Type, Union

from agno.agent import Agent
from pydantic import BaseModel

from backend.agents.output_parser import LLMOutputParserAgent
from backend.settings import SonarConfig, LLMConfig
from backend.utils.llm import get_model, get_sonar_model
from backend.utils.cache_decorator import cacheable
from backend.models.response.finance import (
    RevenueAnalysisResponse,
    ExpenseAnalysisResponse,
    ProfitMarginsResponse,
    ValuationEstimationResponse,
    FundingHistoryResponse,
)
from backend.services.knowledge import KnowledgeBaseService
from backend.plot.factory import get_builder


class FinanceService:
    def __init__(
        self,
        llm_config: LLMConfig,
        sonar_config: SonarConfig,
        knowledge_base_service: KnowledgeBaseService,
        netlify_agent,
    ):
        self.llm_config = llm_config
        self.sonar_config = sonar_config
        self.llm_model = get_model(self.llm_config)
        self.sonar_model = get_sonar_model(self.sonar_config)
        self.llm_output_parser = LLMOutputParserAgent(self.llm_model)
        self.knowledge_base_service = knowledge_base_service
        self.knowledge_base = self.knowledge_base_service.get_knowledge_base()
        self.netlify_agent = netlify_agent
        # cache_service will be injected by the dependency injection system

    async def _execute_llm_analysis(
        self,
        company_name: str,
        prompt: str,
        response_model: Type[BaseModel],
        agent_name: str = "AnalysisAgent",
        use_knowledge_base: bool = False,
    ) -> Union[
        RevenueAnalysisResponse,
        ExpenseAnalysisResponse,
        ProfitMarginsResponse,
        ValuationEstimationResponse,
        FundingHistoryResponse,
    ]:
        """
        Common method to execute LLM analysis and parse the response.

        Args:
            prompt: The prompt to send to the LLM
            response_model: The Pydantic model to parse the response into
            agent_name: Name of the agent for logging/identification

        Returns:
            Parsed response model instance with citations if available
        """
        analysis_agent = Agent(
            name=agent_name,
            model=self.sonar_model,
            instructions=prompt,
        )

        if use_knowledge_base:
            analysis_agent.knowledge = self.knowledge_base
            analysis_agent.knowledge_filters = {"company_name": company_name}

        # Use the LLM to generate the content
        content = analysis_agent.run(prompt)

        # Parse the LLM output into the response model
        response = self.llm_output_parser.parse(content.content, response_model)

        # Attach citations if response is a Pydantic model and has citations
        if hasattr(response, "citations") and hasattr(content, "citations"):
            response.citations = (
                content.citations.urls if hasattr(content.citations, "urls") else []
            )

        # Add plot iframe_url
        try:
            chart_data = response.get_plot_data()
            builder = get_builder(chart_data.kind, self.netlify_agent)
            print("chart_data.kind", chart_data.kind)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception as e:
            print(f"Failed to generate plot for response as {e}")
            response.iframe_url = None

        return response

    @cacheable()
    async def get_revenue_analysis(
        self,
        company_name: str,
        domain: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        granularity: str = "year",
        use_knowledge_base: bool = False,
    ) -> RevenueAnalysisResponse:
        """
        Retrieve revenue analysis data for a company.
        Args:
            company_name (str): Name of the company (required)
            domain (str, optional): Domain of the company
            start_date (date, optional): Start date for analysis
            end_date (date, optional): End date for analysis
            granularity (str, optional): Granularity of data (year, quarter, or month)
        Returns:
            RevenueAnalysisResponse: Contains company name, currency, revenue timeseries,
            total revenue, and last updated timestamp.
        """

        # Compose a detailed prompt for the LLM to generate all required fields
        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a financial analyst. Generate a detailed revenue analysis for the following company:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}
        - Start Date: {start_date or "N/A"}
        - End Date: {end_date or "N/A"}
        - Granularity: {granularity}

        Please provide the following fields in your response:
        - company_name: The name of the company
        - revenue_timeseries: A list of objects, each with period_start, period_end, value, 
          sources (list of strings), and confidence (float between 0 and 1)
        - total_revenue: The total revenue for the period
        - last_updated: The datetime of the latest data (ISO format)

        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=RevenueAnalysisResponse,
            agent_name="RevenueAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_expense_analysis(
        self,
        company_name: str,
        domain: Optional[str] = None,
        year: Optional[int] = None,
        category: Optional[str] = None,
        use_knowledge_base: bool = False,
    ) -> ExpenseAnalysisResponse:
        """
        Retrieve expense analysis data for a company.
        Args:
            company_name (str): Name of the company (required)
            domain (str, optional): Domain of the company
            year (int, optional): Year for analysis
            category (str, optional): Expense category
        Returns:
            ExpenseAnalysisResponse: Contains company name, year, expenses by category,
            total expense, and last updated timestamp.
        """

        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a financial analyst. Generate a detailed expense analysis for the following company:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}
        - Year: {year or "N/A"}
        - Category: {category or "N/A"}

        Please provide the following fields in your response:
        - company_name: The name of the company
        - expenses: A list of expense categories with value, currency, sources, and confidence
        - total_expense: The total expense for the period
        - last_updated: The datetime of the latest data (ISO format)

        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=ExpenseAnalysisResponse,
            agent_name="ExpenseAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_profit_margins(
        self,
        company_name: str,
        domain: Optional[str] = None,
        year: Optional[int] = None,
        use_knowledge_base: bool = False,
    ) -> ProfitMarginsResponse:
        """
        Retrieve profit margin data for a company.
        Args:
            company_name (str): Name of the company (required)
            domain (str, optional): Domain of the company
            year (int, optional): Year for analysis
        Returns:
            dict: Contains company name, year, gross/operating/net margins, margin timeseries, currency, sources, and last updated timestamp.
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a financial analyst. Generate a detailed expense analysis for the following company:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}
        - Year: {year or "N/A"}

        Please provide the following fields in your response:
        - company_name: The name of the company
        - margins: A list of margin categories with value, currency, sources, and confidence
        - last_updated: The datetime of the latest data (ISO format)

        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=ProfitMarginsResponse,
            agent_name="ProfitMarginsAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_valuation_estimation(
        self,
        company_name: str,
        domain: Optional[str] = None,
        as_of_date: Optional[date] = None,
        use_knowledge_base: bool = False,
    ) -> ValuationEstimationResponse:
        """
        Retrieve valuation estimation data for a company.
        Args:
            company_name (str): Name of the company (required)
            domain (str, optional): Domain of the company
            as_of_date (date, optional): Date for valuation
        Returns:
            ValuationEstimationResponse: Contains company name, last valuation, valuation timeseries, and last updated timestamp.
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a financial analyst. Generate a detailed valuation estimation for the following company:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}
        - As of Date: {as_of_date or "N/A"}

        Please provide the following fields in your response:
        - company_name: The name of the company
        - last_valuation: The most recent valuation value for the company
        - valuation_timeseries: A list of objects, each with date, value, currency, sources, and confidence
        - last_updated: The datetime of the latest data (ISO format)

        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=ValuationEstimationResponse,
            agent_name="ValuationEstimationAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_funding_history(
        self,
        company_name: str,
        domain: Optional[str] = None,
        use_knowledge_base: bool = False,
    ) -> FundingHistoryResponse:
        """
        Retrieve funding history data for a company.
        Args:
            company_name (str): Name of the company (required)
            domain (str, optional): Domain of the company
        Returns:
            FundingHistoryResponse: Contains company name, funding rounds, total funding, and last updated timestamp.
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a financial analyst. Generate a detailed funding history for the following company:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}

        Please provide the following fields in your response:
        - company_name: The name of the company
        - funding_rounds: A list of objects, each with round_type, value, currency, date, lead_investors, sources, and confidence
        - total_funding: The total funding for the company
        - last_updated: The datetime of the latest data (ISO format)

        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=FundingHistoryResponse,
            agent_name="FundingHistoryAgent",
            use_knowledge_base=use_knowledge_base,
        )
