from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from backend.services.team import TeamService
from backend.models.requests.team import (
    TeamOverviewRequest,
    IndividualPerformanceRequest,
    OrgStructureRequest,
    TeamGrowthRequest,
)
from backend.models.response.team import (
    TeamOverviewResponse,
    IndividualPerformanceResponse,
    OrgStructureResponse,
    TeamGrowthResponse,
)
from backend.dependencies import get_linkedin_team_service

linkedin_team_router = APIRouter(prefix="/linkedin-team", tags=["linkedin-team"])


@cbv(linkedin_team_router)
class LinkedInTeamAPI:
    linkedin_team_service: TeamService = Depends(get_linkedin_team_service)

    @linkedin_team_router.post("/team-overview", response_model=TeamOverviewResponse)
    async def get_team_overview(self, req: TeamOverviewRequest):
        return await self.linkedin_team_service.get_team_overview(
            company_name=req.company_name, domain=req.domain
        )

    @linkedin_team_router.post(
        "/individual-performance", response_model=IndividualPerformanceResponse
    )
    async def get_individual_performance(self, req: IndividualPerformanceRequest):
        return await self.linkedin_team_service.get_individual_performance(
            company_name=req.company_name,
            domain=req.domain,
            individual_name=req.individual_name,
        )

    @linkedin_team_router.post("/org-structure", response_model=OrgStructureResponse)
    async def get_org_structure(self, req: OrgStructureRequest):
        return await self.linkedin_team_service.get_org_structure(
            company_name=req.company_name, domain=req.domain
        )

    @linkedin_team_router.post("/team-growth", response_model=TeamGrowthResponse)
    async def get_team_growth(self, req: TeamGrowthRequest):
        return await self.linkedin_team_service.get_team_growth(
            company_name=req.company_name,
            domain=req.domain,
            start_date=req.start_date,
            end_date=req.end_date,
        )
