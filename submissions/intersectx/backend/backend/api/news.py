from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_utils.cbv import cbv

from backend.dependencies import get_news_service
from backend.models.response.news import NewsItem
from backend.services.news import NewsService
from backend.utils.logger import get_logger

news_router = APIRouter(prefix="/news", tags=["news"])

LOG = get_logger("News API")


@cbv(news_router)
class NewsAPI:
    news_service: NewsService = Depends(get_news_service)

    @news_router.get("/trending", response_model=list[NewsItem])
    async def get_trending_news(
        self, company_name: str = None, limit: int = 10, domain: str = "Tech"
    ) -> list[NewsItem]:
        LOG.debug(
            f"Received Request for Trending News: Company Name: {company_name}, Limit: {limit}, Domain: {domain}"
        )
        return await self.news_service.get_news(
            limit=limit, company_name=company_name, domain=domain
        )
