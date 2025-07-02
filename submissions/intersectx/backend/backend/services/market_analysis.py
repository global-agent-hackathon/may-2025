from datetime import datetime
from typing import Optional
from backend.settings import LLMConfig, SonarConfig
from backend.utils.llm import get_model, get_sonar_model
from backend.agents.output_parser import LLMOutputParserAgent
from backend.models.response.market_analysis import (
    MarketTrendsResponse,
    CompetitiveAnalysisResponse,
    GrowthProjectionsResponse,
    RegionalTrendsResponse,
)
from agno.agent import Agent
from pydantic import BaseModel
from typing import Type, Union
from backend.plot.factory import get_builder
from backend.utils.cache_decorator import cacheable


class MarketAnalysisService:
    def __init__(self, llm_config: LLMConfig, sonar_config: SonarConfig, netlify_agent):
        self.llm_config = llm_config
        # cache_service will be injected by the dependency injection system
        self.sonar_config = sonar_config
        self.llm_model = get_model(self.llm_config)
        self.sonar_model = get_sonar_model(self.sonar_config)
        self.llm_output_parser = LLMOutputParserAgent(self.llm_model)
        self.netlify_agent = netlify_agent

    async def _execute_llm_analysis(
        self,
        company_name: str,
        prompt: str,
        response_model: Type[BaseModel],
        agent_name: str = "AnalysisAgent",
        use_knowledge_base: bool = False,
    ) -> Union[
        MarketTrendsResponse,
        CompetitiveAnalysisResponse,
        GrowthProjectionsResponse,
        RegionalTrendsResponse,
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

        try:
            chart_data = response.get_plot_data()
            builder = get_builder(chart_data.kind, self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None

        return response

    @cacheable()
    async def get_market_trends(
        self,
        company_name: str,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        """
        Retrieve market trends data for a company.
        Args:
            company_name (str): Name of the company (required)
            industry (str): Name of the industry (required)
            region (str, optional): Region of the company
            start_date (date, optional): Start date for analysis
            end_date (date, optional): End date for analysis
        Returns:
            MarketTrendsResponse: Contains industry, market size, market trend summary, and last updated timestamp.
        """

        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a financial analyst with access to reputable market research sources. Generate a detailed market size trends analysis for the following company:
        - Company Name: {company_name}
        - Industry: {industry or "N/A"}
        - Region: {region or "N/A"}
        - Start Date: {start_date or "N/A"}
        - End Date: {end_date or "N/A"}

        Please provide the following fields in your response:
        - market_size: A list of objects, each with industry , percentage. the different objects represent different industries and their market sizes. (as Pie Chart Data)
        - market_trend_summary: A summary of the market trend whether it is growing, shrinking or stable
        - last_updated: The datetime of the latest data (ISO format)

        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """
        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=MarketTrendsResponse,
            agent_name="MarketTrendsAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_competitive_analysis(
        self,
        company_name: str,
        domain: Optional[str] = None,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        companies_to_compare: Optional[list[str]] = None,
        use_knowledge_base: bool = False,
    ):
        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a financial analyst with access to reputable market research sources. Generate a detailed competitive analysis for the following company:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}
        - Industry: {industry or "N/A"}
        - Region: {region or "N/A"}
        - Companies to Compare: {companies_to_compare or "N/A"}

        Please provide the following fields in your response:
        - top_competitors: A list of objects, each with company_name, industry, market_share, revenue, growth_rate, strengths, weaknesses, differentiating_factors, sources, and confidence
        - summary: A summary of the competitive analysis
        - last_updated: The datetime of the latest data (ISO format)
        
        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """
        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=CompetitiveAnalysisResponse,
            agent_name="CompetitiveAnalysisAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_growth_projections(
        self,
        company_name: str,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a financial analyst with access to reputable market research sources. Generate a detailed growth projections analysis for the following company:
        - Company Name: {company_name}
        - Industry: {industry or "N/A"}
        - Region: {region or "N/A"}
        - Start Date: {start_date or "N/A"}
        - End Date: {end_date or "N/A"}

        Please provide the following fields in your response:
        - projections_timeseries: A list of objects, each with period_start, period_end, projected_value, metric, sources, and confidence
        - summary: A summary of the growth projections
        - last_updated: The datetime of the latest data (ISO format)
        
        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """
        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=GrowthProjectionsResponse,
            agent_name="GrowthProjectionsAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_regional_trends(
        self,
        company_name: str,
        industry: Optional[str] = None,
        regions_of_interest: Optional[list[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a financial analyst with access to reputable market research sources. Generate a detailed regional trends analysis for the following company:
        - Company Name: {company_name}
        - Industry: {industry or "N/A"}
        - Regions of Interest: {regions_of_interest or "N/A"}
        - Start Date: {start_date or "N/A"}
        - End Date: {end_date or "N/A"}

        Please provide the following fields in your response:
        - regional_trends: A list of objects, each with region, period_start, period_end, value, metric, sources, and confidence
        - summary: A summary of the regional trends
        - last_updated: The datetime of the latest data (ISO format)
        
        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """
        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=RegionalTrendsResponse,
            agent_name="RegionalTrendsAgent",
            use_knowledge_base=use_knowledge_base,
        )
