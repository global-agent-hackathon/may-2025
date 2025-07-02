from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from backend.dependencies import get_risk_analysis_service
from backend.services.risk_analysis import RiskAnalysisService
from backend.models.requests.risk_analysis import (
    RegulatoryRisksRequest,
    MarketRisksRequest,
    OperationalRisksRequest,
    LegalRisksRequest,
)
from backend.models.response.risk_analysis import (
    RegulatoryRisksResponse,
    MarketRisksResponse,
    OperationalRisksResponse,
    LegalRisksResponse,
)

risk_analysis_router = APIRouter(prefix="/risk-analysis", tags=["risk-analysis"])


@cbv(risk_analysis_router)
class RiskAnalysisAPI:
    risk_analysis_service: RiskAnalysisService = Depends(get_risk_analysis_service)

    @risk_analysis_router.post(
        "/regulatory-risks", response_model=RegulatoryRisksResponse
    )
    async def get_regulatory_risks(self, req: RegulatoryRisksRequest):
        return await self.risk_analysis_service.get_regulatory_risks(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
        )

    @risk_analysis_router.post("/market-risks", response_model=MarketRisksResponse)
    async def get_market_risks(self, req: MarketRisksRequest):
        return await self.risk_analysis_service.get_market_risks(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
        )

    @risk_analysis_router.post(
        "/operational-risks", response_model=OperationalRisksResponse
    )
    async def get_operational_risks(self, req: OperationalRisksRequest):
        return await self.risk_analysis_service.get_operational_risks(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
        )

    @risk_analysis_router.post("/legal-risks", response_model=LegalRisksResponse)
    async def get_legal_risks(self, req: LegalRisksRequest):
        return await self.risk_analysis_service.get_legal_risks(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
        )
