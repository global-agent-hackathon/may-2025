# Project Title
**BrandView AI – YouTube Influencer Intelligence Agent**

## Overview of the Idea
BrandView AI is a smart agent built with **Agno** that helps brands evaluate YouTube creators for influencer marketing. It analyzes channels and videos to help marketers find safe, high-performing influencers, faster and more accurately than doing manual research.

## Project Goal
To build an intelligent agent that allows brands to instantly:
1. Understand a creator's audience and past performance  
2. Assess risk and sentiment around their content  
3. Analyze how they handle sponsorships  
4. Estimate ROI and CPM based on past metrics  
5. Discover and evaluate new talent by crawling talent agency websites  

## How It Works
Marketers interact with BrandView AI using simple chat prompts. Behind the scenes, the system (a coordinated team of specialized sub-agents) fetches YouTube data, processes it using Python-based tools, and delivers clear, actionable results. For complex calculations, a dedicated Python coder agent writes and executes code on the fly.

Each request can trigger a workflow involving:
- Resolving channel identifiers  
- Collecting channel and video data  
- Transcribing video audio to text  
- Analyzing video content for sponsor segments  
- Conducting risk and sentiment analysis  
- Running Python scripts for metric calculations  
- Crawling influencer talent agency websites to discover new collaborators  

All of this happens transparently within a single conversational interface.

### Example User Journeys:

🧠 User: "Find the top 5 German influencers that are managed by the agency co-mng.de. Make sure they have a YouTube channel."  
💬 Agent:  
- Uses the Talent Specialist agent to crawl co-mng.de website and extract talent information
- Filters for German influencers with YouTube channels
- Ranks them based on their YouTube metrics using the Channel Data Collector
- Response: "_Found 5 German influencers managed by co-mng.de. Here are their channels ranked by subscriber count and engagement metrics..._"

🧠 User: "What would be the price that I should pay CashJordan to keep the CPM under 35€? Fetch the views for the last 20 videos and use the median for the estimation."  
💬 Agent:  
- Channel ID Resolver finds CashJordan's official channel ID
- Video Statistics Specialist fetches the last 20 videos' statistics
- Python Script Executor calculates the median views
- Metrics Calculator determines the maximum price to maintain CPM under 35€
- Response: "_Based on the median views of 450K from the last 20 videos, you should pay no more than €15,750 to maintain a CPM under 35€._"

🧠 User: "Find 3 biggest YouTube influencers in India focused on tech content. Present the channels in the table with columns: Channel name and URL, Followers, Average Views, Average Likes, Average comments. Leave a link to the report document."  
💬 Agent:  
- Channel Search Specialist searches for Indian tech YouTube channels
- Channel Data Collector gathers detailed metrics for each channel
- Python Script Executor calculates averages for views, likes, and comments
- Document Generator creates a formatted report with the table
- Response: "_Here are the top 3 Indian tech influencers with their metrics. View the detailed report here: [Report Link]_"

## How It All Happens Behind the Scenes

- Individual specialized sub-agents (e.g., Channel ID Resolver, Channel Data Collector, Video Analysis Specialist, Risk & Sentiment Analyzer, Document Generator, Python Script Executor, Metrics Calculator, Video Statistics Specialist, Talent Specialist) coordinate under a central team orchestration to handle each task in parallel when needed.
- The Python coder agent (Python Script Executor) writes and runs code for any metric calculations or report generation.
- Firecrawl is used strictly to crawl influencer management agency websites for talent discovery—not for scraping scandal or controversy content.
- Video audio is transcribed on demand (audio→text) for deeper analysis of transcripts.
- Video content analysis (scene parsing and sponsor detection) is performed via the `analyze_video_content` tool.
- Risk and sentiment insights are drawn from comments and online searches using the `sentiment_score` tool and web search tools.  

