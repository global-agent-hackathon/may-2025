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
import random
from flask import Flask, request, jsonify
import re
import traceback


# Initialize API keys
print("Reading API keys from environment variables...")
PERPLEXITY_API_KEY = ""
GEMINI_API_KEY = ""
OPENAI_API_KEY  = ""

if not PERPLEXITY_API_KEY or not GEMINI_API_KEY or not OPENAI_API_KEY:
    print("ERROR: One or more API keys are missing! (Perplexity, Gemini, OpenAI)")
    raise ValueError("API keys not set in environment variables for Perplexity, Gemini, and OpenAI")

print(f"API keys loaded successfully - Perplexity: {'***' + PERPLEXITY_API_KEY[-4:] if PERPLEXITY_API_KEY else 'None'}, Gemini: {'***' + GEMINI_API_KEY[-4:] if GEMINI_API_KEY else 'None'}, OpenAI: {'***' + OPENAI_API_KEY[-4:] if OPENAI_API_KEY else 'None'}")

# Define structured output models
print("Defining data models for structured output...")
class ProfileSearchResult(BaseModel):
    summary: str = Field(..., description="A summary of the person's background and achievements")
    recent_activities: List[str] = Field(..., description="Recent professional activities or news")
    expertise: List[str] = Field(..., description="Areas of expertise and notable skills")
    sources: List[str] = Field(..., description="Detailed sources including URLs, dates, and context for each piece of information")

class SourceAnalysis(BaseModel):
    source: str = Field(..., description="The source URL or publication name")
    date: str = Field(..., description="When the information was published or last updated")
    key_information: List[str] = Field(..., description="Key information found in this source")
    significance: str = Field(..., description="Why this information is significant")

class DetailedAnalysis(BaseModel):
    source_analyses: List[SourceAnalysis] = Field(..., description="Detailed analysis of information from each source")
    key_achievements: List[str] = Field(..., description="Notable achievements and milestones")
    professional_timeline: List[str] = Field(..., description="Chronological timeline of professional events")
    impact_assessment: str = Field(..., description="Assessment of the person's impact in their field")

print("Initialized data models successfully")

# Initialize Perplexity agent for profile search
print("Initializing Perplexity search agent with model 'sonar'...")
search_agent_perplexity = Agent(
    name="Perplexity Profile Searcher",
    model=Perplexity(id="sonar", api_key=PERPLEXITY_API_KEY),
    instructions=[
        "You are a professional profile research assistant that finds and analyzes information about people.",
        "Given basic profile information, search for and provide detailed insights about the person. GIVE ME AS MUCH INFORMATION AS POSSIBLE.",
        "Focus on professional achievements, recent activities, and areas of expertise.",
        "For each piece of information provided, include a detailed source with:",
        "- The source URL or publication name",
        "MAKE SURE TO GIVE AS MUCH INFORMATION AS POSSIBLE FOR EACH PIECE OF INFORMATION.",
        "- The date of the information",
        "- Context about why this source is reliable",
        "If information is uncertain or outdated, clearly indicate this and explain why."
    ],
    response_model=ProfileSearchResult,
    markdown=True
)
print("Perplexity search agent initialized with response model: ProfileSearchResult")

# Initialize OpenAI agent for profile search
print("Initializing OpenAI search agent with model 'gpt-4o'...")
search_agent_openai = Agent(
    name="OpenAI Profile Searcher",
    model=OpenAIChat(id="gpt-4o-search-preview-2025-03-11", api_key=""),
    instructions=[
        "You are an advanced AI research assistant specializing in deep profile analysis and information synthesis.",
        "Given basic profile information (and potentially prior search results), conduct a thorough web search to find comprehensive details.",
        "Focus on uncovering unique professional achievements, specific projects, technical skills, notable collaborations, and quantifiable impacts.",
        "Prioritize information not commonly found or that requires deeper connections between various sources.",
        "For each piece of information provided, include a detailed source with:",
        "- The source URL or publication name",
        "- The date of the information",
        "- Context about why this source is reliable and how it contributes to the overall profile.",
        "If information is uncertain or outdated, clearly indicate this and explain why. Strive for maximum detail and insight."
    ],
    response_model=ProfileSearchResult,
    markdown=True
)
print("OpenAI search agent initialized with response model: ProfileSearchResult")

