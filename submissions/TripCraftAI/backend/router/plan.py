import asyncio
from fastapi import APIRouter, HTTPException, status
from loguru import logger
from models.travel_plan import TravelPlanAgentRequest, TravelPlanResponse
from services.plan_service import generate_travel_plan

router = APIRouter(prefix="/api/plan", tags=["Travel Plan"])

@router.post(
    "/trigger",
    response_model=TravelPlanResponse,
    summary="Trigger Trip Craft Agent",
    description="Triggers the travel plan agent with the provided travel details"
)
async def trigger_trip_craft_agent(request: TravelPlanAgentRequest) -> TravelPlanResponse:
    """
    Trigger the trip craft agent to create a personalized travel itinerary.

    Args:
        request: Travel plan request containing trip details and plan ID

    Returns:
        TravelPlanResponse: Success status and trip plan ID
    """
    try:
        logger.info(f"Triggering travel plan agent for trip ID: {request.trip_plan_id}")
        logger.info(f"Travel plan details: {request.travel_plan}")

        asyncio.create_task(generate_travel_plan(request))

        logger.info(f"Travel plan agent triggered successfully for trip ID: {request.trip_plan_id}")

        return TravelPlanResponse(
            success=True,
            message="Travel plan agent triggered successfully",
            trip_plan_id=request.trip_plan_id
        )

    except Exception as e:
        logger.error(f"Error triggering travel plan agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger travel plan agent: {str(e)}"
        )
