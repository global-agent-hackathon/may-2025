from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_utils.cbv import cbv
from starlette import status
from pydantic import BaseModel

from backend.dependencies import get_auth_service_settings
from backend.models.requests.auth import (
    SignUpRequest,
    LoginRequest,
    FounderSignupRequest,
    VCSignupRequest,
)
from backend.models.response.auth import (
    FounderConnectedVCsResponse,
    VCConnectedCompaniesResponse,
)
from backend.services.auth import AuthService
from backend.utils.logger import get_logger

auth_router = APIRouter(prefix="/auth", tags=["auth"])

LOG = get_logger("Auth API")


class MakeConnectionRequest(BaseModel):
    founder_email: str
    vc_email: str


@cbv(auth_router)
class AuthorizationApi:
    auth_service: AuthService = Depends(get_auth_service_settings)

    @auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
    async def signup(self, signup_request: SignUpRequest):
        return await self.auth_service.signup(signup_request)

    @auth_router.post("/login", status_code=status.HTTP_200_OK)
    async def login(self, login_request: LoginRequest):
        return await self.auth_service.login(login_request)

    @auth_router.post("/founder-signup", status_code=status.HTTP_201_CREATED)
    async def founder_signup(self, founder_signup_request: FounderSignupRequest):
        LOG.info(f"request{founder_signup_request}")
        return await self.auth_service.founder_signup(founder_signup_request)

    @auth_router.post("/vc-signup", status_code=status.HTTP_201_CREATED)
    async def vc_signup(self, vc_signup_request: VCSignupRequest):
        return await self.auth_service.vc_signup(vc_signup_request)

    @auth_router.post("/make-connection", status_code=status.HTTP_200_OK)
    async def make_connection(self, req: MakeConnectionRequest):
        return await self.auth_service.make_connection(req.founder_email, req.vc_email)

    @auth_router.get(
        "/founder-connected-vcs",
        response_model=FounderConnectedVCsResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_founder_connected_vcs(self, email: str):
        """
        Get the list of connected VC emails for a founder.
        """
        return await self.auth_service.get_founder_connected_vcs(email)

    @auth_router.get(
        "/vc-connected-companies",
        response_model=VCConnectedCompaniesResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_vc_connected_companies(self, email: str):
        """
        Get the list of connected companies for a VC.
        """
        return await self.auth_service.get_vc_connected_companies(email)