# Initialize Gemini agent for detailed analysis
print("Initializing analysis agent with Gemini model 'gemini-2.0-flash'...")
analysis_agent = Agent(
    name="Profile Analyzer",
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    instructions=[
        "You are an expert profile analyst that provides deep insights about people's professional journeys.",
        "Given a collection of search results about a person (potentially from multiple search agents), analyze, synthesize, and structure the information to create a single, comprehensive, and highly detailed profile.",
        
        "For each source in `source_analyses`:",
        "  - Extract multiple distinct and impactful facts into the `key_information` list. Aim for 2-3 distinct facts per source if available.",
        "  - The `significance` field MUST clearly explain why this source is crucial for understanding the person's profile and what unique, specific insights it offers. Avoid generic statements. Be specific.",
        
        "For each item in `key_achievements` and `professional_timeline`:",
        "  - Provide a descriptive title or role (e.g., 'Senior Software Engineer at Company X', 'Led Project Y').",
        "  - Include relevant dates or time periods (e.g., 'Jan 2020 - Dec 2022', 'Completed May 2021').",
        "  - Briefly describe the core activity, project, or responsibility in 1-2 sentences.",
        "  - Mention 1-2 specific, quantifiable outcomes, impacts, or key skills demonstrated whenever possible. (e.g., 'Increased efficiency by 15%', 'Developed 3 new features', 'Mastered Python and AWS').",
        "  - Format this information clearly within each single string entry for the list. Example: 'Title: Senior Engineer. Period: 2020-2022. Description: Led a team of 5. Impact: Delivered project X ahead of schedule.'",
        
        "The `impact_assessment` should be a thoughtful, multi-faceted summary of the person's overall professional impact. If possible, structure it with explicit sub-headings like 'Key Strengths:', 'Primary Areas of Impact:', or 'Noteworthy Contributions:' directly within the string, based on the synthesized information. Provide concrete examples.",
        
        "Focus on creating a chronological timeline where appropriate, highlighting major achievements with supporting evidence, and assessing the individual's impact.",
        "Ensure all information is meticulously attributed to its original source(s) when constructing the narrative within the `DetailedAnalysis` fields.",
        "Your goal is to produce the most detailed and insightful analysis possible from all available inputs, ensuring the final `DetailedAnalysis` object is rich and informative."
    ],
    response_model=DetailedAnalysis,
    markdown=True
)
print("Analysis agent initialized with response model: DetailedAnalysis")

# Initialize Refinement Agent
print("Initializing Refinement Agent with OpenAI model 'gpt-4o-search-preview-2025-03-11'...")
refinement_agent = Agent(
    name="Content Refinement Agent",
    model=OpenAIChat(id="gpt-4o-search-preview-2025-03-11", api_key=""),
    instructions=[
        "You are an expert editor. Your task is to refine the content of a DetailedAnalysis object to ensure it is presented in clear, engaging, and grammatically correct professional English.",
        "Target the following fields for refinement:",
        "  - Each string in the `key_achievements` list.",
        "  - Each string in the `professional_timeline` list.",
        "  - Each string within each `source_analyses[i].key_information` list.",
        "  - The `source_analyses[i].significance` string for each source analysis.",
        "  - The `impact_assessment` string.",
        "For `key_achievements` and `professional_timeline` items that are structured (e.g., 'Role: X. Period: Y. Description: Z. Impact: A.'), transform them into well-written narrative sentences or short paragraphs. For example, 'Role: Lead PM. Period: 2020-2022. Description: Managed product. Impact: Launched V2.' should become something like: 'As Lead Product Manager from 2020 to 2022, they successfully managed the product lifecycle, culminating in the launch of version 2.'",
        "For `source_analyses[i].key_information` strings, ensure each is a complete, understandable sentence or a concise, well-phrased bullet point if appropriate for the context.",
        "For `source_analyses[i].significance`, rewrite the text to be clear and compelling, highlighting the source's importance smoothly.",
        "For `impact_assessment`, rewrite this to be a coherent and compelling narrative. Ensure any sub-headings like 'Key Strengths:' are naturally integrated or the content flows well without them if it reads better.",
        "Maintain all factual information and the original meaning. Your focus is SOLELY on improving the language, flow, and presentation.",
        "Do NOT alter the structure of the `DetailedAnalysis` object itself (e.g., do not add or remove fields, or change field names). Return the same object type with refined text content within the specified fields.",
        "Avoid overly casual or informal language. Maintain a professional and polished tone throughout.",
        "If a field is already well-written, you may leave it as is, but always review for potential improvements."
    ],
    response_model=DetailedAnalysis,
    markdown=True
)
print("Refinement agent initialized with response model: DetailedAnalysis")

