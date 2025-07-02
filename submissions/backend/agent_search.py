from googlesearch import search
from linkedin_api import Linkedin
import os
from dotenv import load_dotenv
import json
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import tweepy
from agno.agent import Agent
from agno.models.google import Gemini
from google import genai
  

# Initialize LinkedIn API
password = ''
username = ''
api = None  # Initialize api to None
LINKEDIN_AVAILABLE_AGENT_SEARCH = False  # Flag to indicate LinkedIn API availability
try:
    api = Linkedin(username, password)
    LINKEDIN_AVAILABLE_AGENT_SEARCH = True
    print("✅ LinkedIn API initialized successfully in agent_search.")
except Exception as e:
    print("⚠️ LinkedIn API initialization failed in agent_search. LinkedIn features in this module might be affected.")
    print(f"Error: {str(e)}")
    # api remains None and LINKEDIN_AVAILABLE_AGENT_SEARCH remains False

# Initialize Gemini API
GEMINI_API_KEY = ""
GOOGLE_API_KEY = ""

# Initialize Twitter API
BEARER_TOKEN = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

# Initialize Twitter client
twitter_client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Define structured output models to match linkedin_info.py
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

def extract_useful_profile_info(profile):
    """
    Extract useful information from a LinkedIn profile.
    Returns a dictionary with the most relevant information.
    """
    if not profile:
        return None
        
    useful_info = {
        "name": f"{profile.get('firstName', '')} {profile.get('lastName', '')}",
        "headline": profile.get('headline', ''),
        "summary": profile.get('summary', ''),
        "location": profile.get('locationName', ''),
        "profile_url": f"https://www.linkedin.com/in/{profile.get('public_id', '')}",
        "platform": "LinkedIn",
        "education": [],
        "experience": [],
        "projects": []
    }
    
    # Extract education
    for edu in profile.get('education', []):
        education = {
            "school": edu.get('schoolName', ''),
            "degree": edu.get('degreeName', ''),
            "field_of_study": edu.get('fieldOfStudy', ''),
            "time_period": edu.get('timePeriod', {}),
            "description": edu.get('description', '')
        }
        useful_info["education"].append(education)
    
    # Extract experience
    for exp in profile.get('experience', []):
        experience = {
            "title": exp.get('title', ''),
            "company": exp.get('companyName', ''),
            "time_period": exp.get('timePeriod', {}),
            "description": exp.get('description', ''),
            "location": exp.get('locationName', '')
        }
        useful_info["experience"].append(experience)
    
    # Extract projects
    for proj in profile.get('projects', []):
        project = {
            "title": proj.get('title', ''),
            "description": proj.get('description', ''),
            "time_period": proj.get('timePeriod', {})
        }
        useful_info["projects"].append(project)
    
    # Remove empty lists
    useful_info = {k: v for k, v in useful_info.items() if v != []}
    
    return useful_info

def extract_twitter_profile_info(url):
    """
    Extract useful information from a Twitter/X profile URL using the Twitter API.
    Returns a dictionary with the most relevant information.
    """
    try:
        # Extract username from URL
        if url.startswith("https://x.com/"):
            username = url.split("https://x.com/")[1].split("/")[0].strip()
        else:
            username = url.split("https://twitter.com/")[1].split("/")[0].strip()
        
        # Get profile info using Twitter API
        profile_info = get_twitter_profile(username)
        if not profile_info:
            # Fallback to basic info if API call fails
            profile_info = {
                "name": username,
                "profile_url": url,
                "platform": "Twitter/X"
            }
        
        return profile_info
    except Exception as e:
        print(f"Error extracting Twitter profile info: {str(e)}")
        return None

def extract_instagram_profile_info(url):
    """
    Extract useful information from an Instagram profile URL.
    Returns a dictionary with name, bio, and URL.
    
    Args:
        url (str): Instagram profile URL
        
    Returns:
        dict: Dictionary containing name, bio, and URL or None if extraction fails
    """
    try:
        # Extract username from URL
        if not url.startswith("https://www.instagram.com/"):
            print("Invalid Instagram URL format")
            return None
            
        username = url.split("https://www.instagram.com/")[1].split("/")[0].strip()
        if not username:
            print("Could not extract username from URL")
            return None
        
        # Create profile info structure with default values
        profile_info = {
            "name": username,
            "profile_url": url,
            "bio": "",
            "platform": "Instagram"
        }
        
        try:
            import instaloader
            L = instaloader.Instaloader()
            profile = instaloader.Profile.from_username(L.context, username)
            profile_info["bio"] = profile.biography or ""
            
        except Exception as e:
            print(f"Error getting Instagram profile data: {str(e)}")
        
        return profile_info
        
    except Exception as e:
        print(f"Error extracting Instagram profile info: {str(e)}")
        return None

