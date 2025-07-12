## Overview of the idea

ChessMates AutoAgent is an AI-powered automation agent designed to enhance the ChessMates platform by generating and publishing high-quality chess-related content daily. The agent autonomously creates engaging chess puzzles and shares trending news from the chess world, keeping the community informed and engaged without manual intervention.

## Explanation of how it works

News Generation Workflow

1. Fetching Context
	•	The AgnoAgent class initiates the get_news() function.
	•	This function first queries the database to retrieve the latest 3 news items, forming the base context for potential follow-ups.

2. Agent-Driven News Creation
	•	An Agno-powered agent using A Gemini model evaluates whether to:
	•	Generate a follow-up to one of the existing news items (creating continuity and narrative depth), or
	•	Write a completely new news story based on live data.
	•	The agent uses tools such as DuckDuckGoTool: To search for relevant URLs and headlines.
	•	NewsPaper4kTool: To scrape and extract structured article data like headline, body, and source.

3. Database Update
	•	If a follow-up is generated:
	•	The agent appends it to the referenced news item’s thread.
	•	If a new headline is created:
	•	The oldest of the 3 existing news stories is removed and replaced with the new one.

4. Multilingual Translation
	•	The new or updated news item is passed to the Sarvam.ai API.
	•	The API translates the content into multiple supported languages (configured to hi-IN for now, but can ask for other supported languages as well ).

5. API Exposure
	•	The FastAPI backend exposes a GET /news endpoint that responds with this news data along with the translations.

⸻

Puzzle Generation Workflow

1. Puzzle Generation Agent
	•	An Agno-powered agent coordinates the process using:
	•	A Genetic Algorithm, seeded with a population of 20 chess positions.
	•	The system evaluates and evolves puzzle candidates over 15 iterations using:
	•	Stockfish: To assess move quality and difficulty. It also uses a set of starting positions that are better suited to find a puzzle leading to a checkmate position.

2. API Exposure
	•	The best puzzle is saved to the database.
	•	The FastAPI backend exposes a GET /puzzles endpoint that responds with this puzzle data, which contains a FEN sequence that can be converted to an interactive chess board.

⸻

Automation via Cron Jobs

- A Node.js cron job using node-cron schedules regular execution of two sequences:
- Fetching news data using /news endpoint and posting it to the /create-news endpoint of the ChessMates website where the news is shown in a clean, structured feed. It can be scheduled to happen 3 times a day, it is configured to repeat every 1 minutes for now, for demo purposes.
- Fetching puzzle data using /puzzle endpoint and posting it to the /create-puzzle endpoint of the ChessMates website where the puzzle is shown and can be interacted with. It can be scheduled to happen once a day, it is configured to repeat every 2 minutes for now, for demo purposes.

## Technologies/tools used

**Agno** for agent orchestration.
**Python/FastAPI** for backend processing.
**Stockfish** for puzzle generation.
**DuckDuckGo & NewsPaper4kTools** for scraping and extracting structured news data from websites.
**Sarvam.ai API** to translate into multiple languages.
**Cron Job using node-cron** for scheduling generation of new puzzles and news regularly.

## All setup instructions (API keys, signups, etc.)

- refer to the .env_example file and create a .env file with appropriate API keys:

GEMINI_API_KEY (your gemini api key)
SARVAM_API_KEY (you sarvam ai api key)
DB_USER (your postgresql db user)
DB_PASSWORD (your postgresql db password)
DB_HOST (your postgresql db host name)
DB_PORT (your postgresql db port number)
DB_NAME (your postgresql db name)

FETCH_NEWS_API_URL=http://127.0.0.1:8000/news
FETCH_PUZZLE_API_URL=http://127.0.0.1:8000/puzzle
POST_NEWS_API_URL=https://chessmates-pr.vercel.app/api/create-news
POST_PUZZLE_API_URL=https://chessmates-pr.vercel.app/api/create-puzzle

- Make sure you have python version 3.11 along with postgres and pgadmin up and running 
- The default stockfish engine is for mac os, the windows and linux ones are already installed in the [stockfish directory](stockfish). Rename the required engine to stockfish and rename the others to something else, so as to not clash names

- setup a virtual environment :
``` python -m venv myenv ```

- activate the virtual environment:
``` source myenv/bin/activate ```

- install requirements:
``` pip install -r requirements.txt ```

- start the fastapi server:
``` uvicorn main:app --reload ```

- in a new terminal outside the environment, install packages and start the cron jobs:
``` npm install ```
``` npm run start ```