# Create the agent team
print("Creating agent team with Perplexity, OpenAI, and Analysis agents...")
print("Configuring team instructions and model...")
profile_team = Agent(
    team=[search_agent_perplexity, search_agent_openai, analysis_agent, refinement_agent],
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY),
    instructions=[
        "You are coordinating a team of expert profile research, analysis, and refinement agents to build the most comprehensive and well-written profile possible.",
        "1. First, use the 'Perplexity Profile Searcher' agent to gather initial comprehensive information about the person based on the initial query.",
        "2. Second, use the 'OpenAI Profile Searcher' agent. Provide the initial query AND the full, raw output from the 'Perplexity Profile Searcher' as context to this agent. Instruct it to perform a deeper search, aiming to find additional details, verify information, or explore new angles based on the initial findings.",
        "3. Third, pass the full, raw outputs from BOTH the 'Perplexity Profile Searcher' and the 'OpenAI Profile Searcher' to the 'Profile Analyzer' agent.",
        "The 'Profile Analyzer' agent will then synthesize all collected information into a single, detailed, well-structured analysis, adhering to any output limitations like item counts per category.",
        "4. Finally, pass the `DetailedAnalysis` output from the 'Profile Analyzer' to the 'Content Refinement Agent'. This agent will polish the language of the analysis, ensuring it's in clear, engaging, and professional English, without changing the factual content or structure of the DetailedAnalysis object.",
        "The final output of this team should be the refined DetailedAnalysis object produced by the Content Refinement Agent.",
        "IMPORTANT: Limit the output to exactly 3 items in each category (key_achievements, professional_timeline, source_analyses, etc.) in the final DetailedAnalysis object, selecting the most impactful and relevant ones. This limitation should primarily be handled by the 'Profile Analyzer' before the content goes to the 'Content Refinement Agent'.",
        "PRIORITY: Focus on providing highly useful, specific, and actionable information about the person including:",
        "- Concrete projects they have worked on with technical details when applicable",
        "- Specific research papers, patents, or intellectual contributions",
        "- Measurable career achievements with quantifiable impacts when possible",
        "- Unique professional skills or specialized knowledge areas",
        "- Notable collaborations, partnerships, or professional relationships",
        "Avoid generic biographical information unless particularly significant. The goal is depth and comprehensiveness from the combined search efforts."
    ],
    markdown=True
)
print(f"Agent team initialized successfully with {len(profile_team.team)} agents")
print(f"Team model: {profile_team.model.id}")
print("Agent team configuration complete")

