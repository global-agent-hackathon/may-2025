import streamlit as st
import google.generativeai as genai
from PIL import Image
from phi.model.google import Gemini
from phi.agent import Agent, RunResponse
from phi.utils.pprint import pprint_run_response
from pathlib import Path
import tempfile
from phi.tools.serpapi_tools import SerpApiTools
from phi.tools.firecrawl import FirecrawlTools


from dotenv import load_dotenv
load_dotenv()
import os

# Configure Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

st.set_page_config(    
    page_icon="🏠",
    page_title="RealEstate AI Agent",
    layout="wide"
)

# Streamlit UI
st.title("Real Estate AI Agent - (Floor Map Analyser)")
st.header("Powered by Agno and Google Gemini 2.0 Flash")
st.info("Developed by GnanaSelvan G. With ❤️ from Chennai, India")

with st.sidebar:
    st.subheader("Enter your location")
    city = st.text_input(
            "City",
            placeholder="Enter city name (e.g., Bangalore)",
            help="Enter the city where you want to search for properties"
        )
    st.divider()
    st.title("Current Features 🚀")   
    
    st.divider()

    st.subheader(" 🏡 Floor Plan Analysis")   
  
    st.subheader(" 🏡 Interior Recommendations")   
    
    st.subheader(" 🏡 Sunlight and Ventilation Insights ")   
    
    st.subheader(" 🏡 Market Valuations Insights")   
    st.subheader(" 🏡 Legal and Compliance Advice") 
    st.divider()

    st.title("🌟Upcoming Features 🚀")   
    
    st.divider()

    st.subheader(" 🏗️ 3D Floor Plan Generation")   
  
    st.subheader(" 🏗️ Augmented Reality (AR) View")   
    
    st.subheader(" 🏗️ Virtual Home Tour")   
    
    st.subheader(" 🏗️ Local Area News and happenings")   
    st.subheader(" 🏗️ Chat with Builder's Brochure")   
    st.divider()

#Prompt
#Prompt
floorMapAnalyzerprompt= """You are a real estate recommender agent specializing in analysing floor plan and providing insights. 
Analyse this floor plan based on Hallway Length, Natural Light, Strengths, Drawback,Orientation, Organization, Entry.
Also provide total carpet area of each room in sq.ft by calculating the multiplication of dimensions.
Also suggest possible modifications for better organization and effective space usage
Also mention total area in sq.ft occupied by spaces like hallway, roomway, foyer etc.
and total area in sq.ft occupied by spaces like bedroom, living area, kitchen, balcony""" 

interiorPrompt= """"You are a professional interior designer specializing in space optimization and home aesthetics. 
            Your job is to analyze the floor plan and provide expert recommendations on furniture placement, space-saving solutions, and decor ideas. 
            You take into account natural light availability, room functionality, and user preferences to suggest ideal color schemes, lighting solutions, and design enhancements. 
            You also identify underutilized spaces and propose creative ways to repurpose them.
            Also make use of serapi tool to search google and display 5 home interior relevant results as image. 
            Display the image search results with clickable hyperlinks and image preview.
            Based on the following floor map analysis, suggest interior Ideas: """

sunlightandventilationPrompt= """You are a sustainability expert specializing in natural light optimization and ventilation. 
            Your role is to analyze the floor plan's orientation and window placements to determine 
            how much sunlight and fresh air each room will receive. 
            You assess cross-ventilation efficiency and suggest ways to improve daylight exposure and airflow. 
            Your insights help homeowners reduce energy consumption and enhance indoor comfort.
            Based on the following floor map analysis, suggest sunlight and ventilation Insights:"""

energyefficiencyPrompt= """You are an energy efficiency consultant and green building expert. 
            Your task is to evaluate the floor plan for energy consumption, heating/cooling efficiency, and overall sustainability. 
            You estimate the home’s carbon footprint based on room sizes, window placements, and likely appliance usage. 
            You also suggest energy-efficient upgrades, such as insulation improvements, smart home automation, and solar panel feasibility.
            Based on the following floor map analysis, suggest energy efficiency Insights:"""

marketValuationdesc= """You are a real estate market analyst with expertise in property valuation and investment strategy. 
            Your role is to estimate the property’s market value by analyzing factors such as 
            total area, number of rooms, location, and unique features. 
            You compare it with similar properties in the area and assess rental yield and long-term appreciation potential. 
            You also provide recommendations on home upgrades that can boost resale value and maximize return on investment.
            Based on the following floor map analysis, suggest market Valuation Insights from """
    
legalCompliancePrompt= """You are a legal and compliance expert specializing in real estate regulations. 
            Your job is to review the floor plan for compliance with local building codes, safety regulations, and environmental standards. 
            You identify any potential violations, such as improper room dimensions, ventilation issues, or missing emergency exits. 
            You also provide insights on mortgage eligibility and legal considerations for property buyers.
            Also make use of serapi tool to search youtube and display 5 relevant results. 
            Display the youtube search results with clickable hyperlinks and thumbnail.
            Based on the following floor map analysis, suggest legal Compliance Insights: """

marketValuationPrompt = f"{marketValuationdesc} {city} "
        

# AGNO Agents
image= None

floor_map_agent= Agent(
    name="Floor Map Analyzer",
    role="You are a real estate recommender agent specializing in analysing floor plan and providing insights",
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[],  # Add any relevant tools if needed
    instructions=floorMapAnalyzerprompt,
    debug_mode=True,
    show_tool_calls=True,
    markdown=True,
)

interior_recommender_agent=Agent(
    name="Interior Recommender Agent",
    role="You are a professional interior designer specializing in space optimization and home aesthetics",
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(search_youtube=False)],  # Add any relevant tools if needed
    instructions=interiorPrompt,
    debug_mode=True,
    show_tool_calls=True,
    markdown=True,
)

