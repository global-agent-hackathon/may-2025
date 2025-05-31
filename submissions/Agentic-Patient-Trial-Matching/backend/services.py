import asyncio
import os
import json
import random
from textwrap import dedent
from typing import List, Union, Dict, Any, Optional, Iterator

# --- OpenAI Library Import for direct client use ---
from openai import AsyncAzureOpenAI as SdkAsyncAzureOpenAI

# --- Pydantic Model for LLM Analysis Output ---
from pydantic import BaseModel, Field # BaseModel and Field are standard Pydantic

# --- Agno Imports ---
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.azure import AzureOpenAI as AgnoAzureOpenAI
from agno.workflow import Workflow, RunEvent, RunResponse
# from agno.storage.sqlite import SqliteStorage # Example if persistent storage is needed

# --- Local Imports ---
# All Pydantic response/data models are now imported from models.py
from models import (
    TrialMatch,
    # TrialSearchResponse, # Not directly used in this workflow's output, but kept for consistency
    PatientProfileResponse,
    # PatientProfile,     # For type hints in tool functions
    DiscoveredTrialsResponse,
    LLMAnalysisResult,      # Used internally by _analyze_trial_match_tool
    TrialAnalysisResponse,
    DiscoverTrialsToolInput,
    TrialData           # For trial validation
)
from logger import setup_logger

# --- Configuration & Initialization ---
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_TYPE = os.getenv("AZURE_OPENAI_API_TYPE", "azure")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME_AGENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_DEPLOYMENT_NAME_TOOL_LLM = os.getenv("LLM_MODEL", AZURE_OPENAI_DEPLOYMENT_NAME_AGENT)

if AZURE_OPENAI_API_KEY: os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
if AZURE_OPENAI_ENDPOINT: os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
if AZURE_OPENAI_API_TYPE: os.environ["OPENAI_API_TYPE"] = AZURE_OPENAI_API_TYPE
if OPENAI_API_VERSION: os.environ["OPENAI_API_VERSION"] = OPENAI_API_VERSION

logger = setup_logger("trial_matcher.services", log_level=os.getenv("LOG_LEVEL", "INFO"), log_file="logs/services.log")

# LLM instance for Agno Agents
# Ensure this is a valid Agno model configuration
agent_llm_config = AgnoAzureOpenAI(
    id=AZURE_OPENAI_DEPLOYMENT_NAME_AGENT, # The deployment name for the agent's reasoning LLM
    # model_name=AZURE_OPENAI_DEPLOYMENT_NAME_AGENT # Some Agno models might use model_name
)


# SDK client for direct use in _analyze_trial_match_tool - initialized globally
# This LLM is specifically for the analysis step if not done by an agent's LLM
azure_sdk_client_for_tool = SdkAsyncAzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION,
)

# --- Mock Data (Not fetched from a SQLite DB to avoid hassle of setup during testing and demo) ---
MOCK_PATIENT_DB = {
    "PATIENT_001": {"patient_id": "PATIENT_001", "condition": "Lung Cancer", "stage": "III", "age": 65, "priorTherapies": ["Chemo X"], "biomarkers": ["EGFR+"], "notes": "ECOG 1"},
    "PATIENT_002": {"patient_id": "PATIENT_002", "condition": "Breast Cancer", "stage": "II", "age": 52, "priorTherapies": [], "biomarkers": ["HER2+"], "notes": "No major comorbidities"},
    "PATIENT_003": {"patient_id": "PATIENT_003", "condition": "Non-Small Cell Lung Cancer", "age": 70, "stage": "IV", "priorTherapies": ["Previous Line Chemo"], "biomarkers": ["EGFR+"], "notes": "ECOG 1, HbA1c 8.1%, Mild CKD Stage 2"},
    "PATIENT_NO_MATCH": {"patient_id": "PATIENT_NO_MATCH", "condition": "Rare Condition Y", "age": 40, "priorTherapies": [], "biomarkers": [], "notes": ""},
    "PATIENT_ERROR": {"patient_id": "PATIENT_ERROR", "condition": "Error Condition", "age": 1, "priorTherapies": [], "biomarkers": [], "notes": ""},
}