# Function to handle profile expansion
def expand_profile(profile_id, profile_data):
    print(f"========== EXPAND PROFILE START ==========")
    print(f"Expanding profile for ID: {profile_id}")
    print(f"Profile data received: {json.dumps(profile_data, indent=2)}")
    
    # Create the search prompt based on profile data
    print("Creating search prompt from profile data...")
    profile_info = f"""
    Name: {profile_data.get('name', 'Unknown')}
    Current Role: {profile_data.get('headline', 'Unknown')}
    Platform: {profile_data.get('platform', 'Unknown')}
    """
    
    print(f"Created profile info for search: {profile_info.strip()}")
    
    search_prompt = f"""
    Please research and provide information about this person based on their profile:
    
    {profile_info}
    
    Focus on:
    1. Their professional background and achievements
    2. Recent activities and developments
    3. Areas of expertise and notable contributions
    
    For each piece of information you provide, include:
    - The exact source (URL, publication, or document)
    - When the information was published or last updated
    - Why this source is reliable or relevant
    """
    
    print(f"Search prompt created, length: {len(search_prompt)} characters")
    print("Running profile team search with agents...")
    start_time = time.time()
    
    try:
        print("Executing agent team.run() with search prompt...")
        # Run the profile team and get output
        result = profile_team.run(search_prompt)
        elapsed_time = time.time() - start_time
        print(f"Profile team search completed in {elapsed_time:.2f} seconds")
        print(f"Result type: {type(result)}")
        print(f"Result content type: {type(result.content)}")
        
        # Print individual agent outputs
        print("\n========== INDIVIDUAL AGENT OUTPUTS ==========")
        for agent in profile_team.team:
            print(f"\n--- {agent.name} Output ---")
            if hasattr(agent, 'last_output'):
                if isinstance(agent.last_output, (ProfileSearchResult, DetailedAnalysis)):
                    print(json.dumps(agent.last_output.model_dump(), indent=2))
                else:
                    print(str(agent.last_output))
            else:
                print("No output available for this agent")
        print("\n========== END OF AGENT OUTPUTS ==========\n")
        
        # Print the full output from the agentic team
        print("\n========== AGENT TEAM OUTPUT START ==========")
        if isinstance(result.content, DetailedAnalysis):
            print("OUTPUT (DetailedAnalysis object):")
            output_json = result.content.model_dump()
            print(json.dumps(output_json, indent=2)[:1000] + "..." if len(json.dumps(output_json, indent=2)) > 1000 else json.dumps(output_json, indent=2))
        elif isinstance(result.content, str):
            print("OUTPUT (String):")
            print(result.content[:1000] + "..." if len(result.content) > 1000 else result.content)
        else:
            print(f"OUTPUT (Unknown type - {type(result.content)}):")
            content_str = str(result.content)
            print(content_str[:1000] + "..." if len(content_str) > 1000 else content_str)
        print("========== AGENT TEAM OUTPUT END ==========\n")
        
        # Process the result based on its type
        nodes = []
        print("Processing result to create nodes...")
        
        if isinstance(result.content, DetailedAnalysis):
            print(f"Received DetailedAnalysis object with {len(result.content.key_achievements)} achievements, {len(result.content.professional_timeline)} timeline entries, and {len(result.content.source_analyses)} sources")
            analysis = result.content
            
            # Add nodes for key achievements
            print("Creating nodes for key achievements...")
            for i, achievement in enumerate(analysis.key_achievements):
                print(f"Adding achievement node {i+1}: {achievement[:100]}...")
                nodes.append({
                    "id": f"{profile_id}-achievement-{len(nodes)}",
                    "text": achievement,
                    "source": "Achievement",
                    "avatar": None  # Frontend will assign avatars
                })
            
            # Add nodes for timeline entries
            print("Creating nodes for timeline entries...")
            for i, timeline in enumerate(analysis.professional_timeline):
                print(f"Adding timeline node {i+1}: {timeline[:100]}...")
                nodes.append({
                    "id": f"{profile_id}-timeline-{len(nodes)}",
                    "text": timeline,
                    "source": "Timeline",
                    "avatar": None
                })
                
            # Add nodes for source analyses
            print("Creating nodes for source analyses...")
            for i, source in enumerate(analysis.source_analyses):
                print(f"Adding source node {i+1}: {source.source[:50]}...")
                key_info = source.key_information[0] if source.key_information else "Source information"
                print(f"  - Key info: {key_info[:100]}...")
                nodes.append({
                    "id": f"{profile_id}-source-{len(nodes)}",
                    "text": key_info,
                    "source": source.source,
                    "avatar": None
                })
                
        elif isinstance(result.content, str):
            print("Received string result instead of structured object")
            print(f"String content length: {len(result.content)} characters")
            
            json_parsed = False
            
            try:
                if '{' in result.content and '}' in result.content:
                    print("Content contains JSON-like structures, attempting to extract...")
                    
                    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", result.content)
                    
                    if json_match:
                        json_str = json_match.group(1).strip()
                        print(f"Found JSON in code block, length: {len(json_str)}")
                    else:
                        start_idx = result.content.find('{')
                        end_idx = result.content.rfind('}') + 1
                        
                        if start_idx >= 0 and end_idx > start_idx:
                            json_str = result.content[start_idx:end_idx]
                            print(f"Extracted JSON by finding brackets, length: {len(json_str)}")
                        else:
                            json_str = result.content
                            print("Using full content as potential JSON")
                    
                    try:
                        parsed_json = json.loads(json_str)
                        print(f"Successfully parsed JSON with {len(parsed_json) if isinstance(parsed_json, dict) else 'non-dict'} top-level keys")
                        
                        if isinstance(parsed_json, dict):
                            if "key_achievements" in parsed_json and isinstance(parsed_json["key_achievements"], list):
                                print(f"Processing {len(parsed_json['key_achievements'])} key achievements from JSON")
                                for i, achievement in enumerate(parsed_json["key_achievements"]):
                                    if i >= 2: break
                                    print(f"Adding achievement node from JSON: {achievement[:100]}...")
                                    nodes.append({"id": f"{profile_id}-achievement-{len(nodes)}", "text": achievement, "source": "Achievement", "avatar": None})
                            
                            if "professional_timeline" in parsed_json and isinstance(parsed_json["professional_timeline"], list):
                                print(f"Processing {len(parsed_json['professional_timeline'])} timeline entries from JSON")
                                for i, timeline in enumerate(parsed_json["professional_timeline"]):
                                    if i >= 1: break
                                    print(f"Adding timeline node from JSON: {timeline[:100]}...")
                                    nodes.append({"id": f"{profile_id}-timeline-{len(nodes)}", "text": timeline, "source": "Timeline", "avatar": None})
                            
                            if "source_analyses" in parsed_json and isinstance(parsed_json["source_analyses"], list):
                                print(f"Processing {len(parsed_json['source_analyses'])} source analyses from JSON")
                                for i, source_item in enumerate(parsed_json["source_analyses"]):
                                    if i >= 2 or len(nodes) >= 3: break
                                    if isinstance(source_item, dict) and "source" in source_item:
                                        source_url = source_item["source"]
                                        key_info_list = source_item.get("key_information")
                                        key_info = key_info_list[0] if isinstance(key_info_list, list) and key_info_list else f"Information from {source_url}"
                                        print(f"Adding source node from JSON: {source_url[:50]}... - {key_info[:100]}...")
                                        nodes.append({"id": f"{profile_id}-source-{len(nodes)}", "text": key_info, "source": source_url, "avatar": None})
                            
                            if nodes:
                                print(f"Added {len(nodes)} nodes from parsed JSON")
                                json_parsed = True
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON: {str(e)}")
            except Exception as e:
                print(f"Error while trying to parse JSON: {str(e)}")
                traceback.print_exc()
            
            if not json_parsed and len(nodes) == 0:
                print("Attempting to extract structured information from text...")
                try:
                    achievements = re.findall(r'"key_achievements":\s*\[(.*?)\]', result.content, re.DOTALL)
                    if achievements:
                        achievement_items = re.findall(r'"([^"]+)"', achievements[0])
                        print(f"Found {len(achievement_items)} achievements using regex")
                        for i, achievement in enumerate(achievement_items):
                            if i >= 2: break
                            nodes.append({"id": f"{profile_id}-achievement-{len(nodes)}", "text": achievement, "source": "Achievement", "avatar": None})
                            json_parsed = True
                    
                    sources = re.findall(r'"source":\s*"([^"]+)"', result.content)
                    key_info_blocks = re.findall(r'"key_information":\s*\[(.*?)\]', result.content, re.DOTALL)
                    
                    if sources and key_info_blocks and len(sources) == len(key_info_blocks):
                        print(f"Found {len(sources)} sources with key information using regex")
                        for i, (source_url, info_block) in enumerate(zip(sources, key_info_blocks)):
                            if i >= 2 or len(nodes) >= 3: break
                            key_info_items = re.findall(r'"([^"]+)"', info_block)
                            if key_info_items:
                                nodes.append({"id": f"{profile_id}-source-{len(nodes)}", "text": key_info_items[0], "source": source_url, "avatar": None})
                                json_parsed = True
                except Exception as e:
                    print(f"Error while trying to extract structured information: {str(e)}")
                    traceback.print_exc()
                    
            if not json_parsed and len(nodes) == 0:
                print("Falling back to line-by-line parsing as last resort...")
                lines = result.content.split('\n')
                print(f"Parsed into {len(lines)} lines")
                nodes_added = 0
                for i, line in enumerate(lines):
                    if line.strip() and len(line) > 10 and not line.startswith('```'):
                        if line.strip() in ['{', '}', '[', ']'] or line.strip().startswith('"') and line.strip().endswith('",'):
                            continue
                        print(f"Adding text line node {i}: {line[:100]}...")
                        nodes.append({"id": f"{profile_id}-line-{i}", "text": line.strip(), "source": "Text Analysis", "avatar": None})
                        nodes_added += 1
                        if nodes_added >= 3: break
                print(f"Added {nodes_added} nodes from text lines")
        else:
            print(f"WARNING: Unexpected output type: {type(result.content)}")
            print("Creating placeholder node due to unexpected output type")
            nodes = [{"id": f"{profile_id}-info-1", "text": "Information processed", "source": "System", "avatar": None}]
            
        print(f"Generated {len(nodes)} total nodes from analysis")
        limited_nodes = nodes[:3]
        print(f"Final nodes to return:")
        for i, node in enumerate(limited_nodes):
            print(f"  Node {i+1}: {node['text'][:50]}... (Source: {node['source']})")
        print(f"Returning {len(limited_nodes)} nodes (limited to 3)")
        print("========== EXPAND PROFILE END ==========")
        return {"success": True, "nodes": limited_nodes}
        
    except Exception as e:
        print(f"ERROR in expand_profile: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
        print("========== EXPAND PROFILE END WITH ERROR ==========")
        return {"success": False, "error": str(e), "nodes": []}

# Example usage for local testing
if __name__ == "__main__":
    print("========== RUNNING EXTENSION.PY AS MAIN SCRIPT ==========")
    # Example profile information
    profile_info = """
    Name: Satya Nadella
    Current Role: CEO of Microsoft
    Previous Experience: 
    - Executive Vice President of Cloud and Enterprise
    - Senior Vice President of R&D for Online Services Division
    Education: MS in Computer Science from University of Wisconsin-Milwaukee
    """
    
    # Create the search prompt
    print("Creating test search prompt...")
    search_prompt = f"""
    Please research and provide information about this person based on their profile:
    
    {profile_info}
    
    Focus on:
    1. Their professional background and achievements
    2. Recent activities and developments
    3. Areas of expertise and notable contributions
    
    For each piece of information you provide, include:
    - The exact source (URL, publication, or document)
    - When the information was published or last updated
    - Why this source is reliable or relevant

    
    
    If you find conflicting information from different sources, please note this and explain the discrepancy.
    """
    
    print("Running test search with test profile (Satya Nadella)...")
    test_start_time = time.time()
    # Run the profile team and get JSON output
    print("Executing team.run() with test prompt...")
    result = profile_team.run(search_prompt)
    test_elapsed_time = time.time() - test_start_time
    print(f"Test search completed in {test_elapsed_time:.2f} seconds")
    
    # The result.content should now be the DetailedAnalysis object from the analysis_agent
    if isinstance(result.content, DetailedAnalysis):
        print("SUCCESS: Received DetailedAnalysis object as expected")
        result_json = result.content.model_dump()
        print(f"Result structure: {len(result_json['source_analyses'])} sources, {len(result_json['key_achievements'])} achievements, {len(result_json['professional_timeline'])} timeline entries")
        print("\n========== TEST OUTPUT START ==========")
        print(json.dumps(result_json, indent=2))
        print("========== TEST OUTPUT END ==========\n")
    elif isinstance(result.content, str):
        # Fallback if it's still a string (e.g., error message or unexpected output)
        print("WARNING: Output was a string, not a DetailedAnalysis object:")
        print(f"String length: {len(result.content)}")
        print("\n========== TEST OUTPUT START ==========")
        print(result.content)
        print("========== TEST OUTPUT END ==========\n")
    else:
        print(f"ERROR: Unexpected output type: {type(result.content)}")
        print(str(result.content)[:500] + "..." if len(str(result.content)) > 500 else str(result.content))

    print("Test search analysis completed")
    print("========== TEST COMPLETE ==========")

# Setup Flask app
app = Flask(__name__)

# Enable CORS
@app.after_request
def after_request(response):
    print(f"Adding CORS headers to response for path: {request.path}")
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    print(f"Health check endpoint called from {request.remote_addr}")
    return jsonify({"status": "healthy"})

# Chat endpoint (existing functionality)
@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    print(f"Chat endpoint called from {request.remote_addr}")
    print("This endpoint is a placeholder - implementation would be separate")
    # Implementation for chat endpoint...
    # This would be implemented separately
    return jsonify({"success": True, "message": "Chat response", "profiles": []})

# Add this at the end of the file
if __name__ == "__main__":
    print("========== STARTING FLASK SERVER ==========")
    print(f"Starting Flask server on port 5000, host: 0.0.0.0, debug mode: {True}")
    app.run(debug=True, port=5000, host='0.0.0.0')


