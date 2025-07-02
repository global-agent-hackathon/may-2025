from agno.agent import Agent
from pprint import pprint

from dotenv import load_dotenv

from backend.models.response.finance import RevenueAnalysisResponse
from backend.settings import LLMConfig, SonarConfig, get_app_settings

from agno.models.azure import AzureOpenAI
from agno.models.perplexity import Perplexity
from agno.embedder.azure_openai import AzureOpenAIEmbedder
from backend.settings import VectorStoreConfig


def get_model(llm_config: LLMConfig) -> AzureOpenAI:
    return AzureOpenAI(
        id="gpt-4o",
        api_key=llm_config.api_key,
        azure_endpoint=llm_config.api_base,
        azure_deployment=llm_config.llm_deployment_name,
    )


def get_sonar_model(sonar_config: SonarConfig) -> Perplexity:
    return Perplexity(
        id="sonar-pro",
        base_url=sonar_config.base_url,
        api_key=sonar_config.api_key,
    )


def get_embedding_model(vector_store_config: VectorStoreConfig) -> AzureOpenAIEmbedder:
    return AzureOpenAIEmbedder(
        id="text-embedding-ada-002",
        api_key=vector_store_config.api_key,
        azure_endpoint=vector_store_config.base_url,
        azure_deployment=vector_store_config.embedding_model,
    )


if __name__ == "__main__":
    load_dotenv()
    app_settings = get_app_settings()
    model = get_model(app_settings.llm_config)
    sonar_model = get_sonar_model(app_settings.sonar_config)
    agent = Agent(
        name="FinanceAgent",
        model=sonar_model,
        instructions="You are a general assistant helping in answering any questions",
        show_tool_calls=True,
        response_model=RevenueAnalysisResponse,
    )
    response = agent.run("What is the revenue of Microsoft")
    pprint(response)
