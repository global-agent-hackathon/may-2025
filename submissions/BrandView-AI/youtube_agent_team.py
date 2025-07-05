from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from src.tools.youtube_api import (
    resolve_channel_id,
    search_youtube_channel_videos,
    fetch_channel_info,
    fetch_videos,
    fetch_video_statistics,
    introspect_channel,
    fetch_video_details,
    fetch_comments,
    search_youtube_channels
)
from src.tools.document_output import Document_Output
from src.tools.video_analysis import video_to_text, analyze_video_content
from src.tools.talents import crawl_talent_agency
from agno.tools.python import PythonTools
from agno.tools.tavily import TavilyTools
from pathlib import Path

from src.tools.risk import sentiment_score

from dotenv import load_dotenv
load_dotenv()


# Create individual specialized agents

# Agent 1: Channel ID Resolver
channel_resolver = Agent(
    name="channel_resolver",
    role="Resolves YouTube channel identifiers to their official channel IDs",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[resolve_channel_id],
    instructions=[
        "You are responsible for resolving YouTube channel identifiers to their official channel IDs.",
        "Handle various input formats including channel handles, custom URLs, and direct channel IDs.",
        "Return the resolved channel ID in a clear format."
    ],
    markdown=True
)

# Agent 2: Channel Data Collector
channel_collector = Agent(
    name="channel_collector",
    role="Collects comprehensive data about YouTube channels",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[
        resolve_channel_id,
        search_youtube_channel_videos,
        fetch_channel_info,
        fetch_videos,
        introspect_channel
    ],
    instructions=[
        "You are responsible for collecting comprehensive data about YouTube channels.",
        "You can search for videos within channels, fetch channel information, and get recent videos.",
        "Use the introspect_channel tool for a complete channel analysis.",
        "Present the data in a well-organized, readable format."
    ],
    markdown=True
)

# Agent 3: Video Analysis Specialist
video_analysis_specialist = Agent(
    name="video_analysis_specialist",
    role="Comprehensive video analysis including metadata, comments, transcription, and content analysis",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[
        fetch_video_details,
        fetch_comments,
        video_to_text,
        analyze_video_content
    ],
    instructions=[
        "You are a comprehensive video analysis specialist responsible for all aspects of video analysis.",
        "You can perform the following analyses when given a video ID:",
        "1. Fetch video metadata and details using fetch_video_details",
        "2. Collect and analyze comments using fetch_comments",
        "3. Transcribe video content using video_to_text",
        "4. Analyze video content for scenes, sponsors, and visual elements using analyze_video_content",
        "When analyzing video content:",
        "1. Process the raw tool output and present it in a clear, readable format",
        "2. For sponsor detection, clearly indicate when and where sponsors appear in the video",
        "3. Format timestamps in minutes:seconds format for better readability",
        "4. Group consecutive scenes with the same sponsor together",
        "5. Provide a clear summary of findings at the end",
        "6. If asked about specific timestamps or sponsor mentions, highlight those details prominently",
        "Present all data in a structured, easy-to-read format using markdown."
    ],
    expected_output="""Present your analysis in a clear markdown format with:
        1. Video metadata and basic information
        2. Comment analysis and insights
        3. Video transcription (when requested)
        4. Content analysis including sponsor mentions and timestamps
        5. A comprehensive summary of findings""",
    show_tool_calls=True,
    markdown=True
)

# Agent 4: Channel Search Specialist
channel_searcher = Agent(
    name="channel_searcher",
    role="Searches and discovers YouTube channels using both YouTube and web search",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[search_youtube_channels],
    instructions=[
        "You are responsible for comprehensive channel discovery using both YouTube and web search.",
        "For YouTube channel search:",
        "1. Use the search_youtube_channels tool to find relevant channels based on queries",
        "2. Present YouTube search results in a clear, organized manner",
        "3. Focus on finding the most relevant channels for given topics",
        "Provide:",
        "1. A comprehensive list of relevant channels",
        "2. Context about why each channel is relevant",
        "4. Clear organization of results by source and relevance",
        "For query for the tool search_youtube_channels, always use the short term that a person would realistically search on youtube to find relevant video on this topic. For example, if the topic is 'AI sales automation', then the query should be 'AI sales automation'."
    ],
    expected_output="""Present your findings in a clear markdown format with:
        1. YouTube Search Results
           - List of channels found through YouTube search
           - Basic channel information
           - Relevance to search query
        2. Web Search Results
           - Channels discovered through web search
           - Additional context and insights
           - Source credibility
        3. Combined Analysis
           - Cross-referenced results
           - Overall recommendations
           - Most promising channels""",
    show_tool_calls=True,
    markdown=True
)