MOCK_TRIALS_DB = [
    {"id": "NCT05933044", "title": "Lung Cancer Trial A (EGFR+)", "condition": "Non-Small Cell Lung Cancer", "phase": "3", "status": "Recruiting", "min_age": 50, "max_age": 75, "required_markers": ["EGFR+"], "exclusions": ["Prior immunotherapy", "Brain metastases"], "inclusions": ["Stage III or IV", "ECOG 0-1"], "eligibility_text": "Must have documented EGFR mutation. No prior treatment with EGFR TKIs. Adequate organ function required.", "url": "https://clinicaltrials.gov/study/NCT05933044"},
    {"id": "NCT03520686", "title": "Lung Cancer Trial B (General)", "condition": "Non-Small Cell Lung Cancer", "phase": "2", "status": "Recruiting", "min_age": 18, "max_age": None, "required_markers": [], "exclusions": ["Active autoimmune disease"], "inclusions": ["Advanced or metastatic NSCLC", "At least one prior line of therapy"], "eligibility_text": "Patients with measurable disease per RECIST v1.1.", "url": "https://clinicaltrials.gov/study/NCT03520686"},
    # ... other trials
]

# --- Tool Functions (These will be equipped to Agents) ---
async def _fetch_patient_profile_tool(patient_id: str) -> Dict[str, Any]:
    logger.debug(f"Executing _fetch_patient_profile_tool for {patient_id}")
    await asyncio.sleep(random.uniform(0.1, 0.3)) # Simulate IO
    if patient_id == "PATIENT_ERROR":
        return {"error": "Simulated database connection error", "status": "error"}
    profile_data = MOCK_PATIENT_DB.get(patient_id)
    if profile_data:
        return {"status": "success", "profile": profile_data}
    else:
        return {"status": "not_found", "message": f"Patient ID {patient_id} not found."}

#Pydantic model definition does not work, openAI keeps on giving error
#Invalid schema for function '_discover_trials_tool': In context=('properties', 'patient_profile'), 'propertyNames' is not permitted.
async def _discover_trials_tool(patient_id: str, 
                                condition: str, 
                                age: int, 
                                stage: Optional[str] = None, 
                                priorTherapies: Optional[List[str]] = None,
                                biomarkers: Optional[List[str]] = None,
                                notes: Optional[str] = None) -> Dict[str, Any]:
    """Discover trials matching a patient's profile.

    Args:
        patient_profile: Patient profile data conforming to DiscoverTrialsToolInput.

    Returns:
        Dict containing trial matches or error information.
    """
    profile_data_dict = {"patient_id": patient_id, "condition": condition, "age": age, "stage": stage, "priorTherapies": priorTherapies, "biomarkers": biomarkers, "notes": notes}
    patient_profile = DiscoverTrialsToolInput(**profile_data_dict)
    try:

        patient_condition = patient_profile.condition.lower()
        if not patient_condition:
            return {"status": "error", "error": "Patient profile missing condition."}
        await asyncio.sleep(random.uniform(0.2, 0.5)) # To mock real-world asynchronous operations that involve waiting for I/O

        logger.debug(f"[_discover_trials_tool] MOCK_TRIALS_DB before filtering: {json.dumps(MOCK_TRIALS_DB)}")
        relevant_trials_models: List[TrialData] = []
        for t_dict in MOCK_TRIALS_DB:

            if patient_condition in t_dict.get("condition", "").lower() and t_dict.get("status") == "Recruiting":
                try:
                    relevant_trials_models.append(TrialData(**t_dict))
                except Exception as e:
                    logger.warning(f"[_discover_trials_tool] Could not parse trial dict into TrialData model: {t_dict}. Error: {e}")
                    continue

        ids_from_models = [model.id for model in relevant_trials_models]
        logger.debug(f"[_discover_trials_tool] IDs of relevant_trials_models (before model_dump): {ids_from_models}")

        result_to_return = {"status": "success", "trials": [model.model_dump() for model in relevant_trials_models]}
        logger.debug(f"[_discover_trials_tool] EXACT output being returned: {json.dumps(result_to_return)}")

        return result_to_return

    except AttributeError as ae: # Catch issues like patient_profile.condition if it's not the expected model
        logger.error(f"AttributeError in _discover_trials_tool (likely patient_profile not a DiscoverTrialsToolInput model): {ae}", exc_info=True)
        return {"status": "error", "error": f"Internal tool error: {ae}"}
    except Exception as e:
        logger.error(f"Exception in _discover_trials_tool: {e}", exc_info=True)
        return {"status": "error", "error": f"Unexpected tool error: {str(e)}"}

_ANALYSIS_PROMPT_TEMPLATE_FOR_LLM_TOOL = dedent("""
    You are an expert AI assistant specialized in clinical trial matching.
    Analyze the patient against the trial criteria **meticulously**.
    Patient Profile Snippet: {patient_profile_str}
    Trial Details Snippet: {trial_details_str}
    **Think step-by-step** comparing patient details against trial criteria.
    **Decision:** Conclude 'Potential Match', 'Likely Not a Match', or 'Uncertain'.
    **Rationale:** List specific points supporting a match.
    **Flags:** List specific points against a match or needing review.
    **Output ONLY a JSON object** with keys: "decision", "reasoning_steps", "match_rationale", "flags".
""")

