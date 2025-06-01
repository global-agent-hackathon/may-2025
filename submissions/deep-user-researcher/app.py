from dotenv import load_dotenv
load_dotenv()

import os
import uvicorn
from firecrawl import AsyncFirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

class TimelineEvent(BaseModel):
    year: int = Field(description="Year of the event")
    information: str = Field(description="Description of the event")

class Biography(BaseModel):
    bio: str = Field(description="Max 500 words biography of the user")
    citizenship: str = Field(description="Citizenship of the user")
    birth_year: str = Field(description="Birth year of the user")
    current_location: str = Field(description="Current location of the user")
    profile_picture_url: str = Field(default=None, description="URL of the user's profile picture")
    timeline: List[TimelineEvent] = Field(default_factory=list, description="Timeline of important events in the user's life")

class SocialProfile(BaseModel):
    platform: str = Field(description="Name of the social media platform")
    handle: str = Field(description="Username or handle on the platform")
    followers: int = Field(default=None, description="Number of followers")

class SocialProfiles(BaseModel):
    list: List[SocialProfile] = Field(default_factory=list, description="List of social media profiles")

class SearchRequest(BaseModel):
    full_name: str
    handle: str

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search")
async def search(request: SearchRequest):
    user = request.full_name
    common_handle = request.handle
    general_search_query = f"{user} aka {common_handle}"

    app = AsyncFirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = await app.search(
        query=f"{general_search_query} fFollowers",
        limit=5
    )
    
    d = response.get('data', [])
    f = []
    for item in d:
        url = item.get('url', '')
        title = item.get('title', '')
        description = item.get('description', '')
        formatted_item = f"{url}|{title}|{description}"
        f.append(formatted_item)
    
    social_profiles_raw_data = '\n'.join(f)

    social_profiles_agent = Agent(
        name="Social Profiles Agent",
        role="Get social profiles data",
        model=OpenAIChat(id="gpt-4o"),
        response_model=SocialProfiles,
        instructions="Get the social profiles data for the user",
    )

    social_profiles_agent_response_content = social_profiles_agent.run(social_profiles_raw_data).content
    social_profiles: List[SocialProfile] = social_profiles_agent_response_content.list

    bio_agent = Agent(
        name="Biography Agent",
        role="Get bio data",
        model=OpenAIChat(id="gpt-4o"),
        tools=[ExaTools()],
        instructions="""
        Gather more information about the user if needed and their background and:
        1. Write a short max 500 words biography for them
        2. Estimate their age
        3. Estimate their citizenship
        4. Estimate their current location
        5. Find their profile picture URL from their social profiles
        6. Create a timeline of important events in their life, including:
           - Education milestones (degrees, schools, etc.)
           - Career milestones (jobs, promotions, company changes)
           - Major achievements (awards, publications, significant projects)
           - Important life events
           Each timeline event should have:
           - A specific year (integer)
           - A clear description of the event
           Format the timeline events chronologically from earliest to latest
        """,
        show_tool_calls=True,
        response_model=Biography,
    )

    bio_agent_response_content = bio_agent.run(social_profiles_raw_data).content

    # Sort timeline events by year
    sorted_timeline = sorted(bio_agent_response_content.timeline, key=lambda x: x.year)

    return {
        "bio": bio_agent_response_content.bio,
        "citizenship": bio_agent_response_content.citizenship,
        "birth_year": bio_agent_response_content.birth_year,
        "current_location": bio_agent_response_content.current_location,
        "profile_picture_url": bio_agent_response_content.profile_picture_url,
        "timeline": [event.dict() for event in sorted_timeline],
        "social_profiles": [profile.dict() for profile in social_profiles]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    