# Agent 5: Risk and Sentiment Analysis Specialist
risk_sentiment_analyzer = Agent(
    name="risk_sentiment_analyzer",
    role="Analyzes both potential risks and sentiment for YouTube channels, videos, and comments",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[TavilyTools(), sentiment_score],
    instructions=[
        "You are a comprehensive risk and sentiment analysis specialist responsible for evaluating both brand safety and sentiment.",
        "For risk analysis:",
        "1. Use Tavily to search web for at least 3 different topics with keywords like scandal, controversy, cancelled, etc.",
        "2. Summarize all results together and determine the probability that these controversies are related to the specific influencer.",
        "3. Keep in mind that most influencers should be safe, and keywords like these will always lead to controversies - verify relevance carefully.",
        "For sentiment analysis:",
        "1. Use sentiment_score tool to analyze the sentiment of provided text (comments, video descriptions, etc.)",
        "2. Provide both individual and aggregate sentiment scores when analyzing multiple items",
        "3. Consider context when interpreting sentiment scores",
        "At the end of your analysis, return a JSON object with:",
        "1. risk_score: A numerical assessment of the overall risk level (0-1)",
        "2. confidence_score: How confident you are in your risk assessment (0-1)",
        "3. sentiment_score: The sentiment score for the analyzed content",
        "4. brief_analysis: A concise summary of your findings and reasoning",
        "5. verification_notes: How you verified the relevance of findings to this specific influencer"
    ],
    expected_output="""Present your analysis in a clear markdown format with the following sections:
        1. Risk Assessment
           - Risk Score (0-1) & one-liner explanation
           - Confidence Score (0-1) & one-liner explanation
           - Brief Analysis
           - Verification Notes
        2. Sentiment Analysis
           - Individual/Group Sentiment Scores
           - Context and Interpretation
        3. Overall Assessment
           - Combined Risk and Sentiment Insights
           - Recommendations""",
    show_tool_calls=True,
    markdown=True
)

# Agent 6: Document Generator
document_generator = Agent(
    name="document_generator",
    role="Generates structured documents and reports from data.",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[Document_Output],
    instructions=[
        "1. Use Document_Output tool to create all reports and documents",
        "2. Format content with clear sections and bullet points",
        "3. Include any provided graphs or visualizations in the document",
        "4. Return the document URL to the user",
        "5. Never use Python scripts for document generation"
    ],
    show_tool_calls=True,
    markdown=True
)

# Agent 7: Python Script Executor
python_script_executor = Agent(
    name="python_script_executor",
    role="Executes Python scripts for calculations.",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[PythonTools(base_dir=Path("tmp/python"))],
    instructions=[
        "1. Use PythonTools to write and execute Python scripts for any calculations",
        "2. Use real data from other agents for calculations",
        "3. Never generate reports or documents nor fetch new data - refuse similar tasks."
    ],
    show_tool_calls=True,
    markdown=True
)

# Agent 8: Metrics Calculator
metrics_calculator = Agent(
    name="metrics_calculator",
    role="Calculates influencer marketing metrics using real data provided.",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[PythonTools(base_dir=Path("tmp/python"))],
    instructions=[
        "Receive real data outputs (views, likes, comments, etc.) from Python Script Executor agent.",
        "Calculate CPM, CPV, CPA, engagement rate, and other influencer marketing metrics.",
        "Use the median rather than mean when estimating values like expected views.",
        "For the views estimation, use strictly the MEDIAN because we're always estimating.",
        "Do not generate or simulate synthetic data; only work with provided data.",
        "Always return a structured JSON with each metric."
    ],
    show_tool_calls=False,
    markdown=False
)

