from datetime import datetime

from backend.models.response.news import NewsItem, NewsItemList
from backend.settings import MongoConnectionDetails
from backend.utils.api_helpers import LOG
from backend.utils.llm import get_model, get_sonar_model
from backend.agents.output_parser import LLMOutputParserAgent
from backend.settings import LLMConfig, SonarConfig
from backend.utils.cache_decorator import cacheable
from agno.agent import Agent
from pydantic import BaseModel
from typing import Type


class NewsService:
    def __init__(
        self,
        mongo_config: MongoConnectionDetails,
        llm_config: LLMConfig,
        sonar_config: SonarConfig,
    ):
        self.mongo_config = mongo_config
        self.llm_config = llm_config
        self.sonar_config = sonar_config
        self.llm_model = get_model(self.llm_config)
        self.sonar_model = get_sonar_model(self.sonar_config)
        self.llm_output_parser = LLMOutputParserAgent(self.llm_model)
        # cache_service will be injected by the dependency injection system

    async def _execute_llm_analysis(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        agent_name: str = "NewsAgent",
    ) -> list[NewsItem]:
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
        s = datetime.now()
        # Use the LLM to generate the content
        content = analysis_agent.run(prompt)
        LOG.info(f"Sonar response generated in {datetime.now() - s} seconds")

        # Parse the LLM output into the response model
        s = datetime.now()
        response = self.llm_output_parser.parse(content.content, response_model)
        LOG.info(f"Chatgpt took to Response parsed in {datetime.now() - s} seconds")
        # 3) Extract actual list of NewsItem
        news_items: list[NewsItem] = response.news_items

        return news_items

    @cacheable()
    async def get_news(
        self, limit: int = None, company_name: str = None, domain: str = None
    ) -> list[NewsItem]:
        """
        Retrieve news data for a company.
        Args:
            company_name (str): Name of the company (required)
            domain (str, optional): Domain of the company
            limit (int, optional): Number of news items to retrieve
        Returns:
            list[NewsItem]: List of news items.
        """

        # Compose a detailed prompt for the LLM to generate all required fields
        prompt = f"""
        The current date is {datetime.now().isoformat()}.
        you are a news analyst. Generate a detailed news description for trending
        - Company Name: {company_name or "N/A"} if company name is not provided, generate news for Trending companies
        - Domain: {domain or "N/A"} if domain is not provided, generate news for Trending companies
        - Limit: {limit}
        
        Please provide the following fields in your response:
        - title: The title of the news item
        - content: The content of the news item
        - source: The source of the news item
        - published_at: The published date of the news item
        - category: The category of the news item
        - image_url: a url to the image of the news item
        - citations: The citations of the news item

        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            prompt=prompt,
            response_model=NewsItemList,
            agent_name="NewsAgent",
        )
