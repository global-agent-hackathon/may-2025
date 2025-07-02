import os
import json
import requests
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.perplexity import Perplexity
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import time

# Load environment variables
load_dotenv(dotenv_path="./env", verbose=True)

# Initialize API keys
PERPLEXITY_API_KEY = ""
GEMINI_API_KEY = ""
if not PERPLEXITY_API_KEY or not GEMINI_API_KEY:
    raise ValueError("API keys not set in environment variables")

# Define structured output model
class SourceInfo(BaseModel):
    url: str = Field(..., description="The source URL or publication name")
    date: str = Field(..., description="When the information was published or last updated")
    reliability: str = Field(..., description="Why this source is reliable and relevant")

class ContentSection(BaseModel):
    title: str = Field(..., description="Title of this content section")
    information: str = Field(..., description="Detailed information about this aspect of the person")
    sources: List[SourceInfo] = Field(..., description="List of sources supporting this information")

class CombinedAnalysis(BaseModel):
    professional_background: ContentSection = Field(..., description="Professional history and current role")
    achievements: ContentSection = Field(..., description="Notable achievements and contributions")
    expertise: ContentSection = Field(..., description="Areas of expertise and skills")

# Initialize Perplexity Agent
perplexity_agent = Agent(
    name="Perplexity Profile Searcher",
    model=Perplexity(id="sonar", api_key=PERPLEXITY_API_KEY),
    instructions=[
        "You are an expert research assistant specializing in deep profile analysis. Your goal is to find EVERY SINGLE PIECE of information about the person.",
        "Search and analyze the person's ENTIRE professional and personal history. Leave no stone unturned.",
        "For each piece of information, you MUST include:",
        "1. The EXACT source URL or publication name",
        "2. The PRECISE date of the information",
        "3. A DETAILED explanation of why this source is reliable",
        "4. Any CONTEXT that makes this information significant",
        "Focus on finding:",
        "- Every role they've ever held",
        "- All educational qualifications",
        "- Every major project or initiative",
        "- All significant achievements and milestones",
        "- Every company they've worked with",
        "- All notable partnerships or collaborations",
        "- Any patents, publications, or intellectual contributions",
        "- All public speaking engagements or interviews",
        "- Any awards or recognitions",
        "- All significant investments or business decisions",
        "If you find ANY information, no matter how small, include it. The more detailed and comprehensive, the better.",
        "If information is uncertain or outdated, explain why and provide alternative sources if available."
    ],
    markdown=True
)

# Initialize OpenAI Agent
openai_agent = Agent(
    name="OpenAI Person Analyzer",
    role="Analyze people using OpenAI",
    model=OpenAIChat(id="gpt-4o-search-preview-2025-03-11"),
    instructions="""
    You are an expert at finding and analyzing EVERY DETAIL about a person. Your goal is to provide the MOST COMPREHENSIVE analysis possible.

    Search and analyze EVERY aspect of the person's life and career, including:
    1. Professional Background:
       - Complete work history with dates
       - Every role and position held
       - All companies and organizations
       - Every major project led or contributed to
       - All team sizes managed
       - Every department or division worked in

    2. Education and Training:
       - All degrees and certifications
       - Every educational institution attended
       - All specialized training programs
       - Every academic achievement
       - All relevant coursework
       - Every scholarship or award received

    3. Skills and Expertise:
       - Every technical skill
       - All programming languages known
       - Every tool or technology mastered
       - All methodologies practiced
       - Every domain expertise
       - All soft skills demonstrated

    4. Achievements and Impact:
       - Every major accomplishment
       - All patents filed
       - Every publication authored
       - All awards received
       - Every significant project completed
       - All revenue or growth metrics achieved

    5. Company Information:
       - Every company founded
       - All board positions held
       - Every startup invested in
       - All partnerships formed
       - Every acquisition made
       - All market impact created

    6. Public Presence:
       - Every public speaking engagement
       - All interviews given
       - Every article written
       - All social media presence
       - Every media appearance
       - All community involvement

    For EACH piece of information:
    - Provide the EXACT source
    - Include the PRECISE date
    - Explain why the source is reliable
    - Add any relevant context
    - Note if information is uncertain

    The more detailed and comprehensive your analysis, the better. Leave no detail unmentioned.
    """,
    add_datetime_to_instructions=True
)