def search_social_media(query, max_iterations=30, max_profiles=8):
    """
    Search for social media profiles based on a query.
    
    Args:
        query (str): Search query
        max_iterations (int): Maximum number of search results to process
        min_profiles (int): Minimum number of profiles to collect
        
    Returns:
        List[Dict]: List of extracted profile information
    """
    domain_list = ["linkedin profile", "twitter/X profile", "instagram profile"]
    profiles = []
    max_linkedin_profiles = 6
    max_twitter_profiles = 3
    
    for domain in domain_list:
        if domain == "linkedin profile":
            query_domain = query
        elif domain == "twitter/X profile":
            query_domain = query.replace("site:linkedin.com/in", " site:x.com")
        elif domain == "instagram profile":
            query_domain = query.replace("site:linkedin.com/in", " site:instagram.com")
        for index, url in enumerate(search(query_domain)):
            if index >= max_iterations or len(profiles) >= max_profiles:
                break
            if domain == "linkedin profile":
                if "/in/" in url:
                    if not LINKEDIN_AVAILABLE_AGENT_SEARCH:
                        print("LinkedIn API not available in agent_search, skipping LinkedIn profile.")
                        continue
                    try:
                        linkedin_id = url.split("/in/")[1].split("/")[0].strip()
                        print(f"\n🔍 Retrieving profile for: {linkedin_id}")
                        profile = api.get_profile(linkedin_id)
                        if profile:
                            useful_info = extract_useful_profile_info(profile)
                            if useful_info:
                                profiles.append(useful_info)
                    except Exception as e:
                        print(f"Error retrieving profile for {linkedin_id}: {str(e)}")
                        continue
                    if len(profiles) >= max_linkedin_profiles:
                        break
            elif domain == "twitter/X profile":
                # Only process URLs that are direct profile URLs (no status/post URLs)
                if (url.startswith("https://x.com/") or url.startswith("https://twitter.com/")) and "/status/" not in url:
                    # Extract username and check if it's a profile URL
                    if not any(url.endswith(f"/{suffix}") for suffix in ["/media", "/with_replies", "/likes"]):
                        print(f"\n🔍 Found Twitter/X profile: {url}")
                        profile_info = extract_twitter_profile_info(url)
                        if profile_info:
                            profiles.append(profile_info)
                        if len(profiles) >= max_twitter_profiles:
                            break
            elif domain == "instagram profile":
                if url.startswith("https://www.instagram.com/"):
                    print(f"\n🔍 Found Instagram profile: {url}")
                    profile_info = extract_instagram_profile_info(url)
                    if profile_info:
                        profiles.append(profile_info)
            
    return profiles

