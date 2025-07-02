from linkedin_api import Linkedin
import os
import json
import requests
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from typing import List, Optional
from pydantic import BaseModel, Field
import time
import random

password = ""
username = ""

# Initialize LinkedIn API with error handling
try:
    api = Linkedin(username, password)
    LINKEDIN_AVAILABLE = True
except Exception as e:
    print("⚠️ LinkedIn API initialization failed. LinkedIn features will be disabled.")
    print(f"Error: {str(e)}")
    LINKEDIN_AVAILABLE = False
    api = None


GEMINI_API_KEY = ""

# Define structured output models
class ProfileAnalysis(BaseModel):
    match_reasons: List[str] = Field(..., description="Reasons why this profile matches the search query.")
    commonalities: List[str] = Field(..., description="Common interests, experiences, or attributes shared between profiles.")
    value_propositions: List[str] = Field(..., description="Potential value or benefit of connecting with this person.")
    opening_message: str = Field(..., description="A suggested personalized opening message to send to this person.")

class LinkedInProfile(BaseModel):
    name: str = Field(..., description="Full name of the LinkedIn user.")
    headline: str = Field("", description="Professional headline or tagline.")
    avatar: str = Field("", description="URL to the profile image.")
    platform: str = Field("LinkedIn", description="Social media platform.")
    profile_url: str = Field("", description="URL to the LinkedIn profile.")
    
class AnalyzedProfile(BaseModel):
    profile: LinkedInProfile
    analysis: ProfileAnalysis

# Initialize Agno agent for profile analysis
profile_analyzer = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    instructions=[
        "You are a LinkedIn profile analyzer that helps extract and present key information from profiles.",
        "Analyze profiles to identify key skills, experiences, and potential networking opportunities."
    ],
    response_model=ProfileAnalysis,
    markdown=True
)

def extract_linkedin_id(url):
    """
    Extract LinkedIn ID from a URL if it's a valid LinkedIn profile URL.
    Returns the ID if valid, None otherwise.
    """
    if "linkedin.com/in/" in url:
        # Extract the part after "/in/" and remove any trailing slashes
        linkedin_id = url.split("/in/")[1].split("/")[0].strip()
        return linkedin_id
    return None

