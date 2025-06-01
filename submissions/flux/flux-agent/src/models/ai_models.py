from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AIFieldComputeRequest(BaseModel):
    form_data: Dict[str, Any] = Field(..., description="Form data with user inputs")
    ai_field_id: str = Field(..., description="AI field identifier")
    ai_metadata_prompt: str = Field(..., description="AI metadata prompt with field references")


class AIFieldComputeResponse(BaseModel):
    field_id: str = Field(..., description="Field identifier")
    computed_value: str = Field(..., description="Computed AI value")
    success: bool = Field(..., description="Computation success status")
    error: Optional[str] = Field(None, description="Error message if computation failed") 