sunlight_and_ventilation_agent=Agent(
    name="sunlight_and_ventilation_agent",
    role="You are a sustainability expert specializing in natural light optimization and ventilation",
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(search_youtube=True)],  # Add any relevant tools if needed
    instructions=sunlightandventilationPrompt,
    debug_mode=True,
    show_tool_calls=True,
    markdown=True,
)

energy_efficiency_agent=Agent(
    name="energy_efficiency_agent",
    role="You are an energy efficiency consultant and green building expert",
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(search_youtube=True)],  # Add any relevant tools if needed
    instructions=energyefficiencyPrompt,
    debug_mode=True,
    show_tool_calls=True,
    markdown=True,
)
marketValuationPrompt = ""
marketValuation_agent=Agent(
    name="marketValuation_agent",
    role="You are a real estate market analyst with expertise in property valuation and investment strategy",
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[FirecrawlTools()],  # Add any relevant tools if needed
    instructions=f"""You are a real estate market analyst with expertise in property valuation and investment strategy. 
            Your role is to estimate the property’s market value by analyzing factors such as 
            total area, number of rooms, location, and unique features. 
            You compare it with similar properties in the area and assess rental yield and long-term appreciation potential. 
            You also provide recommendations on home upgrades that can boost resale value and maximize return on investment.
            Search for similar floor plan only from authentic and trusted real estate websites such as 99acres.com, magicbricks.com,nobroker.com,housing.com and other reputable platforms.,
            Based on the following floor map analysis, suggest market Valuation Insights from {city} 
            and provide valuation insights of top 10 residential localities in {city}
            Also provide predictions that how much this property will appreciate in next 5 years, 10 years, 20 years, 40 years""",
    debug_mode=True,
    show_tool_calls=True,
    markdown=True,
)

legalCompliance_agent=Agent(
    name="legalCompliance_agent",
    role="You are a legal and compliance expert specializing in real estate regulations",
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(search_youtube=True)],  # Add any relevant tools if needed
    instructions=legalCompliancePrompt,
    debug_mode=True,
    show_tool_calls=True,
    markdown=True,
)


#Initialize the Agno Agents
#floor_map_agent  = floor_map_agent()
#interior_recommender_agent = interior_recommender_agent()




uploaded_file = st.file_uploader("Upload Floor Map Image", type=["png", "jpg", "jpeg"])


if uploaded_file is not None:
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.write("Temporary file path:", tmp_path)
    # Now you can pass tmp_path to other functions expecting a file path
    image = Image.open(uploaded_file)
    st.image(uploaded_file, caption="Uploaded Floor Map", use_container_width=False,width=800)


        # Run agent and return the response as a variable
        #floor_map_result: RunResponse = floor_map_agent.run(floorMapAnalyzerprompt,images=[tmp_path])
#         floor_map_agent.print_response(
#     floorMapAnalyzerprompt,
#     images=[
#        tmp_path
#          ],
# )
        # Print the response in markdown format
            #pprint_run_response(response, markdown=True)

    #Run Agno Agents
    with st.spinner("Analyzing floor map..."):
        floor_map_result = floor_map_agent.run(floorMapAnalyzerprompt,images=[tmp_path])    
    with st.spinner("Generating interior recommendations..."):
        interior_result = interior_recommender_agent.run(interiorPrompt,images=[tmp_path])
    with st.spinner("Generating sunlight and ventilation recommendations.."):
        sunlight_and_ventilation_result = sunlight_and_ventilation_agent.run(sunlightandventilationPrompt,images=[tmp_path])
    with st.spinner("Generating energy efficiency suggestions..."):
        energy_efficiency_result = energy_efficiency_agent.run(energyefficiencyPrompt,images=[tmp_path])
    with st.spinner("Generating market Valuation insights.."):
        marketValuation_result = marketValuation_agent.run(marketValuationPrompt,images=[tmp_path])
    with st.spinner("Generating legal Compliance reports..."):
        legalCompliance_result = legalCompliance_agent.run(legalCompliancePrompt,images=[tmp_path])


#     #Agent Teams
#     agent_team = Agent(
#     team=[floor_map_agent, interior_recommender_agent],
#     model=Gemini(id="gemini-2.0-flash-exp"),
#     instructions=["Always include sources", "Use tables to display data"],
#     show_tool_calls=True,
#     markdown=True,
# )

    
    #Run Agno Teams
    # team_results= agent_team.run(image=image)
    # with st.expander("📈 Team results"):
    #  st.subheader("team Results")
    #  st.markdown(team_results)


    # Display results
    with st.expander("📈 Floor Map Analysis"):
     st.subheader("Floor Map Analysis")
     st.markdown(floor_map_result.content)

    with st.expander("📈 Interior Design Recommendations"):
     st.subheader("Interior Design Recommendations")    
     st.markdown(interior_result.content)

    with st.expander("📈 Sunlight and Ventilation Recommendations"):
     st.subheader("Sunlight and Ventilation Recommendations")    
     st.markdown(sunlight_and_ventilation_result.content)

    with st.expander("📈 Energy Efficiency Recommendations"):
     st.subheader("Energy Efficiency Recommendations")    
     st.markdown(energy_efficiency_result.content)

    with st.expander("📈 Market Valuation Insights"):
     st.subheader("Market Valuation Insights")    
     st.markdown(marketValuation_result.content)

    with st.expander("📈 Legal Compliance Regulations"):
     st.subheader("Legal Compliance Regulations")    
     st.markdown(legalCompliance_result.content)