def get_linkedin_profile(linkedin_id):
    if not LINKEDIN_AVAILABLE:
        raise Exception("LinkedIn integration is not available. Please check your LinkedIn credentials.")
        
    max_retries = 3
    base_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            print(f"\n🔍 Retrieving profile for: {linkedin_id} (Attempt {attempt + 1}/{max_retries})")
            profile = api.get_profile(linkedin_id)
            
            # Check if we got an empty profile
            if not profile or not profile.get('firstName'):
                raise Exception("This profile can't be accessed")
            
            # Basic profile info with emojis
            print("\n✨ PROFILE OVERVIEW ✨")
            print(f"👤 Name: {profile.get('firstName', '')} {profile.get('lastName', '')}")
            print(f"📌 Headline: {profile.get('headline', 'N/A')}")
            print(f"🏢 Industry: {profile.get('industryName', 'N/A')}")
            print(f"📍 Location: {profile.get('locationName', 'N/A')}")
            
            # Education
            if profile.get('education'):
                print("\n🎓 EDUCATION 🎓")
                for edu in profile.get('education', []):
                    school = edu.get('schoolName', 'Unknown School')
                    degree = edu.get('degreeName', '')
                    field = edu.get('fieldOfStudy', '')
                    date_range = f"{edu.get('timePeriod', {}).get('startDate', {}).get('year', '')} - {edu.get('timePeriod', {}).get('endDate', {}).get('year', 'Present')}"
                    print(f"  • {school}: {degree} {field} ({date_range})")
            
            # Experience
            if profile.get('experience'):
                print("\n💼 EXPERIENCE 💼")
                for exp in profile.get('experience', []):
                    company = exp.get('companyName', 'Unknown Company')
                    title = exp.get('title', 'Unknown Title')
                    location = exp.get('locationName', '')
                    start_year = exp.get('timePeriod', {}).get('startDate', {}).get('year', '')
                    start_month = exp.get('timePeriod', {}).get('startDate', {}).get('month', '')
                    end_year = exp.get('timePeriod', {}).get('endDate', {}).get('year', 'Present')
                    end_month = exp.get('timePeriod', {}).get('endDate', {}).get('month', '')
                    
                    date_range = f"{start_month}/{start_year} - {end_month}/{end_year}" if start_month and end_month else f"{start_year} - {end_year}"
                    print(f"  • {title} at {company} ({date_range})")
                    if exp.get('description'):
                        print(f"    📝 {exp.get('description', '')[:100]}...")
            
            # Get contact info
            try:
                contact_info = api.get_profile_contact_info(linkedin_id)
                print("\n📞 CONTACT INFO 📞")
                if contact_info.get('email_address'):
                    print(f"📧 Email: {contact_info.get('email_address')}")
                if contact_info.get('websites'):
                    print("🌐 Websites:")
                    for site in contact_info.get('websites', []):
                        print(f"  • {site.get('url')}")
                if contact_info.get('phone_numbers'):
                    print("☎️ Phone:")
                    for phone in contact_info.get('phone_numbers', []):
                        print(f"  • {phone.get('number')}")
            except Exception as e:
                print(f"⚠️ Error getting contact info: {e}")
            
            # Get skills
            try:
                skills_data = api.get_profile_skills(linkedin_id)
                if skills_data:
                    print("\n🚀 SKILLS 🚀")
                    for skill in skills_data:
                        print(f"  • {skill.get('name', 'Unknown Skill')}")
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                    print(f"⚠️ Rate limit hit for skills. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                print(f"⚠️ Error getting skills: {e}")
            
            # Get network info
            try:
                network = api.get_profile_network_info(linkedin_id)
                print("\n🔗 NETWORK INFO 🔗")
                print(f"👥 Connections: {network.get('totalConnectionCount', 'N/A')}")
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                    print(f"⚠️ Rate limit hit for network info. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                print(f"⚠️ Error getting network info: {e}")
            
            # Use Agno agent with structured output to provide analysis
            try:
                # Construct a more detailed prompt with profile data
                insights_prompt = f"""
                Analyze this LinkedIn profile and provide insights on networking value:
                
                Name: {profile.get('firstName', '')} {profile.get('lastName', '')}
                Headline: {profile.get('headline', 'N/A')}
                Industry: {profile.get('industryName', 'N/A')}
                Location: {profile.get('locationName', 'N/A')}
                
                Education:
                {', '.join([edu.get('schoolName', '') for edu in profile.get('education', [])])}
                
                Experience:
                {', '.join([f"{exp.get('title', '')} at {exp.get('companyName', '')}" for exp in profile.get('experience', [])])}
                
                Skills:
                {', '.join([skill.get('name', '') for skill in skills_data])}
                
                Focus on identifying networking opportunities, common interests, and effective ways to connect.
                """
                
                # Get structured analysis response
                analysis_result = profile_analyzer.run(insights_prompt)
                
                # Access the content from the RunResponse object
                # Convert the content to our ProfileAnalysis model
                analysis_dict = analysis_result.content
                
                # Print the structured output
                print("\n🔍 AI STRUCTURED ANALYSIS 🔍")
                print(f"Match Reasons: {analysis_dict.match_reasons}")
                print(f"Commonalities: {analysis_dict.commonalities}")
                print(f"Value Propositions: {analysis_dict.value_propositions}")
                print(f"Opening Message: {analysis_dict.opening_message}")
                
                # Convert to dict/JSON for API use
                analysis_json = analysis_dict.model_dump()
                print("\n📋 JSON OUTPUT:")
                print(json.dumps(analysis_json, indent=2))
                
                # Create the structured profile output
                linkedin_profile = LinkedInProfile(
                    name=f"{profile.get('firstName', '')} {profile.get('lastName', '')}",
                    headline=profile.get('headline', ''),
                    profile_url=f"https://www.linkedin.com/in/{linkedin_id}/",
                    # You would need to handle the avatar URL properly here
                    avatar=""
                )
                
                # Create the complete analyzed profile
                analyzed_profile = AnalyzedProfile(
                    profile=linkedin_profile,
                    analysis=analysis_dict
                )
                
                # Print the complete structured output
                print("\n🔍 COMPLETE STRUCTURED PROFILE 🔍")
                print(json.dumps(analyzed_profile.model_dump(), indent=2))
                
            except Exception as e:
                print(f"⚠️ Error generating AI structured analysis: {e}")
                import traceback
                traceback.print_exc()
                
                # Create a fallback analysis
                print("\n🔄 Creating fallback analysis...")
                
                # Extract basic info for fallback analysis
                education = [edu.get('schoolName', '') for edu in profile.get('education', [])]
                experience = [f"{exp.get('title', '')} at {exp.get('companyName', '')}" for exp in profile.get('experience', [])]
                skills_list = [skill.get('name', '') for skill in skills_data if skills_data]
                
                # Create fallback analysis
                fallback_analysis = ProfileAnalysis(
                    match_reasons=[
                        f"Works in {profile.get('industryName', 'relevant industry')}",
                        f"Based in {profile.get('locationName', 'your area')}",
                        f"Has experience in {', '.join(skills_list[:3]) if skills_list else 'relevant areas'}"
                    ],
                    commonalities=[
                        f"Education background that may align with yours",
                        f"Professional experience in {profile.get('industryName', 'relevant field')}",
                        f"Potential shared interests in {', '.join(skills_list[:2]) if skills_list else 'professional development'}"
                    ],
                    value_propositions=[
                        f"Experience in {', '.join(experience[:2]) if experience else 'areas of interest'}",
                        f"Knowledge in {', '.join(skills_list[:3]) if skills_list else 'relevant skills'}",
                        "Potential for mutually beneficial professional connection"
                    ],
                    opening_message=f"Hi {profile.get('firstName', '')}, I came across your profile and was impressed by your experience in {profile.get('headline', 'your field')}. I'd love to connect and learn more about your work."
                )
                
                # Create the structured profile output with fallback analysis
                linkedin_profile = LinkedInProfile(
                    name=f"{profile.get('firstName', '')} {profile.get('lastName', '')}",
                    headline=profile.get('headline', ''),
                    profile_url=f"https://www.linkedin.com/in/{linkedin_id}/",
                    avatar=""
                )
                
                # Create the complete analyzed profile with fallback
                analyzed_profile = AnalyzedProfile(
                    profile=linkedin_profile,
                    analysis=fallback_analysis
                )
                
                # Print the complete fallback structured output
                print("\n🔍 FALLBACK STRUCTURED PROFILE 🔍")
                print(json.dumps(analyzed_profile.model_dump(), indent=2))
            
            print("\n✅ Profile data retrieved successfully!")
            return profile
            
        except Exception as e:
            error_message = str(e)
            if "429" in error_message and attempt < max_retries - 1:
                delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                print(f"⚠️ Rate limit hit. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            elif "This profile can't be accessed" in error_message or "request failed" in error_message:
                raise Exception("This profile can't be accessed")
            else:
                # If it's the last attempt or a different error, raise it
                if attempt == max_retries -1:
                    print(f"❌ Max retries reached for {linkedin_id}. Error: {error_message}")
                raise Exception(f"Error retrieving profile: {error_message}")
    
    # This part is reached if all retries fail for the initial profile fetch
    raise Exception(f"Failed to retrieve profile for {linkedin_id} after {max_retries} attempts.")

# Function to create a sample profile for testing without LinkedIn API
def create_sample_profile():
    try:
        # Create a sample profile with the expected structure
        sample_profile = LinkedInProfile(
            name="Jane Doe",
            headline="Software Engineer at Tech Company",
            avatar="https://example.com/avatar.png",
            platform="LinkedIn",
            profile_url="https://linkedin.com/in/janedoe"
        )
        
        # Create sample analysis
        sample_analysis = ProfileAnalysis(
            match_reasons=[
                "Has 5+ years of experience in software development",
                "Worked in the same industry as you", 
                "Located in your area"
            ],
            commonalities=[
                "Both attended Stanford University",
                "Both have experience with React and Node.js",
                "Both interested in AI/ML technologies"
            ],
            value_propositions=[
                "Could provide insights on transitioning to senior engineering roles",
                "Has connections at companies you're interested in",
                "Experience with technologies you want to learn"
            ],
            opening_message="Hi Jane, I noticed we both attended Stanford and share an interest in AI technologies. I'd love to connect and hear about your experience at Tech Company as I'm exploring similar opportunities."
        )
        
        # Create the complete analyzed profile
        analyzed_profile = AnalyzedProfile(
            profile=sample_profile,
            analysis=sample_analysis
        )
        
        # Print the complete structured output
        print("\n🔍 SAMPLE STRUCTURED PROFILE 🔍")
        print(json.dumps(analyzed_profile.model_dump(), indent=2))
        
        return analyzed_profile.model_dump()
        
    except Exception as e:
        print(f"⚠️ Error creating sample profile: {e}")
        return None

# Run the sample profile function if this file is executed directly
if __name__ == "__main__":
    print("Creating a sample profile for testing...")
    sample_data = create_sample_profile()
    if sample_data:
        print("Sample profile created successfully!")
    else:
        print("Failed to create sample profile.")