from datetime import datetime
from typing import Optional, List, Type, Union
from backend.utils.cache_decorator import cacheable

from agno.agent import Agent
from pydantic import BaseModel

from backend.agents.netlify import NetlifyAgent
from backend.agents.output_parser import LLMOutputParserAgent
from backend.plot.factory import get_builder
from backend.settings import SonarConfig, LLMConfig
from backend.utils.llm import get_model, get_sonar_model
from backend.models.response.customer_sentiment import (
    SentimentSummaryResponse,
    CustomerFeedbackResponse,
    BrandReputationResponse,
    SentimentComparisonResponse,
)


class CustomerSentimentService:
    def __init__(
        self,
        llm_config: LLMConfig,
        sonar_config: SonarConfig,
        netlify_agent: NetlifyAgent,
    ):
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
        SentimentSummaryResponse,
        CustomerFeedbackResponse,
        BrandReputationResponse,
        SentimentComparisonResponse,
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

        # Add citations to the response if available
        if hasattr(response, "citations") and hasattr(content, "citations"):
            response.citations = (
                content.citations.urls if hasattr(content.citations, "urls") else []
            )

        # Add plot iframe_url
        try:
            chart_data = response.get_plot_data()
            builder = get_builder("bar", self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None

        return response

    @cacheable()
    async def get_sentiment_summary(
        self,
        company_name: str,
        domain: Optional[str] = None,
        product: Optional[str] = None,
        region: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        """
        Retrieve sentiment summary for a company.

        Args:
            company_name: Name of the company (required)
            domain: Domain of the company (optional)
            product: Product to focus on (optional)
            region: Region to filter data (optional)
            start_date: Start date for data range (optional)
            end_date: End date for data range (optional)

        Returns:
            SentimentSummaryResponse: Contains sentiment score, breakdown, timeseries, summary, and sources
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}.
        You are a customer sentiment analyst. Generate a detailed sentiment summary for the following company:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}
        - Product: {product or "N/A"}
        - Region: {region or "Global"}
        - Start Date: {start_date or "N/A"}
        - End Date: {end_date or "N/A"}
        
        Please provide the following fields in your response:
        - company_name: The name of the company
        - product: The product name or default if not specified
        - region: The region or "Global" if not specified
        - sentiment_score: A float representing overall sentiment (0-1, higher is better)
        - sentiment_breakdown: An object with exactly these three properties:
          * positive: Integer count of positive mentions
          * negative: Integer count of negative mentions
          * neutral: Integer count of neutral mentions
        - sentiment_timeseries: A list of objects, each with:
          * period_start: An ISO format date string (YYYY-MM-DD)
          * period_end: An ISO format date string (YYYY-MM-DD)
          * positive: Integer count of positive mentions
          * negative: Integer count of negative mentions 
          * neutral: Integer count of neutral mentions
          * sentiment_score: A float representing sentiment for this period
          * sources: List of data source URLs
          * confidence: A float between 0 and 1 representing confidence
        - summary: A brief textual summary of the sentiment analysis
        - sources: List of data sources used (URLs)
        - last_updated: The current timestamp as an ISO format string
        - citations: (This will be automatically populated, do not include in your response)
        
        Be as realistic and detailed as possible. Use plausible numbers and sources.
        IMPORTANT: All dates and timestamps must be in ISO format strings (e.g., "2023-01-01" for dates, "{datetime.now().isoformat()}" for datetimes).
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=SentimentSummaryResponse,
            agent_name="SentimentSummaryAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_customer_feedback(
        self,
        company_name: str,
        domain: Optional[str] = None,
        product: Optional[str] = None,
        region: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        """
        Retrieve customer feedback for a company.

        Args:
            company_name: Name of the company (required)
            domain: Domain of the company (optional)
            product: Product to focus on (optional)
            region: Region to filter data (optional)
            start_date: Start date for data range (optional)
            end_date: End date for data range (optional)

        Returns:
            CustomerFeedbackResponse: Contains feedback items, summary, and sources
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}.
        You are a customer feedback analyst. Generate detailed customer feedback for the following company:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}
        - Product: {product or "N/A"}
        - Region: {region or "Global"}
        - Start Date: {start_date or "N/A"}
        - End Date: {end_date or "N/A"}
        
        Please provide the following fields in your response:
        - company_name: The name of the company
        - product: The product name or default if not specified
        - region: The region or "Global" if not specified
        - feedback_items: A list of feedback items, each with:
          * date: An ISO format date string (YYYY-MM-DD)
          * customer: Customer name if available (can be null)
          * feedback: The actual feedback text
          * sentiment: One of "positive", "negative", or "neutral"
          * sources: List of data source URLs
          * confidence: A float between 0 and 1 representing confidence
        - summary: A brief textual summary of the feedback trends
        - sources: List of data sources used (URLs)
        - last_updated: The current timestamp as an ISO format string
        - citations: (This will be automatically populated, do not include in your response)
        
        Include at least 5 diverse and realistic feedback items from different sources.
        Be as realistic and detailed as possible. Use plausible customer names, feedback text, and sources.
        IMPORTANT: All dates and timestamps must be in ISO format strings (e.g., "2023-01-01" for dates, "{datetime.now().isoformat()}" for datetimes).
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=CustomerFeedbackResponse,
            agent_name="CustomerFeedbackAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_brand_reputation(
        self,
        company_name: str,
        domain: Optional[str] = None,
        region: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        """
        Retrieve brand reputation data for a company.

        Args:
            company_name: Name of the company (required)
            domain: Domain of the company (optional)
            region: Region to filter data (optional)
            start_date: Start date for data range (optional)
            end_date: End date for data range (optional)

        Returns:
            BrandReputationResponse: Contains reputation score, timeseries, summary, and sources
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}.
        You are a brand reputation analyst. Generate detailed brand reputation data for the following company:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}
        - Region: {region or "Global"}
        - Start Date: {start_date or "N/A"}
        - End Date: {end_date or "N/A"}
        
        Please provide the following fields in your response:
        - company_name: The name of the company
        - region: The region or "Global" if not specified
        - reputation_score: A float representing overall brand reputation (0-1, higher is better)
        - reputation_timeseries: A list of objects, each with:
          * period_start: An ISO format date string (YYYY-MM-DD)
          * period_end: An ISO format date string (YYYY-MM-DD)
          * reputation_score: A float representing reputation for this period
          * sources: List of data source URLs
          * confidence: A float between 0 and 1 representing confidence
        - summary: A brief textual summary of the brand reputation trends
        - sources: List of data sources used (URLs)
        - last_updated: The current timestamp as an ISO format string
        - citations: (This will be automatically populated, do not include in your response)
        
        Be as realistic and detailed as possible. Use plausible numbers and sources.
        IMPORTANT: All dates and timestamps must be in ISO format strings (e.g., "2023-01-01" for dates, "{datetime.now().isoformat()}" for datetimes).
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=BrandReputationResponse,
            agent_name="BrandReputationAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_sentiment_comparison(
        self,
        company_name: str,
        competitors: List[str],
        domain: Optional[str] = None,
        product: Optional[str] = None,
        region: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        """
        Compare the sentiment of a target company with its competitors using publicly available data sources.

        Args:
            company_name: Name of the target company
            competitors: List of competitor company names
            domain: Optional domain of the target company
            product: Optional product to focus on
            region: Optional region to filter data
            start_date: Optional start date for data range
            end_date: Optional end date for data range

        Returns:
            SentimentComparisonResponse: Contains comparison data between the target company and competitors
        """
        # Format the competitors list for the prompt
        competitors_str = ", ".join(competitors)

        prompt = f"""
        The current date is {datetime.now().isoformat()}.
        You are a competitive sentiment analyst. Generate a detailed sentiment comparison for the following:
        - Target Company: {company_name}
        - Competitors: {competitors_str}
        - Domain: {domain or "N/A"}
        - Product: {product or "N/A"}
        - Region: {region or "Global"}
        - Start Date: {start_date or "N/A"}
        - End Date: {end_date or "N/A"}
        
        Please provide the following fields in your response:
        - company_name: The name of the target company
        - product: The product name or default if not specified
        - region: The region or "Global" if not specified
        - competitors: List of competitor company names exactly as provided
        - target_sentiment: An object for the target company with:
          * company: Company name (should match the target company name)
          * sentiment_score: A float between -10 and 10 (higher is better)
          * strengths: List of 3-5 commonly mentioned strengths for this company
          * weaknesses: List of 3-5 commonly mentioned weaknesses for this company
        - competitor_sentiments: A list of objects, one for each competitor company, each with:
          * company: Company name (should match the competitor name exactly as provided)
          * sentiment_score: A float between -10 and 10 (higher is better)
          * strengths: List of 3-5 commonly mentioned strengths for this company
          * weaknesses: List of 3-5 commonly mentioned weaknesses for this company
        - summary: A brief textual summary comparing the target company's sentiment position relative to competitors
        - confidence: Overall confidence in the analysis (float between 0 and 1)
        - last_updated: The current timestamp as an ISO format string
        - citations: (This will be automatically populated, do not include in your response)
        
        IMPORTANT: Keep the target company sentiment and competitor sentiments separate - the target company should NOT appear in the competitor_sentiments list.
        
        Be as realistic and detailed as possible. For each company, provide unique and specific strengths/weaknesses
        that would realistically apply to that company and industry. Ensure the sentiment scores have reasonable 
        variation between companies and make logical sense compared to the strengths/weaknesses listed.
        
        IMPORTANT: All dates and timestamps must be in ISO format strings (e.g., "{datetime.now().isoformat()}").
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=SentimentComparisonResponse,
            agent_name="SentimentComparisonAgent",
            use_knowledge_base=use_knowledge_base,
        )
