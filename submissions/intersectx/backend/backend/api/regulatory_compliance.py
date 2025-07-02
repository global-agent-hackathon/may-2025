from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from backend.dependencies import get_regulatory_compliance_service
from backend.services.regulatory_compliance import RegulatoryComplianceService
from backend.models.requests.regulatory_compliance import (
    ComplianceOverviewRequest,
    ViolationHistoryRequest,
    ComplianceRiskRequest,
    RegionalComplianceRequest,
)
from backend.models.response.regulatory_compliance import (
    ComplianceOverviewResponse,
    ViolationHistoryResponse,
    ComplianceRiskResponse,
    RegionalComplianceResponse,
)

regulatory_compliance_router = APIRouter(
    prefix="/regulatory-compliance", tags=["regulatory-compliance"]
)


@cbv(regulatory_compliance_router)
class RegulatoryComplianceAPI:
    regulatory_compliance_service: RegulatoryComplianceService = Depends(
        get_regulatory_compliance_service
    )

    @regulatory_compliance_router.post(
        "/compliance-overview", response_model=ComplianceOverviewResponse
    )
    async def get_compliance_overview(self, req: ComplianceOverviewRequest):
        return await self.regulatory_compliance_service.get_compliance_overview(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
        )

    @regulatory_compliance_router.post(
        "/violation-history", response_model=ViolationHistoryResponse
    )
    async def get_violation_history(self, req: ViolationHistoryRequest):
        return await self.regulatory_compliance_service.get_violation_history(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
            start_date=req.start_date,
            end_date=req.end_date,
        )

    @regulatory_compliance_router.post(
        "/compliance-risk", response_model=ComplianceRiskResponse
    )
    async def get_compliance_risk(self, req: ComplianceRiskRequest):
        return await self.regulatory_compliance_service.get_compliance_risk(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
        )

    @regulatory_compliance_router.post(
        "/regional-compliance", response_model=RegionalComplianceResponse
    )
    async def get_regional_compliance(self, req: RegionalComplianceRequest):
        return await self.regulatory_compliance_service.get_regional_compliance(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            regions=req.regions,
        )
