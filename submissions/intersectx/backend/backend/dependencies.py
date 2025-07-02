from backend.agents.document_processing import DocumentProcessingEngine
from backend.agents.vector_store import VectorStore
from backend.models.base.users import User
from backend.services.auth import AuthService
from backend.services.cache import CacheService
from backend.services.companies import CompaniesService
from backend.services.news import NewsService
from backend.services.chat import ChatService
from backend.services.files import FilesService
from backend.settings import get_app_settings, AppSettings
from fastapi import Request, Depends
from backend.services.finance import FinanceService
from backend.services.market_analysis import MarketAnalysisService
from backend.services.team import TeamService
from backend.services.customer_sentiment import CustomerSentimentService
from backend.utils.llm import get_model
from backend.services.knowledge import KnowledgeBaseService
from backend.services.partnership_network import PartnershipNetworkService
from backend.services.regulatory_compliance import RegulatoryComplianceService
from backend.services.risk_analysis import RiskAnalysisService
from backend.services.research import ResearchService
from backend.agents.netlify import NetlifyAgent
from backend.services.search_service import SearchService


async def get_user(request: Request):
    if "user" in request.scope:
        return request.scope["user"]

    return None


def get_cache_service(app_settings: AppSettings = Depends(get_app_settings)):
    return CacheService(app_settings.db_config)


def get_knowledge_base_service(
    app_settings: AppSettings = Depends(get_app_settings),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = KnowledgeBaseService(
        app_settings.db_config,
        app_settings.vector_store_config,
    )
    return service


def get_news_service(
    app_settings: AppSettings = Depends(get_app_settings),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = NewsService(
        app_settings.db_config, app_settings.llm_config, app_settings.sonar_config
    )
    service.cache_service = cache_service
    return service


def get_auth_service_settings(
    app_settings: AppSettings = Depends(get_app_settings),
):
    service = AuthService(app_settings.db_config, app_settings.jwt_config)
    return service


def get_company_service(
    app_settings: AppSettings = Depends(get_app_settings),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = CompaniesService(app_settings.db_config)
    service.cache_service = cache_service
    return service


def get_chat_service(app_settings: AppSettings = Depends(get_app_settings)):
    return ChatService(
        app_settings.llm_config, app_settings.db_config, app_settings.mcp_url
    )


def get_document_processing_engine(
    app_settings: AppSettings = Depends(get_app_settings),
):
    return DocumentProcessingEngine(
        get_model(app_settings.llm_config), app_settings.storage_config
    )


def get_vector_store(app_settings: AppSettings = Depends(get_app_settings)):
    return VectorStore(app_settings.db_config, app_settings.vector_store_config)


def get_files_service(
    doc_engine=Depends(get_document_processing_engine),
    vector_store=Depends(get_vector_store),
    app_settings: AppSettings = Depends(get_app_settings),
):
    return FilesService(
        doc_engine=doc_engine,
        vector_store=vector_store,
        mongo_config=app_settings.db_config,
    )


def get_netlify_agent(app_settings: AppSettings = Depends(get_app_settings)):
    return NetlifyAgent(app_settings.netlify_config)


def get_finance_service(
    app_settings: AppSettings = Depends(get_app_settings),
    knowledge_base_service=Depends(get_knowledge_base_service),
    netlify_agent=Depends(get_netlify_agent),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = FinanceService(
        app_settings.llm_config,
        app_settings.sonar_config,
        knowledge_base_service,
        netlify_agent,
    )
    service.cache_service = cache_service
    return service


def get_market_analysis_service(
    app_settings: AppSettings = Depends(get_app_settings),
    netlify_agent=Depends(get_netlify_agent),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = MarketAnalysisService(
        app_settings.llm_config, app_settings.sonar_config, netlify_agent
    )
    service.cache_service = cache_service
    return service


def get_linkedin_team_service(
    app_settings: AppSettings = Depends(get_app_settings),
    netlify_agent=Depends(get_netlify_agent),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = TeamService(
        app_settings.llm_config,
        app_settings.sonar_config,
        netlify_agent,
    )
    service.cache_service = cache_service
    return service


def get_customer_sentiment_service(
    app_settings: AppSettings = Depends(get_app_settings),
    netlify_agent=Depends(get_netlify_agent),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = CustomerSentimentService(
        app_settings.llm_config, app_settings.sonar_config, netlify_agent
    )
    service.cache_service = cache_service
    return service


def get_partnership_network_service(
    netlify_agent=Depends(get_netlify_agent),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = PartnershipNetworkService(netlify_agent)
    service.cache_service = cache_service
    return service


def get_search_service(
    app_settings: AppSettings = Depends(get_app_settings),
    netlify_agent=Depends(get_netlify_agent),
    knowledge_base_service=Depends(get_knowledge_base_service),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = SearchService(
        app_settings.llm_config,
        app_settings.sonar_config,
        knowledge_base_service,
        netlify_agent,
    )
    service.cache_service = cache_service
    return service


def get_regulatory_compliance_service(
    netlify_agent=Depends(get_netlify_agent),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = RegulatoryComplianceService(netlify_agent)
    service.cache_service = cache_service
    return service


def get_risk_analysis_service(
    netlify_agent=Depends(get_netlify_agent),
    cache_service: CacheService = Depends(get_cache_service),
):
    service = RiskAnalysisService(netlify_agent)
    service.cache_service = cache_service
    return service


def get_research_service(
    finance_service=Depends(get_finance_service),
    linkedin_team_service=Depends(get_linkedin_team_service),
    market_analysis_service=Depends(get_market_analysis_service),
    partnership_network_service=Depends(get_partnership_network_service),
    customer_sentiment_service=Depends(get_customer_sentiment_service),
    regulatory_compliance_service=Depends(get_regulatory_compliance_service),
    risk_analysis_service=Depends(get_risk_analysis_service),
    cache_service: CacheService = Depends(get_cache_service),
    app_settings: AppSettings = Depends(get_app_settings),
    knowledge_base_service=Depends(get_knowledge_base_service),
    netlify_agent=Depends(get_netlify_agent),
):
    service = ResearchService(
        finance_service=finance_service,
        linkedin_team_service=linkedin_team_service,
        market_analysis_service=market_analysis_service,
        partnership_network_service=partnership_network_service,
        customer_sentiment_service=customer_sentiment_service,
        regulatory_compliance_service=regulatory_compliance_service,
        risk_analysis_service=risk_analysis_service,
        db_config=app_settings.db_config,
        llm_config=app_settings.llm_config,
        knowledge_base_service=knowledge_base_service,
        netlify_agent=netlify_agent,
    )
    service.cache_service = cache_service
    return service


class CommonDeps:
    user: User = Depends(get_user)
