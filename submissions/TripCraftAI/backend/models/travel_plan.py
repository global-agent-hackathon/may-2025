from pydantic import BaseModel
from typing import List

class TravelDates(BaseModel):
    start: str = ""
    end: str = ""

class TravelPlanRequest(BaseModel):
    name: str = ""
    destination: str = ""
    starting_location: str = ""
    travel_dates: TravelDates = TravelDates()
    date_input_type: str = "picker"
    duration: int = 0
    traveling_with: str = ""
    adults: int = 1
    children: int = 0
    age_groups: List[str] = []
    budget: int = 75000
    budget_currency: str = "INR"
    travel_style: str = ""
    budget_flexible: bool = False
    vibes: List[str] = []
    priorities: List[str] = []
    interests: str = ""
    rooms: int = 1
    pace: List[int] = [3]
    been_there_before: str = ""
    loved_places: str = ""
    additional_info: str = ""

class TravelPlanAgentRequest(BaseModel):
    trip_plan_id: str
    travel_plan: TravelPlanRequest

class TravelPlanResponse(BaseModel):
    success: bool
    message: str
    trip_plan_id: str