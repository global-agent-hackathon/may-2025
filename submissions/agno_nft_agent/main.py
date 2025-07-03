import os
import uvicorn
import uuid
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from masumi.config import Config
from masumi.payment import Payment, Amount
from agent_definition import run_workflow
from logging_config import setup_logging

# Configure logging
logger = setup_logging()

# Load environment variables
load_dotenv(override=True)

# Retrieve API Keys and URLs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")
NETWORK = os.getenv("NETWORK")

logger.info("Starting application with configuration:")
logger.info(f"PAYMENT_SERVICE_URL: {PAYMENT_SERVICE_URL}")

# Initialize FastAPI
app = FastAPI(
    title="API following the Masumi API Standard",
    description="API for running Agentic Services tasks with Masumi payment integration",
    version="1.0.0"
)

# ─────────────────────────────────────────────────────────────────────────────
# Temporary in-memory job store (DO NOT USE IN PRODUCTION)
# ─────────────────────────────────────────────────────────────────────────────
jobs = {}
payment_instances = {}

# ─────────────────────────────────────────────────────────────────────────────
# Initialize Masumi Payment Config
# ─────────────────────────────────────────────────────────────────────────────
config = Config(
    payment_service_url=PAYMENT_SERVICE_URL,
    payment_api_key=PAYMENT_API_KEY
)

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────────────────────────
class NFTCreationInput(BaseModel):
    prompt: str = Field(..., description="Text description for generating NFT content")
    content_type: str = Field(default="image", description="Type of content to generate (image or video)")
    wallet_address: str = Field(..., description="Cardano wallet address to receive the NFT")
    display_name: str = Field(default="Agno Test NFT", description="Display name for the NFT")
    
    @field_validator('content_type')
    def validate_content_type(cls, v):
        if v not in ["image", "video"]:
            raise ValueError('content_type must be either "image" or "video"')
        return v
    
    @field_validator('wallet_address')
    def validate_wallet_address(cls, v):
        if not v.startswith(("addr_", "addr1", "stake_", "stake1")):
            raise ValueError('wallet_address must be a valid Cardano address')
        return v

class StartJobRequest(BaseModel):
    identifier_from_purchaser: str
    input_data: dict[str, str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "identifier_from_purchaser": "example_purchaser_123",
                "input_data": {
                    "prompt": "A digital painting of a futuristic city with floating islands",
                    "content_type": "image",
                    "wallet_address": "addr_test1qz47ranxl4p5l97hwtd6793tavxqzzn6mtgmg6ztwf7356x6cluln4vc579dv335axeyk9a9fg9seql3h2d230vve5wscmmu9h",
                    "display_name": "Agno Test NFT"
                }
            }
        }

class ProvideInputRequest(BaseModel):
    job_id: str

# ─────────────────────────────────────────────────────────────────────────────
# CrewAI Task Execution
# ─────────────────────────────────────────────────────────────────────────────
async def execute_crew_task(input_data: dict) -> str:
    """ Execute a agno nft task """
    logger.info(f"Starting agno nft task with input: {input_data}")
    
    # Extract parameters from input data 
    prompt = input_data.get("prompt", "")
    content_type = input_data.get("content_type", "image")
    wallet_address = input_data.get("wallet_address", "")
    display_name = input_data.get("display_name", "Agno Test NFT")
    
    # Force these parameters to strings to avoid type mismatches
    prompt = str(prompt)
    content_type = str(content_type)
    wallet_address = str(wallet_address)
    display_name = str(display_name)
    
    # Run the workflow with the parameters
    responses = list(run_workflow(
        prompt=prompt,
        content_type=content_type,
        wallet_address=wallet_address,
        display_name=display_name
    ))
    
    # Get the final response
    final_response = responses[-1] if responses else None
    
    if final_response and final_response.content:
        logger.info(f"agno nft task completed successfully: {final_response.content[:100]}...")
        return final_response
    else:
        logger.error("No response from workflow")
        raise Exception("Failed to get response from NFT creation workflow")

