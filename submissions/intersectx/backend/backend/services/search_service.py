from datetime import datetime
from typing import Type, Union

from agno.agent import Agent
from pydantic import BaseModel

from backend.agents.output_parser import LLMOutputParserAgent
from backend.settings import SonarConfig, LLMConfig
from backend.utils.llm import get_model, get_sonar_model
from backend.utils.cache_decorator import cacheable
from backend.services.knowledge import KnowledgeBaseService
from backend.models.response.search_service import GeneralSearchKnowledgeResponse


class SearchService:
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
        query: str,
        prompt: str,
        response_model: Type[BaseModel],
        agent_name: str = "GeneralSearchKnowledgeAgent",
        use_knowledge_base: bool = False,
    ) -> Union[GeneralSearchKnowledgeResponse,]:
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

        # Use the LLM to generate the content
        content = analysis_agent.run(query)

        # Parse the LLM output into the response model
        response = self.llm_output_parser.parse(content.content, response_model)

        # Attach citations if response is a Pydantic model and has citations
        if hasattr(response, "citations") and hasattr(content, "citations"):
            response.citations = (
                content.citations.urls if hasattr(content.citations, "urls") else []
            )

        return response

    @cacheable()
    async def get_general_search_knowledge(
        self, query: str
    ) -> GeneralSearchKnowledgeResponse:
        """
        Retrieve general search knowledge for a query.
        Args:
            query (str): Query to search for
        Returns:
            GeneralSearchKnowledgeResponse: Contains company name, currency, revenue timeseries,
            total revenue, and last updated timestamp.
        """

        # Compose a detailed prompt for the LLM to generate all required fields
        prompt = f"""
        The current date is {datetime.now().isoformat()}. 
        You are a general search knowledge agent. Generate a detailed general search knowledge for the following query:
        - Query: {query}

        Please provide the following fields in your response:
        - content: The content of the general search knowledge

        Be as realistic and detailed as possible. Use plausible numbers and sources. 
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            query=query,
            prompt=prompt,
            response_model=GeneralSearchKnowledgeResponse,
            agent_name="GeneralSearchKnowledgeAgent",
        )
