import os
import sys
import asyncio
import streamlit as st
from dotenv import load_dotenv

from agno.agent import Agent
from llama_index.llms.groq import Groq
from agno.models.openai import OpenAIChat
from agents_arion import team_leader, transport_agent
from agents_sahil import transport_agent, location_agent, sightseeing_agent, hotel_booking_agent
from mcp_agents import transport_mcp_agent, hotel_booking_mcp_agent, sightseeing_mcp_agent, location_mcp_agent

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

places_visited = list()

async def multi_agent_collaboration(start_location: str, tourist_destination: str, end_location: str, budget: float, total_days: int, number_of_people: int):
    
    """
    This function coordinates the multi-agent collaboration for a travel itinerary.
    It hard codes the flow between individual agents and their respective tasks.
    We didn't want some pre-defined "team agent" to have the control, instead we wanted to have a more flexible approach.
    """
    
    assert(total_days > 0), "Total days must be greater than 0"
    assert(budget > 0), "Budget must be greater than 0"
    assert(number_of_people > 0), "Number of people must be greater than 0"
    assert(start_location != tourist_destination), "Start location and tourist destination must be different"
    
    start = start_location
    end = tourist_destination
    
    total_prompt = ""
    day = 0
    original_total_days = total_days
    
    # for error tracking
    consecutive_failures = 0
    max_consecutive_failures = 3
    
    while(total_days > 0 and consecutive_failures < max_consecutive_failures):
        
        day += 1
        day_results = {}
        day_success = True
        
        print(f"\n{'='*50}")
        print(f"Processing Day {day} ({total_days} days remaining)")
        print(f"Route: {start} -> {end}")
        print(f"{'='*50}")
        
        ## transport agent
        try:
            print(f"Getting transport options from {start} to {end}...")
            transport = await transport_mcp_agent(
                message = f"Find me the price (convert to USD) of traveling from {start} to {end} using car, train, flight for {number_of_people} people. Please return in json format, no unnecessary text to be returned.",
                people = number_of_people,
            )
            
            if transport and transport.strip():
                day_results['transport'] = transport
                print(f"Transport options retrieved successfully")
            else:
                day_results['transport'] = f"Transport information not available for {start} to {end}"
                print(f"Transport agent returned empty result")
                day_success = False
                
        except Exception as e:
            print(f"Transport agent failed: {e}")
            day_results['transport'] = f"Error getting transport options from {start} to {end}: {str(e)}"
            day_success = False
        
        ## sightseeing agent
        try:
            print(f"Getting sightseeing options for {end}...")
            sightseeing = await sightseeing_mcp_agent(
                message = f"Find me the 4 best sightseeing options for the location {end} for {number_of_people} people. Be very specific and give me the best options.",
                place = end,
                people = number_of_people,
            )
            
            if sightseeing and sightseeing.strip():
                day_results['sightseeing'] = sightseeing
                print(f"Sightseeing options retrieved successfully")
            else:
                day_results['sightseeing'] = f"Sightseeing information not available for {end}"
                print(f"Sightseeing agent returned empty result")
                day_success = False
                
        except Exception as e:
            print(f"Sightseeing agent failed: {e}")
            day_results['sightseeing'] = f"Error getting sightseeing options for {end}: {str(e)}"
            day_success = False
        
        ## hotel booking agent
        try:
            print(f"Getting hotel options for {end}...")
            hotel = await hotel_booking_mcp_agent(
                message = f"Find me the best hotel in {end} for {number_of_people} people. Be very specific and give me the best options with prices (convert to USD).",
                place = end,
                people = number_of_people,
            )
            
            if hotel and hotel.strip():
                day_results['hotel'] = hotel
                print(f"Hotel options retrieved successfully")
            else:
                day_results['hotel'] = f"Hotel information not available for {end}"
                print(f"Hotel booking agent returned empty result")
                day_success = False
                
        except Exception as e:
            print(f"Hotel booking agent failed: {e}")
            day_results['hotel'] = f"Error getting hotel options for {end}: {str(e)}"
            day_success = False
        
        ## updating start and end locations (only if we have days left)
        next_destination = None
        if total_days > 1:  # only if we have more days left
            try:
                print(f"Finding next destination from {end}...")
                next_destination = await location_mcp_agent(
                    message = f"Find me the nearest most popular tourist destination from {end} where tourists can spend the night. Consider that they have {total_days-1} days left.",
                    place = end,
                    days_left = total_days - 1,
                    tourist_destination = tourist_destination,
                    places_visited = places_visited,
                )
                
                places_visited.append(next_destination)
                
                if next_destination and next_destination.strip():
                    # stripping the response
                    next_destination = next_destination.strip().split('\n')[0].strip()
                    print(f"Next destination: {next_destination}")
                else:
                    next_destination = end_location  # default to end location
                    print(f"Location agent returned empty result, using end location as fallback")
                    day_success = False
                    
            except Exception as e:
                print(f"Location agent failed: {e}")
                next_destination = end_location  # default to end location
                day_success = False
        else:
            next_destination = end_location
            print(f"Last day - setting destination to final location: {end_location}")
        
        ## appending everything to the final prompt
        day_info = f"""
                    Day {day}: {start} to {end}
                    Transport: {day_results.get('transport', 'Information not available')}
                    Hotel: {day_results.get('hotel', 'Information not available')}
                    Sightseeing: {day_results.get('sightseeing', 'Information not available')}
                    Next Destination: {next_destination if next_destination != end else 'Final destination'}
                    ---
                    """
        
        # st.markdown(day_info)
        total_prompt += day_info
        
        # failure counter
        if day_success:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            print(f"Day {day} had issues. Consecutive failures: {consecutive_failures}")
        
        # updating locations for next iteration
        start = end
        end = next_destination
        
        total_days -= 1
        
        print(f"Day {day} completed. Days remaining: {total_days}")
        
        await asyncio.sleep(1)
    
    if consecutive_failures >= max_consecutive_failures:
        error_msg = f"\nNOTICE: Trip planning encountered repeated issues after Day {day}. Some information may be incomplete or based on fallback responses.\n"
        total_prompt = error_msg + total_prompt
    
    print(f"\nTrip planning completed! Generated itinerary for {original_total_days} days.")
    return total_prompt