# ─────────────────────────────────────────────────────────────────────────────
# 1) Start Job (MIP-003: /start_job)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/start_job")
async def start_job(data: StartJobRequest):
    """ Initiates a job and creates a payment request """
    print(f"Received data: {data}")
    print(f"Received data.input_data: {data.input_data}")
    try:
        job_id = str(uuid.uuid4())
        agent_identifier = os.getenv("AGENT_IDENTIFIER")
        
        # Extract input text, handling both old and new formats
        input_text = data.input_data.get("prompt", data.input_data.get("text", ""))
        truncated_input = input_text[:100] + "..." if len(input_text) > 100 else input_text
        logger.info(f"Received job request with input: '{truncated_input}'")
        logger.info(f"Starting job {job_id} with agent {agent_identifier}")

        # Define payment amounts
        payment_amount = os.getenv("PAYMENT_AMOUNT", "10000000")  # Default 10 ADA
        payment_unit = os.getenv("PAYMENT_UNIT", "lovelace") # Default lovelace

        amounts = [Amount(amount=payment_amount, unit=payment_unit)]
        logger.info(f"Using payment amount: {payment_amount} {payment_unit}")
        
        # Create a payment request using Masumi
        payment = Payment(
            agent_identifier=agent_identifier,
            #amounts=amounts,
            config=config,
            identifier_from_purchaser=data.identifier_from_purchaser,
            input_data=data.input_data,
            network=NETWORK
        )
        
        logger.info("Creating payment request...")
        payment_request = await payment.create_payment_request()
        payment_id = payment_request["data"]["blockchainIdentifier"]
        payment.payment_ids.add(payment_id)
        logger.info(f"Created payment request with ID: {payment_id}")

        # Store job info (Awaiting payment)
        jobs[job_id] = {
            "status": "awaiting_payment",
            "payment_status": "pending",
            "payment_id": payment_id,
            "input_data": data.input_data,
            "result": None,
            "identifier_from_purchaser": data.identifier_from_purchaser
        }

        async def payment_callback(payment_id: str):
            await handle_payment_status(job_id, payment_id)

        # Start monitoring the payment status
        payment_instances[job_id] = payment
        logger.info(f"Starting payment status monitoring for job {job_id}")
        await payment.start_status_monitoring(payment_callback)

        # Return the response in the required format
        return {
            "status": "success",
            "job_id": job_id,
            "blockchainIdentifier": payment_request["data"]["blockchainIdentifier"],
            "submitResultTime": payment_request["data"]["submitResultTime"],
            "unlockTime": payment_request["data"]["unlockTime"],
            "externalDisputeUnlockTime": payment_request["data"]["externalDisputeUnlockTime"],
            "agentIdentifier": agent_identifier,
            "sellerVkey": os.getenv("SELLER_VKEY"),
            "identifierFromPurchaser": data.identifier_from_purchaser,
            "amounts": amounts,
            "input_hash": payment.input_hash
        }
    except KeyError as e:
        logger.error(f"Missing required field in request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Bad Request: If input_data or identifier_from_purchaser is missing, invalid, or does not adhere to the schema."
        )
    except Exception as e:
        logger.error(f"Error in start_job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Input_data or identifier_from_purchaser is missing, invalid, or does not adhere to the schema."
        )

# ─────────────────────────────────────────────────────────────────────────────
# 2) Process Payment and Execute AI Task
# ─────────────────────────────────────────────────────────────────────────────
async def handle_payment_status(job_id: str, payment_id: str) -> None:
    """ Executes agno nft task after payment confirmation """
    try:
        logger.info(f"Payment {payment_id} completed for job {job_id}, executing task...")
        
        # Update job status to running
        jobs[job_id]["status"] = "running"
        logger.info(f"Input data: {jobs[job_id]['input_data']}")

        # Execute the AI task
        result = await execute_crew_task(jobs[job_id]["input_data"])
        
        # Handle the result correctly - if it's a RunResponse object
        if hasattr(result, 'content'):
            result_content = result.content
            # Try to parse as JSON if it's a string
            if isinstance(result_content, str):
                try:
                    result_dict = json.loads(result_content)
                except json.JSONDecodeError:
                    result_dict = {"result": result_content}
            else:
                result_dict = {"result": str(result_content)}
        else:
            # If result is already a dict
            result_dict = result if isinstance(result, dict) else {"result": str(result)}
            
        logger.info(f"agno nft task completed for job {job_id}")
        
        # Mark payment as completed on Masumi
        await payment_instances[job_id].complete_payment(payment_id, result_dict)
        logger.info(f"Payment completed for job {job_id}")

        # Update job status with the formatted result
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["payment_status"] = "completed"
        jobs[job_id]["result"] = result_content if hasattr(result, 'content') else str(result)

        # Stop monitoring payment status
        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]
    except Exception as e:
        logger.error(f"Error processing payment {payment_id} for job {job_id}: {str(e)}", exc_info=True)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        
        # Still stop monitoring to prevent repeated failures
        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]