# Initialize Gemini Agent for combining results
gemini_agent = Agent(
    name="Gemini Analysis Combiner",
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    instructions=[
        "You are an expert at combining and synthesizing information from multiple sources. Your goal is to create the MOST COMPREHENSIVE profile possible.",
        "Given outputs from two different AI agents about a person, combine their insights into a structured format that captures EVERY detail.",
        "For each content section:",
        "1. Extract and combine ALL relevant information from both sources",
        "2. Include EVERY source that provides information, no matter how small",
        "3. Ensure ALL information is properly attributed to its sources",
        "4. Maintain a professional and objective tone",
        "5. Focus on providing MAXIMUM detail in each section",
        "6. Cross-reference information between sources to verify accuracy",
        "7. Include any additional insights or connections you can make",
        "8. Highlight any unique or particularly significant details",
        "9. Note any discrepancies between sources and explain them",
        "10. Add any relevant context that helps understand the information better",
        "Your goal is to create the most detailed and comprehensive profile possible, leaving no information unmentioned."
    ],
    response_model=CombinedAnalysis,
    markdown=True
)

# Example usage
# person_info = "Satya Nadella, CEO of Microsoft"

# # Get analysis from both agents
# print("\n=== OpenAI Agent Analysis ===\n")
# openai_result = openai_agent.run(
#     f"Analyze this person: {person_info}")

# print("\n=== Perplexity Agent Analysis ===\n")
# perplexity_result = perplexity_agent.run(
#     f"Analyze this person: {person_info}")

# # Combine the results using Gemini
# print("\n=== Combined Analysis (Gemini) ===\n")
# combined_prompt = f"""
# Please analyze and combine the following information about {person_info}:

# Analysis 1:
# {openai_result}

# Analysis 2:
# {perplexity_result}

# Combine these insights into a structured format with three sections please. 
# For each section, include multiple sources and detailed information. MAKE SURE TO PROVIDE AS MUCH INFORMATION AS POSSIBLE.
# """

# gemini_result = gemini_agent.run(combined_prompt)

# print(gemini_result)

# Flask app setup
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to expand profile - Used by the api.py file
def expand_profile(profile_id, profile_data):
    """
    Expands a user profile to gather more detailed information by querying the agents.
    
    Args:
        profile_id (str): Unique identifier for the profile
        profile_data (dict): Profile data including name and other information
        
    Returns:
        dict: Dictionary with expanded profile information including nodes
    """
    try:
        # Extract name or use profile ID if name not available
        person_name = profile_data.get('name', profile_id)
        
        # Format query with specific profile
        profile_query = f"{person_name}"
        if 'headline' in profile_data and profile_data['headline']:
            profile_query += f", {profile_data['headline']}"
            
        # Run analysis with specific profile
        openai_result = openai_agent.run(f"Analyze this person: {profile_query}")
        perplexity_result = perplexity_agent.run(f"Analyze this person: {profile_query}")
        
        # Combine results
        combined_prompt = f"""
        Please analyze and combine the following information about {profile_query}:

        Analysis 1:
        {openai_result}

        Analysis 2:
        {perplexity_result}

        Combine these insights into a structured format with three sections please.
        For each section, include multiple sources and detailed information. MAKE SURE TO PROVIDE AS MUCH INFORMATION AS POSSIBLE.
        """
        
        result = gemini_agent.run(combined_prompt)
        
        # Convert result to JSON-friendly format
        if hasattr(result, 'content') and hasattr(result.content, 'dict'):
            analysis_data = result.content.dict()
        else:
            # If not a structured object, create a simple structure
            analysis_data = {
                "professional_background": {"title": "Professional Background", "information": "Information not available", "sources": []},
                "achievements": {"title": "Achievements", "information": "Information not available", "sources": []},
                "expertise": {"title": "Expertise", "information": "Information not available", "sources": []}
            }
        
        # Create nodes from the analysis sections
        nodes = []
        
        # Add professional background as nodes
        if 'professional_background' in analysis_data:
            bg = analysis_data['professional_background']
            nodes.append({
                "id": f"{profile_id}_background",
                "text": bg.get('information', 'No professional background information available'),
                "source": "Professional Background"
            })
            
        # Add achievements as nodes
        if 'achievements' in analysis_data:
            achievements = analysis_data['achievements']
            nodes.append({
                "id": f"{profile_id}_achievements",
                "text": achievements.get('information', 'No achievement information available'),
                "source": "Achievement"
            })
            
        # Add expertise as nodes
        if 'expertise' in analysis_data:
            expertise = analysis_data['expertise']
            nodes.append({
                "id": f"{profile_id}_expertise",
                "text": expertise.get('information', 'No expertise information available'),
                "source": "Expertise"
            })
        
        # Return structured result
        return {
            "success": True,
            "profileId": profile_id,
            "nodes": nodes
        }
    
    except Exception as e:
        print(f"Error expanding profile: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "nodes": []
        }