# Agent 9: Video Statistics Specialist
video_statistics_specialist = Agent(
    name="video_statistics_specialist",
    role="Analyzes engagement statistics for recent videos on a YouTube channel",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[PythonTools(base_dir=Path("tmp/python")), resolve_channel_id, fetch_video_statistics],
    instructions=[
        "You are a video statistics specialist focused on analyzing engagement metrics.",
        "First resolve the channel identifier to get the official channel ID.",
        "Then fetch statistics for recent videos including views, likes, comments, and favorites.",
        "If you need to do any calculations, use the python tools for it.",
        "Present the statistics in a clear, tabular format.",
        "Focus on providing insights about video performance and engagement patterns."
    ],
    show_tool_calls=True,
    markdown=True
)

# Agent 10: Talent Specialist
talent_specialist = Agent(
    name="talent_specialist",
    role="Discovers and analyzes talents from talent agency websites",
    model=OpenAIChat(id="gpt-4.1-mini"),
    tools=[TavilyTools(), crawl_talent_agency],
    instructions=[
        "You are a talent specialist responsible for discovering and analyzing talents from talent agency websites.",
        "Your workflow should be:",
        "1. Use Tavily search to find relevant talent agency websites based on the search criteria",
        "2. For each found agency website, use crawl_talent_agency to extract talent information",
        "3. Present the findings in a clear, organized format",
        "When searching for agencies:",
        "- Use specific search terms like 'influencer talent agency [location/niche]'",
        "- Focus on finding official agency websites",
        "- Look for agencies that match the given criteria",
        "When analyzing talents:",
        "- Extract basic information (name, social links, bio)",
        "- Note their main categories/niches",
        "- Include any available statistics"
    ],
    expected_output="""Present your findings in a clear markdown format with:
        1. Found Agencies
           - List of relevant talent agencies with their websites
           - Brief description of each agency's focus
        2. Talent Analysis
           - For each agency, list their talents with:
             * Name and social links
             * Brief bio
             * Main categories
             * Key statistics (if available)
        3. Summary
           - Total number of agencies and talents found
           - Most common talent categories
           - Notable talents worth highlighting""",
    show_tool_calls=True,
    markdown=True
)

# Create the YouTube analysis team
youtube_team = Team(
    name="YouTube Analysis Team",
    mode="coordinate",  # Using coordinate mode to delegate tasks and synthesize responses
    model=OpenAIChat(id="gpt-4.1-mini"),
    members=[
        channel_resolver,
        channel_collector,
        video_analysis_specialist,
        channel_searcher,
        risk_sentiment_analyzer,
        document_generator,
        python_script_executor,
        metrics_calculator,
        video_statistics_specialist,
        talent_specialist
    ],
    show_tool_calls=True,
    markdown=True,
    description="A team of specialized agents for comprehensive YouTube data analysis",
    instructions=[
        "You are a team of specialized YouTube data collection agents.",
        "Coordinate between different agents to provide comprehensive YouTube data analysis.",
        "Use the appropriate agent for each specific task.",
        "Ensure proper coordination between agents when tasks require multiple steps.",
        "Make sure to give tasks to the agents in their scope in a way that they can understand and execute it.",
        "Maintain context between different analysis steps. Use strictly the tool set_shared_context after each agent to set the context for the next agent.",
        "Use strictly the tool transfer_task_to_member to transfer the task to the appropriate agent.",
        "Consider the chat history provided in the memory context when responding to maintain conversation continuity.",
        "To generate a report or document, use the document_generator agent.",
        "For data processing and calculations, use the python_script_executor agent - but only after data has been gathered by other agents.",
        "Remember that the python_script_executor agent should never be used to fetch or gather new data - it only processes existing data."
    ],
    expected_output="Present all data in a clear, organized format using markdown.",
    show_members_responses=True,
    enable_agentic_context=True,
    add_context=True  # Enable context addition for memory
)