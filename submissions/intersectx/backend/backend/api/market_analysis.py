from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from backend.dependencies import get_market_analysis_service
from backend.services.market_analysis import MarketAnalysisService
from backend.models.requests.market_analysis import (
    MarketTrendsRequest,
    CompetitiveAnalysisRequest,
    GrowthProjectionsRequest,
    RegionalTrendsRequest,
)
from backend.models.response.market_analysis import (
    MarketTrendsResponse,
    CompetitiveAnalysisResponse,
    GrowthProjectionsResponse,
    RegionalTrendsResponse,
)
from backend.utils.logger import get_logger


market_analysis_router = APIRouter(prefix="/market-analysis", tags=["market-analysis"])

LOG = get_logger("Market Analysis API")


@cbv(market_analysis_router)
class MarketAnalysisCBV:
    market_analysis_service: MarketAnalysisService = Depends(
        get_market_analysis_service
    )

    @market_analysis_router.post("/market-trends", response_model=MarketTrendsResponse)
    async def get_market_trends(self, req: MarketTrendsRequest):
        LOG.debug(f"Received Request for Market Trends: {req.model_dump_json()}")
        return await self.market_analysis_service.get_market_trends(
            company_name=req.company_name,
            industry=req.industry,
            region=req.region,
            start_date=req.start_date,
            end_date=req.end_date,
        )

    @market_analysis_router.post(
        "/competitive-analysis", response_model=CompetitiveAnalysisResponse
    )
    async def get_competitive_analysis(self, req: CompetitiveAnalysisRequest):
        LOG.debug(f"Received Request for Competitive Analysis: {req.model_dump_json()}")
        return await self.market_analysis_service.get_competitive_analysis(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
            companies_to_compare=req.companies_to_compare,
        )

    @market_analysis_router.post(
        "/growth-projections", response_model=GrowthProjectionsResponse
    )
    async def get_growth_projections(self, req: GrowthProjectionsRequest):
        LOG.debug(f"Received Request for Growth Projections: {req.model_dump_json()}")
        return await self.market_analysis_service.get_growth_projections(
            company_name=req.company_name,
            industry=req.industry,
            region=req.region,
            start_date=req.start_date,
            end_date=req.end_date,
        )

    @market_analysis_router.post(
        "/regional-trends", response_model=RegionalTrendsResponse
    )
    async def get_regional_trends(self, req: RegionalTrendsRequest):
        LOG.debug(f"Received Request for Regional Trends: {req.model_dump_json()}")
        return await self.market_analysis_service.get_regional_trends(
            company_name=req.company_name,
            industry=req.industry,
            regions_of_interest=req.regions_of_interest,
            start_date=req.start_date,
            end_date=req.end_date,
        )