# Async wrapper for Streamlit
def run_multi_agent_collaboration(start_location, tourist_destination, end_location, budget, total_days, number_of_people):
    """
    Wrapper function to run the async multi_agent_collaboration in a sync context
    """
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async function
        return loop.run_until_complete(
            multi_agent_collaboration(start_location, tourist_destination, end_location, budget, total_days, number_of_people)
        )
    except Exception as e:
        return f"Error in trip planning: {str(e)}\n\nPlease check your API keys and internet connection."


if __name__ == "__main__":
    
    st.set_page_config(layout='wide', page_title="Around the World with Agents")
    st.title("Around the World with Agents")
    st.write("This is a collaborative multi-agent application for travel itinerary planning.")
    
    with st.sidebar:
        st.header("API Configuration")
        OPENAI_API_KEY = st.text_input("OpenAI API Key", type="password")
        GROQ_API_KEY = st.text_input("GROQ API Key", type="password")
        GOOGLE_MAPS_API_KEY = st.text_input("Google Maps API Key", type="password")
        
    if not OPENAI_API_KEY or not GROQ_API_KEY or not GOOGLE_MAPS_API_KEY:
        st.error("Please provide all API keys in the sidebar to proceed.")
        
    with st.sidebar:
        st.header("Trip Details")
        start_location = st.text_input("Start Location")
        tourist_destination = st.text_input("Tourist Destination(s)")
        end_location = st.text_input("End Location")
        budget = st.number_input("Budget (in USD)")
        total_days = st.number_input("Total Days")
        number_of_people = st.number_input("Number of People")
        if not start_location or not tourist_destination or not end_location or not budget or not total_days or not number_of_people:
            st.error("Please fill in all location fields.")
    
    if st.button("Generate Itinerary"):
        with st.spinner(f"Collecting all information... Might take a few minutes..."):
            total_prompt = run_multi_agent_collaboration(
                start_location,
                tourist_destination,
                end_location,
                budget,
                total_days,
                number_of_people
            )
        
        if total_prompt:
            st.subheader("Generated Itinerary")
            
            with st.spinner("Generating the final itinerary..."):
                llm = Groq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
                total_prompt = f"""
                You are an travel itinerary planner.
                You have been given the following information:
                Start Location: {start_location}
                Tourist Destination: {tourist_destination}
                End Location: {end_location}
                Budget: {budget} $
                Total Days: {total_days}
                Number of People: {number_of_people}
                
                You have to make sure their total expenses stay within the budget.
                You have to make sure that the itinerary is detailed and includes all the necessary information, 
                easy to understand anf follow, well-structured and organized, comprehensive and covers all aspects 
                of the trip, realistic and feasible, enjoyable and memorable, safe and secure.
                
                You have to provide day-wise itinerary for the trip, including:
                - Transport options
                - Hotel options
                - Sightseeing options
                - Any other relevant information
                
                You must not make any logical errors or assumptions.
                Any calculation involving money must be accurate and precise.
                Finally, let them know the final cost of the trip and how much they have saved. 
                If the budget is not enough, let them know that too.
                
                Make sure to include all the information in the itinerary.
                Please maintain a uniform font size and style throughout the itinerary and use bullet points for clarity. Maintain headings and subheadings for different sections.
                Please don't make the itinerary look dirty or messy. Make sure you use proper formatting and structure.
                Please generate a detailed travel itinerary based on the following information:
                
                """ + total_prompt
                response = llm.complete(total_prompt)
            
            st.markdown(response)
            st.success("Enjoy your trip!")
        else:
            st.error("Failed to generate itinerary. Please check your API keys and internet connection.")