### Agents in the Codebase
- **Channel ID Resolver**: Resolves various YouTube channel identifiers to official channel IDs.  
- **Channel Data Collector**: Gathers channel information, recent videos, and overall channel statistics.  
- **Video Analysis Specialist**: Retrieves video metadata, fetches comments, transcribes audio, and finds sponsor segments.  
- **Channel Search Specialist**: Discovers YouTube channels based on search queries.  
- **Risk & Sentiment Analyzer**: Evaluates brand-safety risks and sentiment from comments and online sources.  
- **Document Generator**: Creates structured documents and reports from analyzed data.
- **Python Script Executor**: Writes and executes Python scripts for calculations and data processing, including generating graphs using matplotlib.
- **Metrics Calculator**: Calculates influencer marketing metrics (CPM, CPV, CPA, engagement rate) using real data provided by the Python Script Executor.
- **Video Statistics Specialist**: Analyzes engagement statistics (views, likes, comments) for recent videos.  
- **Talent Specialist**: Crawls influencer talent agency websites to extract talent profiles for collaborations.

## Core Functionality
- **Channel Health Snapshot**  
  - Growth and engagement metrics (views, subscribers)  
  - Aggregate sentiment from recent comments  
- **Brand-Safety & Sentiment Analysis**  
  - Risk scan (flag profanity, controversial topics)  
  - Aggregate sentiment scoring for videos and comments  
- **Sponsor Segment Locator**  
  - Identify sponsor mentions and timestamps in videos  
  - Highlight retention drop-off around sponsored segments  
- **ROI & CPM Estimator**  
  - Calculate CPM, CPV, and CPA based on historical data using Python scripts  
  - Answer "What CPM do we hit if we pay $X?"  
- **Competitive Benchmarking**  
  - Compare two or more channels on views, engagement, and brand-safety metrics  
- **Talent Discovery & Analysis**  
  - Crawl influencer agency websites to find new talent  
  - Extract basic info: name, social links, niche, and any available stats  

## Multimodal Elements
- **Text**: Chat interface, transcripts, and analysis summaries  
- **Audio→Text**: Transcription of video audio when requested  
- **Video Analysis**: Scene parsing and sponsor detection via `analyze_video_content`  

## Tools Used
| **Purpose**                  | **Tool / Library**                                                                                           |
|------------------------------|---------------------------------------------------------------------------------------------------------------|
| Agent Orchestration          | <img src="https://cdn.prod.website-files.com/6796d350b8c706e4533e7e32/6796d350b8c706e4533e8019_Favicon%20small.png" height="16" style="vertical-align:middle;"> **Agno** |
| Backend & API                | **Python**, **FastAPI**                                                                                       |
| Chat LLM                     | **OpenAI GPT-4.1-mini**                                                                                       |
| Data Ingestion               | **YouTube Data API**, **yt-dlp**, <img src="https://firecrawl.dev/favicon.ico" height="16" style="vertical-align:middle;"> **Firecrawl** (crawl talent agency websites) |
| Audio to Text                | **video_to_text (OpenAI Whisper)**                                                                                             |
| Video Analysis               | **analyze_video_content**                                                                                     |
| Sentiment Analysis           | **sentiment_score**                                                                                           |
| Python Execution & Reporting | **PythonTools** (via Python Script Executor agent)                                                             |
| Frontend (Demo)              | **Streamlit**                                                                                                 |
| Memory Layer                 | <img src="https://mem0.ai/favicon.ico" height="16" style="vertical-align:middle;"> **Mem0** (store short-term chat session memory) |

## UI Approach
- **Primary Interface**: Streamlit web app where users can start multiple chat sessions to interact with BrandView AI.  
- **Secondary Interface**: WhatsApp integration for on-the-go influencer queries via the Twilio webhook.

## Visuals

- 👉 [Download all Visuals (ZIP) including Agent Architecture and Workflow Chart](images/visuals.zip)

