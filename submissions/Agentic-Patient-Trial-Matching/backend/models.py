from pydantic import BaseModel, Field
from typing import List, Optional,Dict, Any

# --- Request Models ---

class TrialSearchRequestContext(BaseModel):
    requestingClinicianId: Optional[str] = None
    searchRadiusKm: Optional[int] = None

class TrialSearchRequest(BaseModel):
    patientId: str = Field(..., description="Unique identifier for the patient")
    context: Optional[TrialSearchRequestContext] = None

# --- Data Models (used internally and in responses) ---

class PatientProfile(BaseModel):
    patientId: str
    condition: str
    stage: Optional[str] = None
    age: int
    priorTherapies: List[str] = Field(..., description="List of prior therapies", default_factory=list)
    biomarkers: List[str] = Field(..., description="List of biomarkers", default_factory=list)
    notes: Optional[str] = None
    

class TrialMatch(BaseModel):
    id: str = Field(..., example="NCT03520686")
    title: str = Field(..., example="Trial for Advanced Widgetitis")
    status: str = Field(..., example="Recruiting")
    phase: str = Field(..., example="Phase 3")
    condition: str = Field(..., example="Widgetitis")
    locations: List[str] = Field(..., example=["City Hospital", "Regional Clinic"], default_factory=list)
    matchRationale: List[str] = Field(..., example=["Matches diagnosis: Widgetitis Stage IV", "Meets age criteria (55)"], default_factory=list)
    flags: List[str] = Field(..., example=["Requires confirmation of eGFR > 60"], default_factory=list)
    detailsUrl: Optional[str] = Field(None, example="https://clinicaltrials.gov/study/NCT03520686")
    contactInfo: Optional[str] = Field(None, example="Dr. Smith, 555-1234")
    rank_score: Optional[float] = Field(None, description="Internal score for ranking") # Usually not sent to frontend
    

# --- Response Models ---

class TrialSearchResponse(BaseModel):
    status: str = "success"
    matches: List[TrialMatch]
    searchTimestamp: str # ISO format string

class NoMatchesResponse(BaseModel):
    status: str = "no_matches_found"
    matches: List = []
    message: str = "No suitable recruiting trials found based on current criteria."
    searchTimestamp: str # ISO format string

# --- Pydantic Models for Agent/Tool Interactions ---
class PatientProfileResponse(BaseModel):
    status: str = Field(..., description="Status of the fetch operation (success, not_found, error)")
    profile: Optional[PatientProfile] = Field(None, description="Patient profile data if successful.")
    message: Optional[str] = Field(None, description="Error or status message.")
    error: Optional[str] = Field(None, description="Detailed error message if status is 'error'.")


class TrialData(BaseModel):
    id: str = Field(..., description="Trial identifier",example="NCT03520686")
    title: str = Field(..., description="Title of the trial")
    condition: str = Field(..., description="Medical condition being studied")
    phase: str = Field(..., description="Trial phase")
    status: str = Field(..., description="Trial status (e.g., Recruiting)")
    min_age: Optional[int] = Field(None, description="Minimum age requirement")
    max_age: Optional[int] = Field(None, description="Maximum age requirement")
    required_markers: List[str] = Field(default_factory=list, description="Required biomarkers")
    exclusions: List[str] = Field(default_factory=list, description="Exclusion criteria")
    inclusions: List[str] = Field(default_factory=list, description="Inclusion criteria")
    eligibility_text: Optional[str] = Field(None, description="Full eligibility criteria text")
    url: Optional[str] = Field(None, description="Trial details URL")
    
class DiscoveredTrialsResponse(BaseModel):
    status: str = Field(..., description="Status of the discovery operation (success, error)")
    trials: Optional[List[TrialData]] = Field(None, description="List of discovered trials if successful.")
    message: Optional[str] = Field(None, description="Error or status message.")
    error: Optional[str] = Field(None, description="Detailed error message if status is 'error'.")

class LLMAnalysisResult(BaseModel):
    decision: str = Field(..., description="LLM's decision (e.g., 'Potential Match').")
    reasoning_steps: List[str] = Field(..., description="LLM's reasoning steps.", default_factory=list)
    match_rationale: List[str] = Field(..., description="Points supporting a match.", default_factory=list)
    flags: List[str] = Field(..., description="Points against a match or needing review.", default_factory=list)

class AnalysisDetails(BaseModel):
    decision: Optional[str] = None
    reasoning_steps: Optional[List[str]] = Field(default_factory=list)
    match_rationale: Optional[List[str]] = Field(default_factory=list)
    flags: Optional[List[str]] = Field(default_factory=list)
    


class TrialAnalysisResponse(BaseModel):
    status: str = Field(..., description="Status of the analysis (success, no_match, error).")
    match_data: Optional[TrialMatch] = Field(None, description="Formatted match data if successful match.")
    llm_analysis: Optional[LLMAnalysisResult] = Field(None, description="Raw LLM analysis details.")
    reason: Optional[str] = Field(None, description="Reason for no_match or error.")
    message: Optional[str] = Field(None, description="Further details or error message.")
    details: Optional[AnalysisDetails] = Field(None, description="Full LLM response for no_match/error")
    
class DiscoverTrialsToolInput(BaseModel):
    patient_id: str
    condition: str
    stage: Optional[str] = None
    age: int
    priorTherapies: List[str] = Field(default_factory=list)
    biomarkers: List[str] = Field(default_factory=list)
    notes: Optional[str] = None