def analyze_profile(profiles: List[Dict], query: str, my_profile: Dict) -> List[Dict]:
    """
    Analyzes social media profiles using Gemini to find matches with the query and user's profile.
    
    Args:
        profiles (List[Dict]): List of social media profiles to analyze
        query (str): Original search query
        my_profile (Dict): User's own LinkedIn profile
        
    Returns:
        List[Dict]: List of analyzed profiles with recommendations
    """
    # Initialize Agno agent with Gemini model and structured output
    agent = Agent(
        model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
        instructions=[
            "You are a profile analyzer that helps users find the best connections based on their search query and profile.",
            "Analyze target profiles from the perspective of the user's background, interests, and goals.",
            "Provide match reasons, commonalities, value propositions, and a personalized opening message."
        ],
        response_model=ProfileAnalysis,
        markdown=True
    )
    
    analyzed_profiles = []
    
    for profile in profiles:
        try:
            print(f"\n🔍 Analyzing profile: {profile.get('name', 'Unknown')}")
            
            # Create a summary of the user's profile
            user_summary = "Your profile:\n"
            if my_profile:
                user_summary += f"Name: {my_profile.get('name', 'Not provided')}\n"
                user_summary += f"Headline: {my_profile.get('headline', 'Not provided')}\n"
                user_summary += f"Experience: {my_profile.get('experience', 'Not provided')}\n"
                user_summary += f"Education: {my_profile.get('education', 'Not provided')}\n"
                user_summary += f"Skills: {my_profile.get('skills', 'Not provided')}\n"
            else:
                user_summary += "No profile information provided.\n"
            
            # Create a summary of the target profile
            target_summary = "Target profile:\n"
            target_summary += f"Name: {profile.get('name', 'Not provided')}\n"
            target_summary += f"Headline: {profile.get('headline', 'Not provided')}\n"
            
            if 'experience' in profile and isinstance(profile['experience'], list) and profile['experience']:
                target_summary += "Experience:\n"
                for exp in profile['experience'][:3]:  # Limit to first 3 experiences
                    if isinstance(exp, dict):
                        target_summary += f"- {exp.get('title', '')} at {exp.get('company', '')}\n"
                    else:
                        target_summary += f"- {exp}\n"
            
            if 'education' in profile and isinstance(profile['education'], list) and profile['education']:
                target_summary += "Education:\n"
                for edu in profile['education'][:2]:  # Limit to first 2 educations
                    if isinstance(edu, dict):
                        target_summary += f"- {edu.get('school', '')} - {edu.get('degree', '')} {edu.get('field_of_study', '')}\n"
                    else:
                        target_summary += f"- {edu}\n"
            
            # Use the default avatar placeholder for this platform
            platform = profile.get('platform', 'LinkedIn')
            avatar_placeholder = {
                'LinkedIn': "https://cdn-icons-png.flaticon.com/512/174/174857.png",
                'Twitter/X': "https://cdn-icons-png.flaticon.com/512/124/124021.png",
                'Instagram': "https://cdn-icons-png.flaticon.com/512/174/174855.png"
            }.get(platform, "")
            
            # Create the prompt for Gemini
            prompt = f"""
            Based on the following information, analyze how this profile matches the user's search query: "{query}"
            
            {user_summary}
            
            {target_summary}
            
            Provide the following:
            1. Match reasons - Why this profile is relevant to the search query
            2. Commonalities - What the user and this profile have in common
            3. Value propositions - What value connecting with this person might bring
            4. A personalized opening message the user could send to connect
            """
            
            # Get structured analysis using Agno
            print("Running analysis with Agno...")
            analysis_result = agent.run(prompt)
            
            # Get the structured content
            analysis_dict = analysis_result.content
            
            # Create the structured profile
            linkedin_profile = LinkedInProfile(
                name=profile.get('name', 'Unknown User'),
                headline=profile.get('headline', ''),
                avatar=profile.get('avatar', avatar_placeholder),
                platform=profile.get('platform', 'LinkedIn'),
                profile_url=profile.get('profile_url', '')
            )
            
            # Create the full analyzed profile
            analyzed_profile = AnalyzedProfile(
                profile=linkedin_profile,
                analysis=analysis_dict
            )
            
            # Convert to dict for API response
            analyzed_profiles.append(analyzed_profile.model_dump())
            print(f"✅ Analysis complete for {profile.get('name', 'Unknown')}")
            
        except Exception as e:
            print(f"⚠️ Error analyzing profile {profile.get('name', 'Unknown')}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Create fallback analysis
            try:
                print(f"🔄 Creating fallback analysis for {profile.get('name', 'Unknown')}")
                
                # Use default avatar placeholder for this platform
                platform = profile.get('platform', 'LinkedIn')
                avatar_placeholder = {
                    'LinkedIn': "https://cdn-icons-png.flaticon.com/512/174/174857.png",
                    'Twitter/X': "https://cdn-icons-png.flaticon.com/512/124/124021.png",
                    'Instagram': "https://cdn-icons-png.flaticon.com/512/174/174855.png"
                }.get(platform, "")
                
                # Create fallback analysis
                fallback_analysis = ProfileAnalysis(
                    match_reasons=[
                        f"Matches your search for '{query}'",
                        f"Works in a relevant industry",
                        f"May have experience relevant to your interests"
                    ],
                    commonalities=[
                        "Potential professional overlap",
                        "May share similar industry experience",
                        "Could have aligned career interests"
                    ],
                    value_propositions=[
                        "Potential professional connection",
                        "Might provide industry insights",
                        "Could offer networking opportunities"
                    ],
                    opening_message=f"Hi {profile.get('name', '').split()[0] if profile.get('name') else ''}, I came across your profile during my search for {query} and I'd like to connect to learn more about your experience in this area."
                )
                
                # Create the structured profile
                linkedin_profile = LinkedInProfile(
                    name=profile.get('name', 'Unknown User'),
                    headline=profile.get('headline', ''),
                    avatar=profile.get('avatar', avatar_placeholder),
                    platform=profile.get('platform', 'LinkedIn'),
                    profile_url=profile.get('profile_url', '')
                )
                
                # Create the full analyzed profile
                analyzed_profile = AnalyzedProfile(
                    profile=linkedin_profile,
                    analysis=fallback_analysis
                )
                
                # Add to results
                analyzed_profiles.append(analyzed_profile.model_dump())
                print(f"✅ Fallback analysis complete for {profile.get('name', 'Unknown')}")
                
            except Exception as fallback_error:
                print(f"⚠️ Fatal error creating fallback for {profile.get('name', 'Unknown')}: {str(fallback_error)}")
                # Skip this profile
                continue
    
    return analyzed_profiles

def get_twitter_profile(username: str) -> Dict:
    """
    Fetch a Twitter profile using the Twitter API v2.
    
    Args:
        username (str): Twitter username without @ symbol
        
    Returns:
        Dict: Dictionary containing profile information
    """
    try:
        # Get user by username
        user = twitter_client.get_user(username=username, user_fields=['description'])
        
        if not user.data:
            return None
            
        profile_info = {
            "name": user.data.name,
            "bio": user.data.description,
            "platform": "Twitter/X"
        }
        
        return profile_info
        
    except Exception as e:
        print(f"Error fetching Twitter profile: {str(e)}")
        return None

def format_search_query(query: str) -> str:
    """
    Uses Gemini to turn a natural‐language requirement into a single,
    optimized Google search string that:
      1. always begins with `site:linkedin.com/in`
      2. uses exact‐phrase quotes for multi‐word terms
      3. uses Boolean operators (`OR`, `AND`) where appropriate
      4. strips out any leading prepositions from keywords (e.g. 'at Google' → 'Google')
      5. contains no extra explanation—output only the search string.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
You are a search‐query engineer. Convert the following user requirement into a single, optimized Google search string that:

1. **always** begins with `site:linkedin.com/in`
2. Extract and focus on specific technical terms, organizations, skills, and credentials from the requirement
3. Avoid generic phrases like "published papers" or "worked at" - instead extract the specific technical domains, organizations, or qualifications
4. Use exact‐phrase quotes only for multi‐word specific terms (like organization names, technical specialties)
5. Use Boolean operators (`OR`, `AND`) strategically to connect key concepts
6. For any organization or entity keywords, remove any prepositions such as 'at', 'in', 'on', so that only the bare term remains
7. Contains no extra explanation—output only the search string

Requirement:
{query}
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={"max_output_tokens": 64}
    )
    return response.text.strip()


def main():
    """
    Main function to demonstrate the usage of the profile search and analysis system.
    """
    # Get your own profile
    my_profile = api.get_profile('vaibhav-mehra-main')
    my_profile_info = extract_useful_profile_info(my_profile)
    
    # Search for profiles
    query = "I want to connect with people published papers in ICRA and graduated from UCL"
    formatted_query = format_search_query(query)
    print(f"Formatted query: {formatted_query}")
    profiles = search_social_media(formatted_query)
    
    # Analyze profiles
    analyzed_profiles = analyze_profile(profiles, query, my_profile_info)
    
    # Print results
    for profile in analyzed_profiles:
        print("\n" + "="*80)
        profile_data = profile['profile']
        
        # Handle different profile structures based on platform
        if profile_data.get('platform') == 'Twitter/X':
            print(f"👤 Profile: {profile_data['name']}")
            print(f"📝 Bio: {profile_data.get('bio', 'N/A')}")
            print(f"🌐 Platform: {profile_data['platform']}")
        elif profile_data.get('platform') == 'Instagram':
            print(f"👤 Profile: {profile_data['name']}")
            print(f"🌐 Platform: {profile_data['platform']}")
            print(f"💬 Bio: {profile_data.get('bio', 'N/A')}")
            print(f"🔗 Profile URL: {profile_data['profile_url']}")
        elif profile_data.get('platform') == 'LinkedIn':
            print(f"👤 Profile: {profile_data['name']}")
            print(f"🌐 Platform: {profile_data['platform']}")
            print(f"💼 Headline: {profile_data.get('headline', 'N/A')}")
            print(f"🔗 Profile URL: {profile_data['profile_url']}")
        
        analysis = profile['analysis']
        print("\n🎯 Match Reasons:")
        for reason in analysis.get('match_reasons', []):
            print(f"• {reason}")
        
        print("\n🤝 Commonalities:")
        for common in analysis.get('commonalities', []):
            print(f"• {common}")
        
        print("\n💡 Value Propositions:")
        for value in analysis.get('value_propositions', []):
            print(f"• {value}")
        
        print("\n✉️ Suggested Opening Message:")
        print(analysis.get('opening_message', ''))
        
        print("="*80)

if __name__ == "__main__":
    main()