#Pydantic model definition does not work, openAI keeps on giving error
#Invalid schema for function '_analyze_trial_match_tool': In context=('properties', 'patient_profile'), 'propertyNames' is not permitted.
async def _analyze_trial_match_tool(
    # Required Patient Profile Fields
    patient_id: str, 
    patient_condition: str, 
    patient_age: int,       
    
    # Required Trial Data Fields
    trial_id: str,    
    trial_title: str,
    trial_condition: str, 
    trial_phase: str,
    trial_status: str,

    # Optional Patient Profile Fields
    patient_stage: Optional[str] = None,
    patient_prior_therapies: Optional[List[str]] = None, 
    patient_biomarkers: Optional[List[str]] = None,    
    patient_notes: Optional[str] = None,
    
    # Optional Trial Data Fields
    trial_min_age: Optional[int] = None,
    trial_max_age: Optional[int] = None,
    trial_required_markers: Optional[List[str]] = None, 
    trial_exclusions: Optional[List[str]] = None,         
    trial_inclusions: Optional[List[str]] = None,         
    trial_eligibility_text: Optional[str] = None,
    trial_url: Optional[str] = None
) -> Dict[str, Any]:

    logger.debug(f"Executing _analyze_trial_match_tool for trial_id: {trial_id}")

    # Handle optional lists for patient profile
    actual_patient_prior_therapies = patient_prior_therapies or []
    actual_patient_biomarkers = patient_biomarkers or []
    
    # Handle optional lists for trial data
    actual_trial_required_markers = trial_required_markers or []
    actual_trial_exclusions = trial_exclusions or []
    actual_trial_inclusions = trial_inclusions or []

    # For the LLM prompt template
    patient_profile_for_prompt = {
        "age": patient_age, 
        "condition": patient_condition, # Patient's condition
        "stage": patient_stage,
        "biomarkers": actual_patient_biomarkers,
        "notes": patient_notes
    }
    # For the LLM prompt template, use the specific trial fields
    trial_details_for_prompt = {
        "min_age": trial_min_age,
        "max_age": trial_max_age,
        "condition": trial_condition, # Trial's target condition
        "required_markers": actual_trial_required_markers,
        "inclusions": actual_trial_inclusions,
        "exclusions": actual_trial_exclusions
    }

    patient_profile_str_for_prompt = json.dumps(patient_profile_for_prompt)
    trial_details_str_for_prompt = json.dumps(trial_details_for_prompt)
    
    prompt_content = _ANALYSIS_PROMPT_TEMPLATE_FOR_LLM_TOOL.format(
        patient_profile_str=patient_profile_str_for_prompt, # Use the new var name
        trial_details_str=trial_details_str_for_prompt    # Use the new var name
    )
    
    messages_for_sdk: list[dict[str, str]] = [
        {"role": "system", "content": "You output ONLY valid JSON."},
        {"role": "user", "content": prompt_content}
    ]
    raw_llm_response_content = None
    try:
        #The use of the OpenAI SDK directly has been chosen for control and precision.
        chat_completion = await azure_sdk_client_for_tool.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME_TOOL_LLM,
            messages=messages_for_sdk,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        if chat_completion.choices and chat_completion.choices[0].message:
            raw_llm_response_content = chat_completion.choices[0].message.content
        if not raw_llm_response_content:
            return {"status": "error", "message": "LLM returned empty content (SDK)."}

        parsed_llm_data = LLMAnalysisResult(**json.loads(raw_llm_response_content))
        # Use trial_id (the parameter) for logging
        logger.debug(f"LLM analysis (SDK) for trial {trial_id}: {parsed_llm_data.decision}")

        if parsed_llm_data.decision == "Potential Match":
            # Use trial_phase (the parameter)
            phase_value = f"Phase {trial_phase}" if trial_phase not in [None, "N/A", ""] else "N/A"
            
            # Construct TrialMatch using the direct parameter values
            match_data = TrialMatch(
                id=trial_id,             
                title=trial_title,       
                status=trial_status,     
                phase=phase_value,
                condition=trial_condition, 
                locations=["Location Pending API"], 
                matchRationale=parsed_llm_data.match_rationale, 
                flags=parsed_llm_data.flags,
                detailsUrl=trial_url,    
                contactInfo="Contact Pending API", 
                rank_score=round(1.0 - (len(parsed_llm_data.flags) * 0.1), 2)
            )
            # TrialAnalysisResponse expects a TrialMatch Pydantic object for match_data
            return {"status": "success", "match_data": match_data, "llm_analysis": parsed_llm_data}
        else:
            # TrialAnalysisResponse expects an LLMAnalysisResult Pydantic object for llm_analysis
            return {"status": "no_match", "reason": parsed_llm_data.decision, "details": parsed_llm_data.model_dump(), "llm_analysis": parsed_llm_data}
            
    except json.JSONDecodeError as e:
        logger.error(f"SDK JSON Parsing Error: {e}. Raw: {raw_llm_response_content}", exc_info=True)
        return {"status": "error", "message": "LLM output parsing failed (SDK)."}
    except NameError as ne:
        logger.error(f"NameError in _analyze_trial_match_tool: {ne}", exc_info=True)
        return {"status": "error", "message": f"NameError in tool: {ne}"}
    except Exception as e:
        logger.error(f"SDK LLM Call Error or other Exception in _analyze_trial_match_tool: {e}", exc_info=True)
        return {"status": "error", "message": f"LLM API call failed (SDK) or other tool error: {str(e)}"}


