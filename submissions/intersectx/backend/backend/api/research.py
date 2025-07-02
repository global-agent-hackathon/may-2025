from fastapi import APIRouter, Depends, Path
from fastapi_utils.cbv import cbv

from backend.dependencies import get_research_service
from backend.services.research import ResearchService
from backend.models.response.research import ResearchResponse

research_router = APIRouter(prefix="/research", tags=["research"])


@cbv(research_router)
class ResearchAPI:
    research_service: ResearchService = Depends(get_research_service)

    @research_router.get("/{company_name}", response_model=ResearchResponse)
    async def get_research(self, company_name: str = Path(...)):
        # Placeholder implementation
        return await self.research_service.get_deep_research(company_name)

    @research_router.get(
        "/get-basic-info/{company_name}", response_model=ResearchResponse
    )
    async def get_basic_info(self, company_name: str = Path(...)):
        return await self.research_service.get_research(
            company_name, use_knowledge_base=False
        )
