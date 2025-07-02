from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    email: str = Field(..., description="Email address of the user")
    first_name: str = Field(..., description="First Name")
    last_name: str = Field(..., description="Last Name")
    token: str = Field(..., description="JWT Token")
    user_type: str = Field(default="vc", description="Type of user: 'vc' or 'founder'")


class FounderConnectedVCsResponse(BaseModel):
    connected_vcs: list[str] = Field(
        ..., description="List of connected VC emails for the founder"
    )


class VCConnectedCompaniesResponse(BaseModel):
    connected_companies: list[str] = Field(
        ..., description="List of connected companies for the VC"
    )
