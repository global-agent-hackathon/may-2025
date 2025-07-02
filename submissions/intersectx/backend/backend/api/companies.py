from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv

from backend.dependencies import get_company_service
from backend.models.response.companies import (
    FeaturedCompaniesResponse,
    CompanySearchResult,
    TopInvestorsListResponse,
)
from backend.models.response.research import ResearchResponse
from backend.services.companies import CompaniesService

companies_router = APIRouter(prefix="/companies", tags=["companies"])


@cbv(companies_router)
class CompaniesAPI:
    company_service: CompaniesService = Depends(get_company_service)

    @companies_router.get("/search", response_model=list[CompanySearchResult])
    async def get_companies_list(self, limit: int = 100) -> list[CompanySearchResult]:
        """
        Get a list of companies for search functionality

        Returns simplified company information including name and logo URL
        """
        return await self.company_service.get_companies(limit)

    @companies_router.get("/{companyName}/analysis", response_model=ResearchResponse)
    async def get_company_analysis(self, companyName: str):
        return await self.company_service.get_company_analysis(companyName)

    @companies_router.get("/featured", response_model=FeaturedCompaniesResponse)
    async def get_featured_companies(
        self,
        limit: int = Query(10, description="Number of companies to return"),
        page: int = Query(1, description="Page number for pagination"),
    ) -> FeaturedCompaniesResponse:
        """
        Get featured investment companies.

        This endpoint returns a list of featured companies for investment consideration.
        Optional authentication via Bearer token provides personalized results.
        """
        result = await self.company_service.get_featured_companies(limit, page)
        return result

    @companies_router.get("/top-investors", response_model=TopInvestorsListResponse)
    async def get_top_investors(
        self, limit: int = Query(10, description="Number of top investors to return")
    ):
        """
        Get a list of top investors sorted by portfolio value.
        """
        return await self.company_service.get_top_investors(limit)
