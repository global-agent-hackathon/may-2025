import os
from agno.agent import Agent, RunResponse
from agno.tools.firecrawl import FirecrawlTools
from agno.models.groq import Groq
import streamlit as st

import logging

logging.basicConfig(level=logging.DEBUG)

st.title("RhythmWeaver 🎸")
st.caption("Generative Chords Improvisation Agent")

groq_api_key = st.sidebar.text_input("GROQ API KEY", type="password")
firecrawl_api_key = st.sidebar.text_input("FIRECRAWL API KEY", type="password")

keys_provided = all([groq_api_key, firecrawl_api_key])

url = st.text_input("Enter chords webapp URL:")

# Define the tools
def title(agent: Agent, title: str) -> str:
    """Add song title"""
    agent.session_state["title"] = title
    return agent.session_state['title']

def old_chord(agent: Agent, old_chord: str) -> str:
    """Add html <pre> old chords"""
    agent.session_state["old_chord"] = old_chord
    return agent.session_state['old_chord']

def new_chord(agent: Agent, new_chord: str) -> str:
    """Add html <pre> improvised chords"""
    agent.session_state["new_chord"] = new_chord
    return agent.session_state['new_chord']

if st.button("Generate Improvisation"):
    if not keys_provided:
        st.warning("Please enter all required API keys.")
    elif not url:
        st.warning("Please enter valid URL.")
    else:
        os.environ["GROQ_API_KEY"] = groq_api_key
        os.environ["FIRECRAWL_API_KEY"] = firecrawl_api_key

        with st.spinner("Improving chords..."):
            try:

                agent = Agent(
                    name="Generative Chords Improvisation Agent",
                    agent_id="generative_chords_improvisation_agent",
                    model=Groq(id="llama-3.3-70b-versatile"),
                    session_state={"title": "", "old_chord": "", "new_chord": ""},
                    tools=[
                        FirecrawlTools(),
                        title,
                        old_chord,
                        new_chord,
                    ],
                    description="Your primary role is to generate generative musical improvisations and modify musical chords within an HTML code snippet.",
                    instructions=[
                        """Your task is to use FirecrawlTools to scrape and extract chords and lyrics from a given URL. The chords and lyrics are typically enclosed within the <pre> tags, with chords aligned using leading spaces and spaces between chord tags relative to the lyrics. This spatial alignment is crucial. 
                        Follow these steps for optimal results:""",
                        "1: Scrape the URL using FirecrawlTools to obtain chords and lyrics within the <pre> tags, keeping their alignment intact.",
                        "2: Analyze the extracted lyrics and chords to understand the themes, sentiments, structures, and rhythms. Use this analysis to inform your improvisation.",
                        "3: Generate generative chords improvisations based on the textual input, feature extraction, and especially focusing on the spaces that create timelines. The lyrics must not be changed or translated.",
                        "4: Wrap the original and improvised chords back into the <pre> tag format. Ensure the original lyrics and their spatial alignment with the chords are maintained precisely."
                    ],
                    add_state_in_messages=True,
                    markdown=False,
                    debug_mode=True,
                )

                agent.run(f"Begin by scraping and extracting the data from the URL provided: {url}")

                st.subheader(f"{agent.session_state["title"]} (Improvised Chords)")
                st.html(f"<pre>{agent.session_state["new_chord"]}</pre>")

                st.subheader(f"{agent.session_state["title"]} (Original Chords)")
                st.html(f"<pre>{agent.session_state["old_chord"]}</pre>")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("Enter chords webapp URL and click 'Generate Improvisation'.")