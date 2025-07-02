import json
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv

# Load environment variables
load_dotenv(verbose=True)
GEMINI_API_KEY = ""

# Define structured output models
class ProfileAnalysis(BaseModel):
    match_reasons: List[str] = Field(..., description="Reasons why this profile matches the search query.")
    commonalities: List[str] = Field(..., description="Common interests, experiences, or attributes shared between profiles.")
    value_propositions: List[str] = Field(..., description="Potential value or benefit of connecting with this person.")
    opening_message: str = Field(..., description="A suggested personalized opening message to send to this person.")

# Initialize Agno agent with structured output
profile_analyzer = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    instructions=[
        "You are a profile analyzer that helps users find the best connections based on their search query and profile.",
        "Analyze target profiles from the perspective of the user's background, interests, and goals.",
        "Provide match reasons, commonalities, value propositions, and a personalized opening message."
    ],
    response_model=ProfileAnalysis,
    markdown=True
)

def test_structured_output():
    print("🧪 Testing structured output with Agno and Gemini...")
    
    # Sample profiles
    user_profile = {
        "name": "Jane Doe",
        "headline": "Software Engineer looking for AI opportunities",
        "experience": "5 years in web development",
        "education": "Computer Science degree from MIT",
        "skills": "Python, JavaScript, Machine Learning"
    }
    
    target_profile = {
        "name": "John Smith",
        "headline": "AI Engineer at Tech Company",
        "experience": "Senior AI Engineer at Tech Company",
        "education": "Ph.D. in Computer Science from Stanford",
        "skills": "Machine Learning, Deep Learning, Python"
    }
    
    # Search query
    query = "AI engineers with machine learning experience"
    
    # Create the prompt
    prompt = f"""
    Based on the following information, analyze how this profile matches the user's search query: "{query}"
    
    Your profile:
    Name: {user_profile['name']}
    Headline: {user_profile['headline']}
    Experience: {user_profile['experience']}
    Education: {user_profile['education']}
    Skills: {user_profile['skills']}
    
    Target profile:
    Name: {target_profile['name']}
    Headline: {target_profile['headline']}
    Experience: {target_profile['experience']}
    Education: {target_profile['education']}
    Skills: {target_profile['skills']}
    
    Provide the following:
    1. Match reasons - Why this profile is relevant to the search query
    2. Commonalities - What the user and this profile have in common
    3. Value propositions - What value connecting with this person might bring
    4. A personalized opening message the user could send to connect
    """
    
    try:
        # Get structured analysis using Agno
        print("Running analysis with Agno...")
        analysis_result = profile_analyzer.run(prompt)
        
        # Get the structured content
        print("✅ Analysis complete!")
        print("\n🔍 STRUCTURED ANALYSIS RESULT:")
        
        # Access content from RunResponse
        analysis_dict = analysis_result.content
        
        # Print the structured data
        print("MATCH REASONS:")
        for reason in analysis_dict.match_reasons:
            print(f"  • {reason}")
        
        print("\nCOMMONALITIES:")
        for common in analysis_dict.commonalities:
            print(f"  • {common}")
        
        print("\nVALUE PROPOSITIONS:")
        for value in analysis_dict.value_propositions:
            print(f"  • {value}")
        
        print("\nOPENING MESSAGE:")
        print(analysis_dict.opening_message)
        
        # Show the JSON output
        print("\n📋 JSON OUTPUT:")
        json_output = analysis_dict.model_dump()
        print(json.dumps(json_output, indent=2))
        
        return analysis_dict
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_structured_output() 