# ─────────────────────────────────────────────────────────────────────────────
# 3) Check Job and Payment Status (MIP-003: /status)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/status")
async def get_status(job_id: str):
    """ Retrieves the current status of a specific job """
    logger.info(f"Checking status for job {job_id}")
    if job_id not in jobs:
        logger.warning(f"Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    # Check latest payment status if payment instance exists
    if job_id in payment_instances:
        try:
            status = await payment_instances[job_id].check_payment_status()
            job["payment_status"] = status.get("data", {}).get("status")
            logger.info(f"Updated payment status for job {job_id}: {job['payment_status']}")
        except ValueError as e:
            logger.warning(f"Error checking payment status: {str(e)}")
            job["payment_status"] = "unknown"
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}", exc_info=True)
            job["payment_status"] = "error"

    # Get the result - ensure it's properly formatted
    result_data = job.get("result")
    
    # If result_data is a RunResponse object or has a 'raw' attribute, extract the content
    if result_data:
        if hasattr(result_data, 'raw'):
            result = result_data.raw
        elif hasattr(result_data, 'content'):
            result = result_data.content
        else:
            result = result_data
    else:
        result = None

    return {
        "job_id": job_id,
        "status": job["status"],
        "payment_status": job["payment_status"],
        "result": result
    }

# ─────────────────────────────────────────────────────────────────────────────
# 4) Check Server Availability (MIP-003: /availability)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/availability")
async def check_availability():
    """ Checks if the server is operational """
    return {"status": "available", "type": "masumi-agent", "message": "The server is running smoothly."}

# ─────────────────────────────────────────────────────────────────────────────
# 5) Retrieve Input Schema (MIP-003: /input_schema)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/input_schema")
async def input_schema():
    """
    Returns the expected input schema for the /start_job endpoint.
    Fulfills MIP-003 /input_schema endpoint.
    """
    return {
        "input_data": [
            {
                "id": "prompt",
                "type": "string",
                "name": "Content Description",
                "data": {
                    "description": "Description of the content to generate for the NFT, should be detailed otherise it will be rejected",
                    "placeholder": "A digital painting of a futuristic city with floating islands"
                }
            },
            {
                "id": "content_type",
                "type": "string",
                "name": "Content Type",
                "data": {
                    "description": "Type of content to generate (image or video)",
                    "options": [
                        {"label": "Image", "value": "image"},
                        {"label": "Video", "value": "video"}
                    ],
                    "default": "image"
                }
            },
            {
                "id": "wallet_address",
                "type": "string",
                "name": "Wallet Address",
                "data": {
                    "description": "Cardano wallet address to receive the NFT, at the moment only on testnet",
                    "placeholder": "addr_test1qz..."
                }
            },
            {
                "id": "display_name",
                "type": "string",
                "name": "NFT Display Name",
                "data": {
                    "description": "Display name for the NFT",
                    "placeholder": "Agno Test NFT",
                    "default": "Agno Test NFT"
                }
            }
        ]
    }

# ─────────────────────────────────────────────────────────────────────────────
# 6) Health Check
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """
    Returns the health of the server.
    """
    return {
        "status": "healthy"
    }

# ─────────────────────────────────────────────────────────────────────────────
# Main Logic if Called as a Script
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("Running CrewAI as standalone script is not supported when using payments.")
    print("Start the API using `python main.py api` instead.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        print("Starting FastAPI server with Masumi integration...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        main()