## Demo Video Link
[Watch the Demo](https://www.loom.com/share/5510b1e2420a4f839ca107a3899350ec?sid=660cdbee-e59b-46b5-9e83-91c84ddc98b7)

## How to Use the App

Follow these steps to get BrandView AI up and running locally:

1. **Clone the GitHub repository**  
   Open a terminal and run:
   ```bash
   git clone https://github.com/mmestrov2000/BrandView-AI.git
   cd BrandView-AI
   ```

2. **Install dependencies**  
   Ensure you have Python 3.8+ and pip installed, then run:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Obtain API keys**  
   You will need to sign up for the following services and obtain their API keys:

   - **YouTube API**: Get your API key from [Google Cloud Console](https://console.cloud.google.com/) (YouTube Data API v3)
   - **OpenAI API**: Get your API key from [OpenAI Platform](https://platform.openai.com/docs/overview)
   - **FireCrawl API**: Sign up at [FireCrawl](https://www.firecrawl.dev/app)
   - **AWS S3**: Create an account on [AWS](https://aws.amazon.com/) and follow the [S3 Getting Started Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/GetStartedWithS3.html)
   - **Tavily API**: Get your API key from [Tavily](https://www.tavily.com/)
   - **Mem0 API**: Get your API key from [Mem0 Dashboard](https://app.mem0.ai/dashboard/)

4. **Configure Environment Variables**
   Create a `.env` file in the project's root directory with the following variables:
   ```
   YOUTUBE_API_KEY=<your_youtube_api_key>
   OPENAI_API_KEY=<your_openai_api_key>
   FIRECRAWL_API_KEY=<your_firecrawl_api_key>
   AWS_ACCESS_KEY_ID=<your_aws_access_key_id>
   AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key>
   S3_BUCKET_NAME=<your_s3_bucket_name>
   AWS_REGION=<your_aws_region>
   TAVILY_API_KEY=<your_tavily_api_key>
   MEM0_API_KEY=<your_mem0_api_key>
   ```
   Replace each `<...>` placeholder with the actual key/value you obtained in step 3.

5. **Run the Streamlit app**  
   From the project root, execute:
   ```bash
   streamlit run app.py
   ```
   This will launch the local web UI. Open the URL shown in your terminal (typically `http://localhost:8501`) in your browser to start interacting with BrandView AI.

## Team Information
- **Team Lead**: @mmestrov2000
- **Team Members**: @Abhishek637Saraswat, @LukaMestrovic
- **Background/Experience**: Marin Mestrovic has a Bachelor's degree in Mathematics with strong skills in algorithms, data science, and machine learning. Abhishek Saraswat is a B.Tech student in Electronics Engineering with experience in AI, machine learning, backend development, and projects in stock analysis and speech recognition. Luka Mestrovic has a background in physics, statistics, and mathematics, combined with industry-specific insights in influencer marketing.

## Prize Category (leave blank, to be assigned by judges)
- [ ] Best use of Agno
- [ ] Best use of Firecrawl
- [ ] Best use of Mem0
- [ ] Best use of Graphlit
- [ ] Best use of Browser Use
- [ ] Best Overall Project

## Additional Notes
- **Agent Collaboration**: Although BrandView AI appears as a single chat agent, it is powered by a coordinated team of specialized sub-agents, each with its own focus (data collection, analysis, Python scripting, talent discovery).  
- **Python-Driven Calculations**: Any complex metric calculation or report generation is handled by the Python Script Executor agent, ensuring accuracy and reproducibility.  
- **Firecrawl Usage**: Firecrawl is used exclusively to crawl official influencer agency websites for talent information—not for controversy scraping.  
- **Streamlit & WhatsApp Integration**: The Streamlit interface serves as the primary demo platform, while the WhatsApp integration allows users to query the agent from their mobile devices.  
- **Extensibility**: The modular architecture makes it straightforward to add new platforms (e.g., TikTok, Twitch) or additional analysis tools in the future.