# --- Define Clinical Trial Matching Workflow ---
class ClinicalTrialMatchingWorkflow(Workflow):
    description: str = "Orchestrates agents to find clinical trial matches for a patient using a direct workflow with Agents."

    patient_profiler_agent: Agent
    trial_discoverer_agent: Agent
    trial_analyzer_agent: Agent

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.patient_profiler_agent = Agent(
            name="PatientProfilerAgent",
            role="Fetches a patient's profile using their ID.",
            model=agent_llm_config,
            tools=[_fetch_patient_profile_tool],
            instructions="You will be given a patient_id. Use the `_fetch_patient_profile_tool` with this patient_id to get the profile. Output the result from the tool.",
            response_model=PatientProfileResponse,
            structured_outputs=True,
        )        

        self.trial_discoverer_agent = Agent(
            name="TrialDiscovererAgent",
            role="Discovers clinical trials based on a patient's profile.",
            model=agent_llm_config,
            tools=[_discover_trials_tool],
            # tool_choice={"type": "function", "function": {"name": "_discover_trials_tool"}}, <-- Going into infinite loop if used
            instructions=(
                "You will receive a JSON string containing a 'patient_profile' object. "
                "You are FORCED to call the `_discover_trials_tool`. "
                "Extract the necessary values from the 'patient_profile' object in your input "
                "to use as named arguments for the `_discover_trials_tool` (patient_id, condition, age, etc.). "
                "The `_discover_trials_tool` will return a JSON string. "
                "Your *only* task is to output this EXACT JSON string that the tool returns. "
                "Do not modify it in any way. Do not try to parse it or reformat it. Output the raw JSON string."
            ),
            response_model=DiscoveredTrialsResponse,
            structured_outputs=True,
            show_tool_calls=True
        )

        self.trial_analyzer_agent = Agent(
            name="TrialAnalyzerAgent",
            role="Analyzes a single trial against a patient's profile for a match.",
            model=agent_llm_config, 
            tools=[(_analyze_trial_match_tool)],
            # tool_choice = {"type": "function", "function": {"name": "_analyze_trial_match_tool"}}, <-- Going into infinite loop if used
            instructions=["You will be given a patient_profile (JSON string). Parse it into a dictionary. This dictionary is the 'patient_profile' argument for the '_discover_trials_tool'. Call the tool and output its result.", "DO NOT CREATE ANY TRIAL IDs YOURSELF."],
            response_model=TrialAnalysisResponse, 
            structured_outputs=True,
            show_tool_calls=True 
        )


    async def _get_cached_data(self, key_prefix: str, patient_id: str) -> Optional[Any]:
        key = f"{key_prefix}_{patient_id}"
        data = self.session_state.get(key)
        if data:
            logger.debug(f"Workflow cache hit for key: {key}")
            
            return data
        logger.debug(f"Workflow cache miss for key: {key}")
        return None

    async def _add_cached_data(self, key_prefix: str, patient_id: str, data: Any):
        key = f"{key_prefix}_{patient_id}"
        logger.debug(f"Workflow caching data for key: {key}")
        
        if hasattr(data, 'model_dump'):
            self.session_state[key] = data.model_dump()
        else:
            self.session_state[key] = data


    # # This synchronous run method is generally not ideal if your primary entry is async.
    # # It's kept for compatibility with how Agno might expect to call workflows in some contexts.
    # def run(self, patient_id: str, use_cache: bool = True) -> Iterator[RunResponse]:
    #     logger.warning(
    #         "Synchronous Workflow.run() called. For async execution from FastAPI, "
    #         "the run_trial_matching_workflow (async) function is preferred."
    #     )
    #     # This path would require careful handling of event loops if an outer loop is running.
    #     # For simplicity in this context, we'll assume it's called where it can manage its own loop
    #     # or that it won't be the primary execution path from an async framework.
    #     if asyncio.get_event_loop().is_running():
    #         logger.error("Synchronous run() cannot be reliably called when an event loop is already running.")
    #         yield RunResponse(
    #             content={"error_type": "ASYNC_CONFLICT", "message": "Sync run called with running event loop."},
    #             event=RunEvent.workflow_completed, run_id=self.run_id)
    #         return

    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     try:
    #         content, event = loop.run_until_complete(
    #             self._arun_steps(patient_id, use_cache)
    #         )
    #         yield RunResponse(content=content, event=event, run_id=self.run_id)
    #     except Exception as e:
    #         logger.error(f"Workflow run failed in synchronous wrapper for {patient_id}: {e}", exc_info=True)
    #         yield RunResponse(
    #             content={"error_type": "WORKFLOW_SYNC_EXECUTION_ERROR", "message": str(e)},
    #             event=RunEvent.workflow_completed, run_id=self.run_id )
    #     finally:
    #         loop.close()


    async def _arun_steps(self, patient_id: str, use_cache: bool) -> tuple[Union[List[Dict[str, Any]], Dict[str, Any]], RunEvent]:
        # 0. Check cache for final result
        if use_cache:
            cached_final_result = await self._get_cached_data("final_matches", patient_id)
            if cached_final_result is not None and isinstance(cached_final_result, (list, dict)):
                logger.info(f"Returning cached final result for patient {patient_id}")
                return cached_final_result, RunEvent.workflow_completed

        # 1. Fetch Patient Profile using Agent
        logger.info(f"Step 1: Fetching patient profile for {patient_id} using Agent")
        profile_data: Optional[Dict[str, Any]] = None
        patient_profile_response_obj: Optional[PatientProfileResponse] = None

        if use_cache:
            cached_profile_dict = await self._get_cached_data("patient_profile_agent_response", patient_id)
            if cached_profile_dict:
                try:
                    patient_profile_response_obj = PatientProfileResponse(**cached_profile_dict)
                    if patient_profile_response_obj.status == "success" and patient_profile_response_obj.profile:
                        profile_data = patient_profile_response_obj.profile
                except Exception as e:
                    logger.warning(f"Could not validate cached patient profile: {e}")


        if not profile_data:
            profiler_response: RunResponse = await self.patient_profiler_agent.arun(patient_id) # Agent's async run
            if profiler_response and isinstance(profiler_response.content, PatientProfileResponse):
                patient_profile_response_obj = profiler_response.content
                if use_cache:
                    await self._add_cached_data("patient_profile_agent_response", patient_id, patient_profile_response_obj) # Cache the Pydantic object's dict
            else:
                err_msg = "Patient Profiler Agent did not return valid PatientProfileResponse."
                logger.error(f"{err_msg} Content: {profiler_response.content if profiler_response else 'None'}")
                return {"error_type": "AGENT_RESPONSE_ERROR", "agent": "PatientProfilerAgent", "message": err_msg}, RunEvent.workflow_completed

            if patient_profile_response_obj.status == "success" and patient_profile_response_obj.profile:
                profile_data = patient_profile_response_obj.profile
            elif patient_profile_response_obj.status == "not_found":
                logger.warning(f"Patient {patient_id} not found by agent.")
                return {"error_type": "PATIENT_NOT_FOUND", "message": patient_profile_response_obj.message or f"Patient {patient_id} not found."}, RunEvent.workflow_completed
            else: # Error
                err_msg = patient_profile_response_obj.message or patient_profile_response_obj.error or "Agent failed to fetch profile."
                logger.error(f"Error from PatientProfilerAgent for {patient_id}: {err_msg}")
                return {"error_type": "ERROR_FETCHING_PATIENT", "message": err_msg}, RunEvent.workflow_completed

        if not profile_data:
            return {"error_type": "INTERNAL_ERROR", "message": "Patient profile became unavailable after agent fetch."}, RunEvent.workflow_completed

        # 2. Discover Trials using Agent
        logger.info(f"Step 2: Discovering trials for patient {patient_id} using Agent")
        discovered_trials_list: Optional[List[TrialData]] = None 
        discoverer_response_obj: Optional[DiscoveredTrialsResponse] = None

        if use_cache:
            cached_trials_dict = await self._get_cached_data("discovered_trials_agent_response", patient_id)
            if cached_trials_dict:
                try:
                    discoverer_response_obj = DiscoveredTrialsResponse(**cached_trials_dict)
                    if discoverer_response_obj.status == "success" and discoverer_response_obj.trials is not None:
                        # Ensure that cached trials are TrialData instances
                        if all(isinstance(t, TrialData) for t in discoverer_response_obj.trials):
                            discovered_trials_list = discoverer_response_obj.trials
                        elif all(isinstance(t, dict) for t in discoverer_response_obj.trials):
                            logger.info("Cached trials are dicts, converting to TrialData instances.")
                            discovered_trials_list = [TrialData(**t) for t in discoverer_response_obj.trials]
                        else:
                            logger.warning("Cached trials are of mixed or unexpected types. Will refetch.")
                            discovered_trials_list = None # Force refetch
                except Exception as e:
                    logger.warning(f"Could not validate cached discovered trials: {e}. Will refetch.")
                    discovered_trials_list = None # Force refetch
        
        if discovered_trials_list is None: # If not found in cache or cache was invalid
            logger.info(f"Cache miss or invalid for discovered_trials_agent_response. Fetching from agent for patient {patient_id}.")
            profile_dict_for_agent = profile_data.model_dump() if hasattr(profile_data, 'model_dump') else profile_data
            agent_input_args_obj = {"patient_profile": profile_dict_for_agent}
            discoverer_input_json = json.dumps(agent_input_args_obj)
            logger.debug(f"Passing to TrialDiscovererAgent.arun(): {discoverer_input_json}")
            
            try:
                discoverer_agent_response = await self.trial_discoverer_agent.arun(discoverer_input_json)
            except Exception as e:
                logger.error(f"Exception directly from TrialDiscovererAgent.arun(): {e}", exc_info=True)
                return {"error_type": "AGENT_RUN_EXCEPTION", "agent": "TrialDiscovererAgent", "message": str(e)}, RunEvent.workflow_completed

            # ---- START CRITICAL LOGS for debussing infinite loop issue (finally found forced tool use in the agent was the problem)----
            if not discoverer_agent_response:
                logger.debug("TrialDiscovererAgent.arun() returned a None response.")
                return {"error_type": "AGENT_EMPTY_RESPONSE", "agent": "TrialDiscovererAgent", "message": "Agent returned None"}, RunEvent.workflow_completed

            logger.debug(f"TrialDiscovererAgent - Raw RunResponse.content: {str(discoverer_agent_response.content)[:1000]}")
            if hasattr(discoverer_agent_response.content, 'model_dump_json') and discoverer_agent_response.content is not None : # check for None
                logger.debug(f"TrialDiscovererAgent - Content (as Pydantic model): {discoverer_agent_response.content.model_dump_json(indent=2)}")
            
            if discoverer_agent_response.tools:
                logger.debug(f"TrialDiscovererAgent - Number of tool executions recorded: {len(discoverer_agent_response.tools)}")
                for i, tool_execution in enumerate(discoverer_agent_response.tools):
                    tool_result_str = str(tool_execution.result)
                    logger.debug(
                        f"TrialDiscovererAgent - Recorded ToolExecution {i}: "
                        f"Name='{tool_execution.tool_name}', "
                        f"Args='{tool_execution.tool_args}', "
                        f"Result (first 1000 chars)='{tool_result_str[:1000]}', "
                        f"Error='{tool_execution.tool_call_error}'"
                    )
                    if tool_execution.tool_name == "_discover_trials_tool" and tool_execution.result:
                         logger.debug(f"FULL _discover_trials_tool RAW Result from ToolExecution.result: {tool_execution.result}")
            else:
                logger.warning("TrialDiscovererAgent - No tool executions recorded in RunResponse.tools (after agent.arun)")

            if discoverer_agent_response.thinking:
                 logger.debug(f"TrialDiscovererAgent - Thinking: {discoverer_agent_response.thinking}")
            # ---- END CRITICAL LOGS ----

            # Process the response from the agent
            if isinstance(discoverer_agent_response.content, str):
                raw_json_from_agent = discoverer_agent_response.content
                logger.info(f"TrialDiscovererAgent returned raw string: {raw_json_from_agent}")
                try:
                    tool_output_dict = json.loads(raw_json_from_agent)
                    if tool_output_dict.get("status") == "success":
                        trials_from_tool_dict = tool_output_dict.get("trials", [])
                        parsed_trials = [TrialData(**trial_dict) for trial_dict in trials_from_tool_dict]
                        discoverer_response_obj = DiscoveredTrialsResponse(status="success", trials=parsed_trials)
                    else:
                        discoverer_response_obj = DiscoveredTrialsResponse(
                            status=tool_output_dict.get("status", "error"), 
                            error=tool_output_dict.get("error", "Unknown error from tool output string"),
                            message=tool_output_dict.get("message")
                        )
                    if use_cache:
                        await self._add_cached_data("discovered_trials_agent_response", patient_id, discoverer_response_obj)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON string from TrialDiscovererAgent: {e}. String was: {raw_json_from_agent}")
                    return {"error_type": "AGENT_BAD_JSON_STRING", "agent": "TrialDiscovererAgent", "message": "Agent returned unparsable JSON string."}, RunEvent.workflow_completed
            
            # This case should ideally not be hit if response_model is None and structured_outputs is False
            elif isinstance(discoverer_agent_response.content, DiscoveredTrialsResponse):
                logger.info("TrialDiscovererAgent returned a DiscoveredTrialsResponse Pydantic model directly.")
                discoverer_response_obj = discoverer_agent_response.content
                if use_cache:
                    await self._add_cached_data("discovered_trials_agent_response", patient_id, discoverer_response_obj)
            else:
                err_msg = f"TrialDiscovererAgent returned unexpected content type: {type(discoverer_agent_response.content)}. Content: {str(discoverer_agent_response.content)[:500]}"
                logger.error(err_msg)              
                return {"error_type": "AGENT_UNEXPECTED_RESPONSE_TYPE", "agent": "TrialDiscovererAgent", "message": err_msg}, RunEvent.workflow_completed
            
            # Populate discovered_trials_list from the processed discoverer_response_obj
            if discoverer_response_obj and discoverer_response_obj.status == "success":
                discovered_trials_list = discoverer_response_obj.trials or []
            elif discoverer_response_obj: # Error or other non-success status from agent/tool
                err_msg = discoverer_response_obj.message or discoverer_response_obj.error or "Agent/tool failed to discover trials."
                logger.error(f"Error from TrialDiscovererAgent or tool processing for {patient_id}: {err_msg}")
                return {"error_type": "ERROR_DISCOVERING_TRIALS", "message": err_msg}, RunEvent.workflow_completed
            else: # discoverer_response_obj is None, meaning some path above didn't populate it.
                logger.error("discoverer_response_obj is None after agent call and processing. This should not happen.")
                return {"error_type": "INTERNAL_WORKFLOW_ERROR", "message": "Failed to get response object from discoverer agent."}, RunEvent.workflow_completed

        # After cache or agent call, check discovered_trials_list
        if discovered_trials_list is None : # Should be an empty list if no trials, not None
             logger.error("discovered_trials_list is still None after cache and agent logic. This indicates a flaw in population.")
             #This means it didn't go into the "if discovered_trials_list is None:" block above, or failed within.
             #It might also mean an error occurred within that block before discoverer_response_obj was processed.
             return {"error_type": "INTERNAL_WORKFLOW_ERROR", "message": "Trial list not populated."}, RunEvent.workflow_completed

        if not discovered_trials_list: # Handles empty list: no trials found
            logger.info(f"No trials found by agent for patient {patient_id}.")
            if use_cache and not await self._get_cached_data("final_matches", patient_id): # Avoid re-caching empty if already cached
                await self._add_cached_data("final_matches", patient_id, [])
            return [], RunEvent.workflow_completed
        
        # Log before Step 3
        logger.info(f"Data prepared for TrialAnalyzerAgent. Number of trials in discovered_trials_list: {len(discovered_trials_list)}")
        for i, trial_item_for_analyzer in enumerate(discovered_trials_list):
            if hasattr(trial_item_for_analyzer, 'model_dump_json'):
                logger.debug(f"Trial {i} for Analyzer: {trial_item_for_analyzer.model_dump_json(indent=2)}")
            else: 
                 logger.debug(f"Trial {i} for Analyzer (raw dict, unexpected): {json.dumps(trial_item_for_analyzer, indent=2)}")
        # 3. Analyze Each Trial using Agent
        logger.info(f"Step 3: Analyzing {len(discovered_trials_list)} discovered trials for {patient_id} using Agent")
        potential_matches_models: List[TrialMatch] = []

        for trial_data in discovered_trials_list: # trial_data is a TrialData model
            trial_id = trial_data.id
            logger.debug(f"Analyzing trial {trial_id} using Agent...")            
            profile_dict = profile_data.model_dump() if hasattr(profile_data, 'model_dump') else profile_data
            # Convert trial Pydantic model to dict for analysis
            trial_dict = trial_data.model_dump()
            analyzer_input = {"patient_profile": profile_dict, "trial": trial_dict}
            analyzer_input_json = json.dumps(analyzer_input)
            logger.debug(f"Analyzing trial {trial_id} with input: {analyzer_input_json}")
            analyzer_agent_response: RunResponse = await self.trial_analyzer_agent.arun(analyzer_input_json)

            if analyzer_agent_response and isinstance(analyzer_agent_response.content, TrialAnalysisResponse):
                analysis_result_obj = analyzer_agent_response.content

                if analysis_result_obj.status == "success" and analysis_result_obj.match_data:
                    logger.info(f"Potential match from Agent: Trial {trial_id} for patient {patient_id}")
                    # match_data should be a TrialMatch object because TrialAnalysisResponse has match_data: Optional[TrialMatch]
                    potential_matches_models.append(analysis_result_obj.match_data)
                elif analysis_result_obj.status == "error":
                    logger.warning(f"Error from TrialAnalyzerAgent for trial {trial_id}: {analysis_result_obj.message or analysis_result_obj.reason}")
                else: # no_match or other
                    logger.debug(f"No match from Agent for trial {trial_id}: {analysis_result_obj.reason}")
            else:
                logger.error(f"Trial Analyzer Agent for trial {trial_id} did not return valid TrialAnalysisResponse. Content: {analyzer_agent_response.content if analyzer_agent_response else 'None'}")

        # 4. Compile Final Results
        logger.info(f"Step 4: Compiling final results. Found {len(potential_matches_models)} potential matches from agent analyses.")
        # Convert list of TrialMatch Pydantic models to list of dictionaries
        final_match_list_dicts = [match.model_dump() for match in potential_matches_models]

        if use_cache:
            await self._add_cached_data("final_matches", patient_id, final_match_list_dicts)

        return final_match_list_dicts, RunEvent.workflow_completed


