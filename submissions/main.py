import streamlit as st
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.github import GithubTools
from agno.tools.exa import ExaTools
from agno.tools.thinking import ThinkingTools
from agno.tools.reasoning import ReasoningTools
import re
import yaml

# Set wide layout
st.set_page_config(layout="wide")

# Load YAML prompts with caching
@st.cache_data
def load_yaml(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        st.error("❌ YAML prompt file not found. Please ensure 'hiring_prompts.yaml' is in the directory.")
        st.stop()
    except yaml.YAMLError as e:
        st.error(f"❌ Error parsing YAML file: {e}")
        st.stop()

data = load_yaml("hiring_prompts.yaml")

description_multi = data.get("description_for_multi_candidates", "")
instructions_multi = data.get("instructions_for_multi_candidates", "")
description_single = data.get("description_for_single_candidate", "")
instructions_single = data.get("instructions_for_single_candidate", "")

# Streamlit UI Setup
st.markdown("""
    <div style="text-align:center;">
        <h1 style="font-size: 2.8rem;">🧠 Candilyzer</h1>
        <p style="font-size:1.1rem;">Elite GitHub + LinkedIn Candidate Analyzer for Tech Hiring</p>
    </div>
""", unsafe_allow_html=True)

# Initialize API key session state variables
for key in ["deepseek_api_key", "github_api_key", "exa_api_key"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# Sidebar
st.sidebar.title("🔑 API Keys & Navigation")
st.sidebar.markdown("### Enter API Keys")
st.session_state.deepseek_api_key = st.sidebar.text_input(
    "DeepSeek API Key", value=st.session_state.deepseek_api_key, type="password"
)
st.session_state.github_api_key = st.sidebar.text_input(
    "GitHub API Key", value=st.session_state.github_api_key, type="password"
)
st.session_state.exa_api_key = st.sidebar.text_input(
    "Exa API Key", value=st.session_state.exa_api_key, type="password"
)

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Select Page",
    ("Multi-Candidate Analyzer", "Single Candidate Analyzer"),
    horizontal=True  # Horizontal radio buttons
)

# Page 1: Multi-Candidate Analyzer
if page == "Multi-Candidate Analyzer":
    st.header("Multi-Candidate Analyzer 🕵️‍♂️")
    st.markdown(
        """
        Enter multiple GitHub usernames (one per line) and a target job role.
        The AI will analyze all candidates with strict criteria.
        """
    )

    with st.form("multi_candidate_form"):
        github_usernames = st.text_area(
            "GitHub Usernames (one per line)",
            placeholder="username1\nusername2\n..."
        )
        job_role = st.text_input("Target Job Role", placeholder="e.g. Backend Engineer")
        submit = st.form_submit_button("Analyze Candidates")

    if submit:
        if not github_usernames or not job_role:
            st.error("❌ Please enter both usernames and job role.")
        elif not all([st.session_state.deepseek_api_key, st.session_state.github_api_key, st.session_state.exa_api_key]):
            st.error("❌ Please enter all API keys in the sidebar.")
        else:
            usernames = [u.strip() for u in github_usernames.split("\n") if u.strip()]
            if not usernames:
                st.error("❌ Please enter at least one valid GitHub username.")
            else:
                agent = Agent(
                    description=description_multi,
                    instructions=instructions_multi,
                    model=DeepSeek(id="deepseek-coder", api_key=st.session_state.deepseek_api_key),
                    name="StrictCandidateEvaluator",
                    tools=[
                        ThinkingTools(think=True, instructions="Analyze GitHub candidates with strict criteria"),
                        GithubTools(access_token=st.session_state.github_api_key),
                        ExaTools(api_key=st.session_state.exa_api_key, include_domains=["github.com"], type="keyword"),
                        ReasoningTools(add_instructions=True)
                    ],
                    markdown=True,
                    show_tool_calls=True
                )

                st.markdown("### 🔎 Evaluation in Progress...")
                with st.spinner("Running detailed analysis on candidates..."):
                    query = f"Evaluate GitHub candidates for the role '{job_role}': {', '.join(usernames)}"
                    stream = agent.run(query, stream=True)

                    output = ""
                    block = st.empty()
                    for chunk in stream:
                        if hasattr(chunk, "content") and isinstance(chunk.content, str):
                            output += chunk.content
                            block.markdown(output, unsafe_allow_html=True)

# Page 2: Single Candidate Analyzer
elif page == "Single Candidate Analyzer":
    st.header("Candilyzer - Single Candidate Profile Analyzer")
    st.markdown(
        """
        Analyze a single candidate’s GitHub and optional LinkedIn profile for a specific job role.
        """
    )

    if not all([st.session_state.deepseek_api_key, st.session_state.github_api_key, st.session_state.exa_api_key]):
        st.info("Please enter all API keys in the sidebar.")

    with st.form("single_candidate_form"):
        col1, col2 = st.columns(2)
        with col1:
            github_username = st.text_input("GitHub Username", placeholder="e.g. Toufiq")
            linkedin_url = st.text_input("LinkedIn Profile (Optional)", placeholder="https://linkedin.com/in/...")
        with col2:
            job_role = st.text_input("Job Role", placeholder="e.g. ML Engineer")
        submit_button = st.form_submit_button("Analyze Candidate 🔥")

    if submit_button:
        if not github_username or not job_role:
            st.error("GitHub username and job role are required.")
        elif not all([st.session_state.deepseek_api_key, st.session_state.github_api_key, st.session_state.exa_api_key]):
            st.error("❌ Please enter all API keys in the sidebar.")
        else:
            try:
                agent = Agent(
                    model=DeepSeek(id="deepseek-chat", api_key=st.session_state.deepseek_api_key),
                    name="Candilyzer",
                    tools=[
                        ThinkingTools(add_instructions=True),
                        GithubTools(access_token=st.session_state.github_api_key),
                        ExaTools(
                            api_key=st.session_state.exa_api_key,
                            include_domains=["linkedin.com", "github.com"],
                            type="keyword",
                            text_length_limit=2000,
                            show_results=True
                        ),
                        ReasoningTools(add_instructions=True)
                    ],
                    description=description_single,
                    instructions=instructions_single,
                    markdown=True,
                    show_tool_calls=True,
                    add_datetime_to_instructions=True
                )

                st.markdown("### 🤖 AI Evaluation in Progress...")
                with st.spinner("Analyzing... please wait."):
                    input_text = f"GitHub: {github_username}, Role: {job_role}"
                    if linkedin_url:
                        input_text += f", LinkedIn: {linkedin_url}"

                    response_stream = agent.run(
                        f"Analyze candidate for {job_role}. {input_text}. Provide score and detailed report give final combine and in detailed",
                        stream=True
                    )

                    full_response = ""
                    placeholder = st.empty()
                    for chunk in response_stream:
                        if hasattr(chunk, "content") and isinstance(chunk.content, str):
                            full_response += chunk.content
                            placeholder.markdown(full_response, unsafe_allow_html=True)

                    # Extract Score from response (e.g., "85/100")
                    score = 0
                    match = re.search(r"(\d{1,3})/100", full_response)
                    if match:
                        score = int(match.group(1))
                        st.success(f"Candidate Score: {score}/100")

            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")

            st.markdown(
                "For more information on how to use this tool, visit the [documentation](https://github.com/Toufiqqureshi/Candilyzer)."
            )
