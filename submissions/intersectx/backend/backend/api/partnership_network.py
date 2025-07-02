from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from backend.dependencies import get_partnership_network_service
from backend.services.partnership_network import PartnershipNetworkService
from backend.models.requests.partnership_network import (
    PartnerListRequest,
    StrategicAlliancesRequest,
    NetworkStrengthRequest,
    PartnershipTrendsRequest,
)
from backend.models.response.partnership_network import (
    PartnerListResponse,
    StrategicAlliancesResponse,
    NetworkStrengthResponse,
    PartnershipTrendsResponse,
)

partnership_network_router = APIRouter(
    prefix="/partnership-network", tags=["partnership-network"]
)


@cbv(partnership_network_router)
class PartnershipNetworkAPI:
    partnership_network_service: PartnershipNetworkService = Depends(
        get_partnership_network_service
    )

    @partnership_network_router.post(
        "/partner-list", response_model=PartnerListResponse
    )
    async def get_partner_list(self, req: PartnerListRequest):
        return await self.partnership_network_service.get_partner_list(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
        )

    @partnership_network_router.post(
        "/strategic-alliances", response_model=StrategicAlliancesResponse
    )
    async def get_strategic_alliances(self, req: StrategicAlliancesRequest):
        return await self.partnership_network_service.get_strategic_alliances(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
        )

    @partnership_network_router.post(
        "/network-strength", response_model=NetworkStrengthResponse
    )
    async def get_network_strength(self, req: NetworkStrengthRequest):
        return await self.partnership_network_service.get_network_strength(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
        )

    @partnership_network_router.post(
        "/partnership-trends", response_model=PartnershipTrendsResponse
    )
    async def get_partnership_trends(self, req: PartnershipTrendsRequest):
        return await self.partnership_network_service.get_partnership_trends(
            company_name=req.company_name,
            domain=req.domain,
            industry=req.industry,
            region=req.region,
            start_date=req.start_date,
            end_date=req.end_date,
        )