# --- Main async function to run the workflow (called by API endpoint) ---
async def run_trial_matching_workflow(patient_id: str, use_cache: bool = True) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    logger.info(f"run_trial_matching_workflow (async orchestrator with Agents) for patient: {patient_id}")

    workflow_session_id = f"direct_workflow_agents_for_{patient_id}"
    trial_matcher_workflow = ClinicalTrialMatchingWorkflow(
        session_id=workflow_session_id,
        debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true"
    )

    final_output: Union[List[Dict[str, Any]], Dict[str, Any]]

    try:
        content, event = await trial_matcher_workflow._arun_steps(
            patient_id=patient_id,
            use_cache=use_cache
        )
        final_output = content 

        if event == RunEvent.workflow_completed:
            if isinstance(final_output, list):
                 logger.info(f"Workflow with Agents for {patient_id} completed successfully. Matches: {len(final_output)}")
            elif isinstance(final_output, dict) and "error_type" in final_output:
                 logger.warning(f"Workflow with Agents for {patient_id} completed by reporting an error: {final_output.get('message')}")
            else: # Should ideally not happen if _arun_steps returns correctly
                 logger.error(f"Workflow with Agents for {patient_id} completed with unexpected output format: {final_output}")
                 final_output = {"error_type": "WORKFLOW_BAD_AGENT_OUTPUT_FORMAT", "message": "Workflow completed with unexpected output."}
        else: # Should not happen if _arun_steps guarantees workflow_completed event
            logger.error(f"Workflow with Agents for {patient_id} _arun_steps returned unexpected event: {event}. Output: {final_output}")
            final_output = {"error_type": "WORKFLOW_UNEXPECTED_AGENT_EVENT", "message": f"Unexpected event from _arun_steps: {event}"}

    except Exception as e:
        logger.error(f"Exception during agent-based workflow execution for {patient_id}: {e}", exc_info=True)
        final_output = {"error_type": "WORKFLOW_AGENT_UNHANDLED_EXCEPTION", "message": str(e)}

    return final_output


# --- Example Usage 3062603---
async def main():
    test_patient_ids = ["PATIENT_001", "PATIENT_002", "PATIENT_NO_MATCH", "PATIENT_ERROR"]
    # test_patient_ids = ["PATIENT_001"]

    for p_id in test_patient_ids:
        print(f"\n--- Running agent-based workflow for Patient ID: {p_id} ---")
        result = await run_trial_matching_workflow(p_id, use_cache=True)
        print(f"Result for {p_id} (1st run): {json.dumps(result, indent=2)}")

        print(f"\n--- Running agent-based workflow for Patient ID: {p_id} (AGAIN to test cache) ---")
        result_cached = await run_trial_matching_workflow(p_id, use_cache=True)
        print(f"Result for {p_id} (2nd run): {json.dumps(result_cached, indent=2)}")

        if p_id == "PATIENT_001":
            print(f"\n--- Running agent-based workflow for Patient ID: {p_id} (NO CACHE) ---")
            result_no_cache = await run_trial_matching_workflow(p_id, use_cache=False)
            print(f"Result for {p_id} (no cache run): {json.dumps(result_no_cache, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())